"""Subprocess protocol tests for the mock MCP provider; Python standard library only."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import platform
from queue import Empty, Queue
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "mock_mcp_server.py"
META_KEY = "engineering-process-provider"
APPLICATION = "urn:engineering-process-spec:mock-engineering"
VERSION = "0.1.0-draft.1"
VOLUME_ARGS = {
    "length": {"value": 100, "unit": "mm"},
    "width": {"value": 80, "unit": "mm"},
    "thickness": {"value": 2.5, "unit": "mm"},
}
MASS_ARGS = {"volume": {"quantity": "volume", "value": 0.00002, "unit": "m3"}, "density": {"value": 7850, "unit": "kg/m3"}}
MEASUREMENT = {"quantity": "mass", "value": 0.157, "unit": "kg"}


class Session:
    """Tiny test driver: actual newline-delimited stdio, no server/adapter imports."""

    def __init__(self, arguments: list[str], audit: Path, initialize: bool = True):
        self.audit_path = audit
        self.responses: Queue = Queue()
        self.next_id = 0
        self.transcript: list[dict] = []
        self.process = subprocess.Popen(
            [sys.executable, "-u", str(SERVER), "--audit", str(audit), *arguments],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        self.reader = Thread(target=self._read, daemon=True)
        self.reader.start()
        self.initialize_response = self.initialize() if initialize else None

    def _read(self) -> None:
        try:
            for line in self.process.stdout:
                self.responses.put(line)
        finally:
            self.responses.put(None)

    def send(self, value: dict) -> None:
        self.send_raw(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")))

    def send_raw(self, value: str) -> None:
        self.process.stdin.write(value + "\n")
        self.process.stdin.flush()

    def receive(self) -> dict:
        try:
            line = self.responses.get(timeout=5)
        except Empty as error:
            raise AssertionError("No protocol response within five seconds") from error
        if line is None:
            raise EOFError("Mock closed stdio without a response")
        value = json.loads(line, parse_constant=lambda literal: (_ for _ in ()).throw(AssertionError(f"Non-finite wire value: {literal}")))
        if not isinstance(value, dict) or value.get("jsonrpc") != "2.0":
            raise AssertionError(f"Non-protocol stdout: {line!r}")
        self.transcript.append(value)
        return value

    def request(self, method: str, params: dict | None = None) -> dict:
        self.next_id += 1
        request = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        if params is not None:
            request["params"] = params
        self.send(request)
        response = self.receive()
        if response.get("id") != self.next_id:
            raise AssertionError(f"Response has wrong request ID: {response}")
        return response

    def notify(self, method: str, params: dict | None = None) -> None:
        message = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        self.send(message)

    def initialize(self, version: str = "2025-11-25", notify: bool = True) -> dict:
        response = self.request("initialize", {"protocolVersion": version, "capabilities": {}, "clientInfo": {"name": "mock-protocol-test", "version": VERSION}})
        if notify:
            self.notify("notifications/initialized")
        return response

    def call(self, name: str, arguments: dict) -> dict:
        return self.request("tools/call", {"name": name, "arguments": arguments})

    def events(self, event: str | None = None) -> list[dict]:
        if not self.audit_path.exists():
            return []
        values = [json.loads(line) for line in self.audit_path.read_text(encoding="utf-8").splitlines()]
        return values if event is None else [value for value in values if value["event"] == event]

    def close(self) -> str:
        try:
            if not self.process.stdin.closed:
                self.process.stdin.close()
        except BrokenPipeError:
            pass
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        self.reader.join(timeout=1)
        stderr = self.process.stderr.read()
        self.process.stderr.close()
        self.process.stdout.close()
        return stderr


class MockProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="engineering-process-mock-")
        self.sessions: list[Session] = []

    def tearDown(self) -> None:
        diagnostics = []
        for session in self.sessions:
            diagnostics.append(session.close())
        self.temporary.cleanup()
        self.assertEqual(diagnostics, [""] * len(diagnostics), "Unexpected mock stderr")

    def session(self, *arguments: str, initialize: bool = True) -> Session:
        session = Session(list(arguments), Path(self.temporary.name) / f"audit-{len(self.sessions)}.jsonl", initialize)
        self.sessions.append(session)
        return session

    def tool_result(self, response: dict) -> dict:
        self.assertNotIn("error", response)
        result = response["result"]
        self.assertFalse(result["isError"])
        self.assertEqual(json.loads(result["content"][0]["text"]), result["structuredContent"])
        return result["structuredContent"]

    def test_initialize_and_discovery_match_reviewed_contract(self) -> None:
        session = self.session()
        init = session.initialize_response["result"]
        self.assertEqual(init["protocolVersion"], "2025-11-25")
        self.assertEqual(init["serverInfo"], {"name": "engineering-process-mock", "version": VERSION})
        self.assertEqual(set(init["capabilities"]), {"tools", "resources"})
        expected_provider = {"implementation": "urn:engineering-process-spec:mock-mcp", "revision": VERSION, "application": APPLICATION, "applicationVersion": VERSION, "executionPlatform": sys.platform}
        self.assertEqual(init["_meta"], {META_KEY: expected_provider})
        listing = session.request("tools/list")["result"]
        self.assertEqual(listing["_meta"], init["_meta"])
        self.assertEqual([tool["name"] for tool in listing["tools"]], ["engineering.volume", "engineering.mass", "engineering.record"])
        for tool in listing["tools"]:
            expected = json.loads((ROOT / "snapshots" / f"{tool['name']}.tool.json").read_text(encoding="utf-8"))
            self.assertEqual(tool, expected)
            for suffix, field in (("input", "inputSchema"), ("output", "outputSchema")):
                snapshot = json.loads((ROOT / "snapshots" / f"{tool['name']}.{suffix}.json").read_text(encoding="utf-8"))
                self.assertEqual(tool[field], snapshot)
                self.assertEqual(snapshot["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(session.events("tool_call"), [])

    def test_initialization_and_initialized_notification_gate_operations(self) -> None:
        session = self.session(initialize=False)
        self.assertEqual(session.request("tools/list")["error"]["code"], -32600)
        self.assertEqual(session.request("ping")["result"], {})
        self.assertIn("result", session.initialize(notify=False))
        self.assertEqual(session.request("tools/list")["error"]["code"], -32600)
        session.notify("notifications/initialized")
        self.assertIn("tools", session.request("tools/list")["result"])
        self.assertEqual(session.initialize()["error"]["code"], -32600)
        self.assertEqual(session.events("tool_call"), [])

    def test_protocol_negotiation_returns_supported_version(self) -> None:
        session = self.session(initialize=False)
        response = session.initialize("2099-01-01", notify=False)
        self.assertEqual(response["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(session.events("tool_call"), [])

    def test_unknown_notification_has_no_response_and_ping_preserves_unicode_id(self) -> None:
        session = self.session()
        session.notify("notifications/not-implemented", {"text": "ignored\nnotification"})
        session.send({"jsonrpc": "2.0", "id": "request-μ", "method": "ping"})
        self.assertEqual(session.receive(), {"jsonrpc": "2.0", "id": "request-μ", "result": {}})

    def test_deterministic_calculation_hands_volume_to_mass(self) -> None:
        session = self.session()
        volume = self.tool_result(session.call("engineering.volume", VOLUME_ARGS))
        self.assertEqual(volume, {"quantity": "volume", "value": 0.00002, "unit": "m3"})
        mass = self.tool_result(session.call("engineering.mass", {"volume": volume, "density": {"value": 7850, "unit": "kg/m3"}}))
        self.assertEqual(mass, {"quantity": "mass", "value": 0.157, "unit": "kg"})
        self.assertEqual([event["name"] for event in session.events("tool_call")], ["engineering.volume", "engineering.mass"])
        self.assertEqual(session.events("mutation"), [])

    def test_declared_equivalent_units_have_same_result(self) -> None:
        session = self.session()
        volume = self.tool_result(session.call("engineering.volume", {
            "length": {"value": 0.1, "unit": "m"}, "width": {"value": 0.08, "unit": "m"}, "thickness": {"value": 0.0025, "unit": "m"},
        }))
        mass = self.tool_result(session.call("engineering.mass", {"volume": {"value": 20000, "unit": "mm3"}, "density": {"value": 7.85, "unit": "g/cm3"}}))
        self.assertEqual(volume["value"], 0.00002)
        self.assertEqual(mass["value"], 0.157)

    def test_tool_validation_returns_iserror_and_prevents_mutation(self) -> None:
        session = self.session()
        bad_arguments = [
            {}, {**VOLUME_ARGS, "fault": "ignore-validation"},
            {**VOLUME_ARGS, "length": {"value": 100, "unit": "kg"}},
            {**VOLUME_ARGS, "length": {"value": True, "unit": "mm"}},
            {**VOLUME_ARGS, "length": {"value": 0, "unit": "mm"}},
            {**VOLUME_ARGS, "length": {"value": -1, "unit": "mm"}},
            {**VOLUME_ARGS, "length": {"quantity": "mass", "value": 1, "unit": "mm"}},
        ]
        for arguments in bad_arguments:
            with self.subTest(arguments=arguments):
                result = session.call("engineering.volume", arguments)
                self.assertNotIn("error", result)
                self.assertTrue(result["result"]["isError"])
                self.assertNotIn("structuredContent", result["result"])
        record = session.call("engineering.record", {"measurement": {"quantity": "mass", "value": 1, "unit": "mm"}})
        self.assertTrue(record["result"]["isError"])
        self.assertEqual(session.events("mutation"), [])

    def test_finite_computation_overflow_is_refused(self) -> None:
        session = self.session()
        result = session.call("engineering.volume", {key: {"value": 1e300, "unit": "m"} for key in VOLUME_ARGS})
        self.assertTrue(result["result"]["isError"])
        self.assertIn("finite", result["result"]["content"][0]["text"])

    def test_invalid_json_nonfinite_numbers_and_duplicates_never_call_tools(self) -> None:
        session = self.session()
        malformed = ["not JSON", '{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":NaN}}', '{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":Infinity}}', '{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":1e999}}', '{"jsonrpc":"2.0","id":1,"id":2,"method":"ping"}']
        for wire in malformed:
            with self.subTest(wire=wire):
                session.send_raw(wire)
                response = session.receive()
                self.assertEqual(response["error"]["code"], -32700)
                self.assertNotIn("id", response)
        self.assertEqual(session.request("ping")["result"], {})
        self.assertEqual(session.events("tool_call"), [])

    def test_invalid_envelopes_unknown_methods_and_malformed_calls_are_protocol_errors(self) -> None:
        session = self.session()
        for message in ([], {"jsonrpc": "2.0", "id": None, "method": "ping"}, {"jsonrpc": "1.0", "id": 1, "method": "ping"}):
            with self.subTest(message=message):
                session.send_raw(json.dumps(message))
                self.assertEqual(session.receive()["error"]["code"], -32600)
        self.assertEqual(session.request("not/a/method")["error"]["code"], -32601)
        self.assertEqual(session.call("missing.tool", {})["error"]["code"], -32602)
        self.assertEqual(session.request("tools/call", {"name": "engineering.volume", "arguments": []})["error"]["code"], -32602)
        self.assertEqual(session.events("tool_call"), [])

    def test_resource_read_has_stable_inputs_identity_and_revision(self) -> None:
        session = self.session()
        listing = session.request("resources/list")["result"]["resources"]
        self.assertEqual([resource["uri"] for resource in listing], ["mock://plate"])
        self.assertEqual(session.request("resources/templates/list")["result"], {"resourceTemplates": []})
        first = session.request("resources/read", {"uri": "mock://plate"})["result"]
        second = session.request("resources/read", {"uri": "mock://plate"})["result"]
        self.assertEqual(first, second)
        content = first["contents"][0]
        self.assertEqual(content["mimeType"], "application/json")
        value = json.loads(content["text"])
        self.assertEqual({key: value[key] for key in ("id", "provider", "revision")}, {"id": "mock://plate", "provider": APPLICATION, "revision": "r1"})
        self.assertEqual({key: value[key] for key in VOLUME_ARGS}, VOLUME_ARGS)
        self.assertEqual(session.events("mutation"), [])

    def test_record_mutates_session_resource_and_audit(self) -> None:
        session = self.session()
        recorded = self.tool_result(session.call("engineering.record", {"measurement": MEASUREMENT}))
        self.assertEqual(recorded, {"stored": True, "measurement": MEASUREMENT, "resource": {"id": "mock://plate", "provider": APPLICATION, "revision": "r2"}})
        readback = json.loads(session.request("resources/read", {"uri": "mock://plate"})["result"]["contents"][0]["text"])
        self.assertEqual(readback["revision"], "r2")
        self.assertEqual(readback["measurement"], MEASUREMENT)
        self.assertEqual(session.events("mutation")[0]["resource"], readback)
        again = self.tool_result(session.call("engineering.record", {"measurement": MEASUREMENT}))
        self.assertEqual(again["resource"]["revision"], "r3", "record is deliberately not idempotent")

    def test_tool_error_fault_is_distinct_from_protocol_error(self) -> None:
        for mode in ("tool-error", "rpc-error"):
            with self.subTest(mode=mode):
                session = self.session("--fault", mode, "--fault-tool", "engineering.mass")
                self.tool_result(session.call("engineering.volume", VOLUME_ARGS))
                response = session.call("engineering.mass", MASS_ARGS)
                if mode == "tool-error":
                    self.assertNotIn("error", response)
                    self.assertTrue(response["result"]["isError"])
                else:
                    self.assertNotIn("result", response)
                    self.assertEqual(response["error"]["code"], -32603)
                self.assertEqual(session.events("mutation"), [])

    def test_faults_exercise_schema_and_engineering_acceptance_independently(self) -> None:
        for mode in ("malformed-output", "wrong-unit", "wrong-value"):
            with self.subTest(mode=mode):
                session = self.session("--fault", mode, "--fault-tool", "engineering.mass")
                self.tool_result(session.call("engineering.volume", VOLUME_ARGS))
                value = self.tool_result(session.call("engineering.mass", MASS_ARGS))
                if mode == "malformed-output":
                    self.assertEqual(value, {"deliberatelyInvalid": True})
                elif mode == "wrong-unit":
                    self.assertEqual(value["unit"], "s")
                else:
                    self.assertEqual(value, {"quantity": "mass", "value": 157.0, "unit": "kg"})
                    self.assertGreater(abs(value["value"] - 0.157), 0.000001)

    def test_resource_absence_denial_and_revision_mismatch_remain_distinct(self) -> None:
        for state in ("absent", "denied", "revision-mismatch"):
            with self.subTest(state=state):
                session = self.session("--resource-state", state)
                result = session.request("resources/read", {"uri": "mock://plate"})
                if state == "revision-mismatch":
                    value = json.loads(result["result"]["contents"][0]["text"])
                    self.assertEqual(value["revision"], "r999")
                else:
                    self.assertEqual(result["error"]["code"], -32002 if state == "absent" else -32003)
                    self.assertEqual(result["error"]["data"]["reason"], state)
                self.assertEqual(session.events("tool_call"), [])

    def test_wrong_application_and_changed_default_are_observable(self) -> None:
        session = self.session("--application", "urn:engineering-process-spec:mock-other-engineering")
        init = session.initialize_response["result"]["_meta"][META_KEY]
        listed = session.request("tools/list")["result"]["_meta"][META_KEY]
        self.assertEqual(init, listed)
        self.assertNotEqual(init["application"], APPLICATION)
        changed = self.session("--fault", "changed-default")
        initial = changed.initialize_response["result"]["_meta"][META_KEY]
        discovered = changed.request("tools/list")["result"]["_meta"][META_KEY]
        self.assertEqual(initial["application"], APPLICATION)
        self.assertNotEqual(initial["application"], discovered["application"])
        self.assertEqual(changed.events("tool_call"), [])

    def test_disconnect_occurs_after_one_audited_mutation_without_response(self) -> None:
        session = self.session("--fault", "disconnect-after-mutation", "--fault-tool", "engineering.record")
        with self.assertRaises(EOFError):
            session.call("engineering.record", {"measurement": MEASUREMENT})
        self.assertEqual(len(session.events("tool_call")), 1)
        mutations = session.events("mutation")
        self.assertEqual(len(mutations), 1)
        self.assertEqual(mutations[0]["resource"]["revision"], "r2")
        self.assertEqual(mutations[0]["resource"]["measurement"], MEASUREMENT)
        self.assertEqual(len(session.events("disconnect_after_mutation")), 1)
        self.assertFalse(any("structuredContent" in response.get("result", {}) for response in session.transcript))

    def test_tool_limit_prevents_additional_mutation(self) -> None:
        session = self.session("--max-tool-calls", "1")
        self.tool_result(session.call("engineering.record", {"measurement": MEASUREMENT}))
        limited = session.call("engineering.record", {"measurement": MEASUREMENT})
        self.assertTrue(limited["result"]["isError"])
        self.assertEqual(len(session.events("mutation")), 1)

    def test_unsupported_task_augmentation_and_cursor_are_explicit_errors(self) -> None:
        session = self.session()
        self.assertEqual(session.request("tools/list", {"cursor": "invented"})["error"]["code"], -32602)
        request = {"name": "engineering.volume", "arguments": VOLUME_ARGS, "task": {"ttl": 1000}}
        self.assertEqual(session.request("tools/call", request)["error"]["code"], -32602)
        self.assertEqual(session.events("tool_call"), [])


class HTTPProcess:
    def __init__(self, arguments: list[str], audit: Path, initialize: bool = True):
        self.audit_path = audit
        self.next_id = 0
        self.session_id: str | None = None
        self.process = subprocess.Popen(
            [sys.executable, "-u", str(SERVER), "--http-port", "0", "--audit", str(audit), *arguments],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        ready: Queue = Queue()
        Thread(target=lambda: ready.put(self.process.stderr.readline()), daemon=True).start()
        try:
            line = ready.get(timeout=5)
            self.readiness = json.loads(line)
        except (Empty, ValueError) as error:
            self.process.terminate()
            self.process.wait(timeout=3)
            self.process.stdout.close()
            self.process.stderr.close()
            raise AssertionError("No valid mock HTTP readiness line") from error
        if self.readiness.get("event") != "listening":
            raise AssertionError(f"Unexpected readiness: {self.readiness}")
        parsed = urlparse(self.readiness["url"])
        self.port = parsed.port
        self.initialize_response = self.initialize() if initialize else None

    def exchange(self, method: str = "POST", message: dict | None = None, headers: dict | None = None, raw: bytes | None = None) -> tuple[int, dict, bytes]:
        selected_headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json", "MCP-Protocol-Version": "2025-11-25"}
        if self.session_id:
            selected_headers["Mcp-Session-Id"] = self.session_id
        for key, value in (headers or {}).items():
            if value is None:
                selected_headers.pop(key, None)
            else:
                selected_headers[key] = value
        body = raw if raw is not None else json.dumps(message, ensure_ascii=False, allow_nan=False).encode("utf-8") if message is not None else None
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            connection.request(method, "/mcp", body=body, headers=selected_headers)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def request(self, method: str, params: dict | None = None) -> dict:
        self.next_id += 1
        message = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        if params is not None:
            message["params"] = params
        status, headers, body = self.exchange(message=message)
        if status != 200 or headers.get("Content-Type") != "application/json":
            raise AssertionError(f"Unexpected HTTP request response: {status}, {headers}, {body}")
        if "Mcp-Session-Id" in headers:
            self.session_id = headers["Mcp-Session-Id"]
        response = json.loads(body)
        if response.get("id") != self.next_id:
            raise AssertionError(f"Wrong response ID: {response}")
        return response

    def notify(self, method: str) -> None:
        status, _, body = self.exchange(message={"jsonrpc": "2.0", "method": method})
        if status != 202 or body:
            raise AssertionError(f"Notification must return empty 202: {status}, {body}")

    def initialize(self, notify: bool = True) -> dict:
        result = self.request("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "mock-http-test", "version": VERSION}})
        if notify:
            self.notify("notifications/initialized")
        return result

    def call(self, name: str, arguments: dict) -> dict:
        return self.request("tools/call", {"name": name, "arguments": arguments})

    def events(self, event: str) -> list[dict]:
        return [value for line in self.audit_path.read_text(encoding="utf-8").splitlines() if (value := json.loads(line))["event"] == event]

    def close(self) -> tuple[str, str]:
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=3)
        stdout, stderr = self.process.stdout.read(), self.process.stderr.read()
        self.process.stdout.close()
        self.process.stderr.close()
        return stdout, stderr


class MockHTTPTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="engineering-process-http-")
        self.servers: list[HTTPProcess] = []

    def tearDown(self) -> None:
        output = [server.close() for server in self.servers]
        self.temporary.cleanup()
        self.assertEqual(output, [("", "")] * len(output), "HTTP stdout must stay empty; only readiness belongs on stderr")

    def server(self, *arguments: str, initialize: bool = True) -> HTTPProcess:
        server = HTTPProcess(list(arguments), Path(self.temporary.name) / f"http-{len(self.servers)}.jsonl", initialize)
        self.servers.append(server)
        return server

    def test_http_real_loopback_path_runs_mcp_with_declared_target_platform(self) -> None:
        server = self.server("--execution-platform", "mock-linux-target")
        self.assertTrue(server.readiness["url"].startswith("http://127.0.0.1:"))
        self.assertTrue(server.session_id)
        initialized = server.initialize_response["result"]
        listed = server.request("tools/list")["result"]
        self.assertEqual(initialized["_meta"], listed["_meta"])
        self.assertEqual(initialized["_meta"][META_KEY]["executionPlatform"], "mock-linux-target")
        self.assertEqual(server.events("tool_call"), [])
        volume = server.call("engineering.volume", VOLUME_ARGS)["result"]["structuredContent"]
        mass = server.call("engineering.mass", {"volume": volume, "density": MASS_ARGS["density"]})["result"]["structuredContent"]
        self.assertEqual(mass, {"quantity": "mass", "value": 0.157, "unit": "kg"})
        self.assertEqual(len(server.events("tool_call")), 2)

    def test_http_initialization_notification_gate_and_isolated_sessions(self) -> None:
        server = self.server(initialize=False)
        self.assertIn("result", server.initialize(notify=False))
        self.assertEqual(server.request("tools/list")["error"]["code"], -32600)
        server.notify("notifications/initialized")
        original_session = server.session_id
        recorded = server.call("engineering.record", {"measurement": MEASUREMENT})["result"]["structuredContent"]
        self.assertEqual(recorded["resource"]["revision"], "r2")
        server.session_id = None
        server.initialize()
        self.assertNotEqual(server.session_id, original_session)
        second = json.loads(server.request("resources/read", {"uri": "mock://plate"})["result"]["contents"][0]["text"])
        self.assertEqual(second["revision"], "r1")
        self.assertNotIn("measurement", second)
        server.session_id = original_session
        original = json.loads(server.request("resources/read", {"uri": "mock://plate"})["result"]["contents"][0]["text"])
        self.assertEqual(original["revision"], "r2")

    def test_http_accept_content_type_origin_protocol_and_session_errors(self) -> None:
        server = self.server()
        ping = {"jsonrpc": "2.0", "id": "http-ping", "method": "ping"}
        cases = [
            ({"Accept": "application/json"}, 406),
            ({"Content-Type": "text/plain"}, 415),
            ({"Origin": "https://untrusted.example"}, 403),
            ({"MCP-Protocol-Version": None}, 400),
            ({"MCP-Protocol-Version": "2026-07-28"}, 400),
            ({"Mcp-Session-Id": None}, 400),
            ({"Mcp-Session-Id": "unknown-session"}, 404),
        ]
        for headers, expected_status in cases:
            with self.subTest(headers=headers):
                self.assertEqual(server.exchange(message=ping, headers=headers)[0], expected_status)
        self.assertEqual(server.exchange(method="GET")[0], 405)
        self.assertEqual(server.request("ping")["result"], {})
        self.assertEqual(server.events("tool_call"), [])

    def test_http_session_deletion_invalidates_access(self) -> None:
        server = self.server()
        self.assertEqual(server.exchange(method="DELETE")[0], 204)
        status, _, _ = server.exchange(message={"jsonrpc": "2.0", "id": 99, "method": "tools/list"})
        self.assertEqual(status, 404)

    def test_http_disconnect_preserves_mutation_for_explicit_readback(self) -> None:
        server = self.server("--fault", "disconnect-after-mutation", "--fault-tool", "engineering.record")
        with self.assertRaises(http.client.RemoteDisconnected):
            server.call("engineering.record", {"measurement": MEASUREMENT})
        self.assertEqual(len(server.events("tool_call")), 1)
        self.assertEqual(len(server.events("mutation")), 1)
        resource = json.loads(server.request("resources/read", {"uri": "mock://plate"})["result"]["contents"][0]["text"])
        self.assertEqual(resource["revision"], "r2")
        self.assertEqual(resource["measurement"], MEASUREMENT)
        self.assertEqual(len(server.events("tool_call")), 1, "Readback must not replay the mutation")

    def test_http_malformed_json_has_error_response_without_execution(self) -> None:
        server = self.server()
        status, _, body = server.exchange(raw=b'{"jsonrpc":"2.0","id":1,"method":"ping","params":{"value":NaN}}')
        self.assertEqual(status, 400)
        self.assertEqual(json.loads(body)["error"]["code"], -32700)
        self.assertEqual(server.events("tool_call"), [])


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases: dict[str, dict] = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.cases[test.id()] = {"id": test.id(), "status": "passed"}

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.cases[test.id()] = {"id": test.id(), "status": "failed", "reason": self._exc_info_to_string(error, test)}

    def addError(self, test, error):
        super().addError(test, error)
        self.cases[test.id()] = {"id": test.id(), "status": "failed", "reason": self._exc_info_to_string(error, test)}

    def addSubTest(self, test, subtest, error):
        super().addSubTest(test, subtest, error)
        if error:
            self.cases[test.id()] = {"id": test.id(), "status": "failed", "reason": self._exc_info_to_string(error, test)}

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.cases[test.id()] = {"id": test.id(), "status": "not run", "reason": reason}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Write a machine-readable result; parent directory must exist")
    options = parser.parse_args()
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromTestCase(MockProtocolTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(MockHTTPTests),
    ])
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    if options.report:
        report = {
            "suite": "mock-mcp-protocol", "suiteVersion": VERSION,
            "protocolVersion": "2025-11-25", "generatedAt": datetime.now(timezone.utc).isoformat(),
            "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
            "python": sys.version, "platform": platform.platform(),
            "serverSha256": hashlib.sha256(SERVER.read_bytes()).hexdigest(),
            "testSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "snapshots": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted((ROOT / "snapshots").glob("*.json"))},
            "scope": "Mock provider protocol behavior only; not full MCP certification, independent executor conformance or real CAD evidence",
            "counts": {"total": result.testsRun, "passed": sum(case["status"] == "passed" for case in result.cases.values()), "failed": sum(case["status"] == "failed" for case in result.cases.values()), "notRun": len(result.skipped)},
            "cases": list(result.cases.values()),
        }
        options.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
