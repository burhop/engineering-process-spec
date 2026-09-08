"""Deterministic test-only MCP 2025-11-25 provider; no Wright or CAD dependency."""

from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os
from pathlib import Path
import secrets
import socket
import sys
from typing import Any
from urllib.parse import urlparse


PROTOCOL_VERSION = "2025-11-25"
VERSION = "0.1.0-draft.1"
IMPLEMENTATION = "urn:engineering-process-spec:mock-mcp"
APPLICATION = "urn:engineering-process-spec:mock-engineering"
OTHER_APPLICATION = "urn:engineering-process-spec:mock-other-engineering"
META_KEY = "engineering-process-provider"
RESOURCE_URI = "mock://plate"
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


def object_schema(properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties) if required is None else required,
        "additionalProperties": False,
    }


def quantity_schema(units: list[str], quantity: str | None = None) -> dict:
    properties = {
        "value": {"type": "number", "exclusiveMinimum": 0},
        "unit": {"type": "string", "enum": units},
    }
    if quantity:
        properties["quantity"] = {"const": quantity}
    return object_schema(properties, ["value", "unit"])


def result_quantity_schema(quantity: str, unit: str) -> dict:
    return object_schema({
        "quantity": {"const": quantity},
        "value": {"type": "number", "exclusiveMinimum": 0},
        "unit": {"const": unit},
    })


MEASUREMENT_SCHEMA = object_schema({
    "quantity": {"type": "string", "enum": ["mass", "volume", "length", "thickness"]},
    "value": {"type": "number"},
    "unit": {"type": "string", "enum": ["kg", "m3", "mm3", "m", "mm"]},
})
RESOURCE_IDENTITY_SCHEMA = object_schema({
    "id": {"const": RESOURCE_URI},
    "provider": {"type": "string", "minLength": 1},
    "revision": {"type": "string", "pattern": "^r[1-9][0-9]*$"},
})


def descriptor(name: str, description: str, inputs: dict, outputs: dict, read_only: bool) -> dict:
    return {
        "name": name,
        "description": description,
        "inputSchema": {"$schema": SCHEMA_DIALECT, **inputs},
        "outputSchema": {"$schema": SCHEMA_DIALECT, **outputs},
        "annotations": {
            "readOnlyHint": read_only,
            "destructiveHint": False,
            "idempotentHint": read_only,
            "openWorldHint": False,
        },
    }


TOOLS = [
    descriptor(
        "engineering.volume", "Mock rectangular-plate volume from positive lengths; no CAD operation.",
        object_schema({key: quantity_schema(["m", "mm"], "length") for key in ("length", "width", "thickness")}),
        result_quantity_schema("volume", "m3"), True,
    ),
    descriptor(
        "engineering.mass", "Mock mass from positive volume and density; no material certification.",
        object_schema({
            "volume": quantity_schema(["m3", "mm3"], "volume"),
            "density": quantity_schema(["kg/m3", "g/cm3"], "density"),
        }),
        result_quantity_schema("mass", "kg"), True,
    ),
    descriptor(
        "engineering.record", "Record a mock measurement in session state and increment its resource revision.",
        object_schema({"measurement": MEASUREMENT_SCHEMA}),
        object_schema({
            "stored": {"const": True},
            "measurement": MEASUREMENT_SCHEMA,
            "resource": RESOURCE_IDENTITY_SCHEMA,
        }), False,
    ),
]


class ProtocolError(Exception):
    def __init__(self, code: int, message: str, data: Any = None):
        super().__init__(message)
        self.code, self.message, self.data = code, message, data


class ToolInputError(Exception):
    pass


class DisconnectAfterMutation(Exception):
    pass


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def finite_number(value: Any) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def check_keys(value: Any, required: set[str], optional: set[str] = frozenset()) -> None:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise ToolInputError(f"Expected fields {sorted(required)} with optional fields {sorted(optional)}")


def quantity(value: Any, factors: dict[str, str], meaning: str) -> Decimal:
    check_keys(value, {"value", "unit"}, {"quantity"})
    if not finite_number(value["value"]) or value["value"] <= 0:
        raise ToolInputError(f"{meaning} value must be a positive finite number")
    unit = value["unit"]
    if not isinstance(unit, str) or unit not in factors:
        raise ToolInputError(f"{meaning} unit must be one of {sorted(factors)}")
    if "quantity" in value and value["quantity"] != meaning:
        raise ToolInputError(f"Expected quantity meaning {meaning}")
    return Decimal(str(value["value"])) * Decimal(factors[unit])


def checked_measurement(value: Any) -> dict:
    check_keys(value, {"quantity", "value", "unit"})
    allowed_units = {"mass": {"kg"}, "volume": {"m3", "mm3"}, "length": {"m", "mm"}, "thickness": {"m", "mm"}}
    if not finite_number(value["value"]):
        raise ToolInputError("measurement value must be finite")
    if not isinstance(value["quantity"], str) or not isinstance(value["unit"], str):
        raise ToolInputError("measurement quantity and unit must be strings")
    if value["unit"] not in allowed_units.get(value["quantity"], set()):
        raise ToolInputError("measurement quantity and unit are incompatible or unsupported")
    return deepcopy(value)


class MockProvider:
    def __init__(self, options: argparse.Namespace, session_label: str = "stdio"):
        self.options = options
        self.application = options.application
        self.initialized = False
        self.ready = False
        self.revision = 999 if options.resource_state == "revision-mismatch" else 1
        self.measurement: dict | None = None
        self.sequence = 0
        self.tool_calls = 0
        self.session_label = session_label
        self.audit("session_started", protocol=PROTOCOL_VERSION, provider=self.provider_metadata(), fault=options.fault)

    def audit(self, event: str, **fields: Any) -> None:
        if not self.options.audit:
            return
        self.sequence += 1
        # The audit file is explicitly configured by the test operator, never an MCP argument.
        with self.options.audit.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(compact_json({"session": self.session_label, "sequence": self.sequence, "event": event, **fields}) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    def provider_metadata(self) -> dict:
        return {
            "implementation": IMPLEMENTATION,
            "revision": VERSION,
            "application": self.application,
            "applicationVersion": VERSION,
            "executionPlatform": self.options.execution_platform,
        }

    def meta(self) -> dict:
        return {META_KEY: self.provider_metadata()}

    def resource_identity(self) -> dict:
        return {"id": RESOURCE_URI, "provider": self.application, "revision": f"r{self.revision}"}

    def resource_data(self) -> dict:
        value = {
            **self.resource_identity(),
            "length": {"value": 100, "unit": "mm"},
            "width": {"value": 80, "unit": "mm"},
            "thickness": {"value": 2.5, "unit": "mm"},
            "density": {"value": 7850, "unit": "kg/m3"},
        }
        if self.measurement is not None:
            value["measurement"] = deepcopy(self.measurement)
        return value

    def check_resource(self, uri: str) -> None:
        if uri != RESOURCE_URI or self.options.resource_state == "absent":
            raise ProtocolError(-32002, "Resource not found", {"uri": uri, "reason": "absent"})
        if self.options.resource_state == "denied":
            # -32003 is this mock's documented code, not a universal MCP permission code.
            raise ProtocolError(-32003, "Mock resource access denied", {"uri": uri, "reason": "denied"})

    def handle(self, request: dict) -> dict | None:
        method = request["method"]
        params = request.get("params", {})
        if not isinstance(params, dict):
            raise ProtocolError(-32602, "Request params must be an object")
        if "id" not in request:
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
                self.audit("initialized_notification")
            # Notifications never receive responses, including unknown notifications.
            return None
        self.audit("request", method=method, requestId=request["id"])
        if method == "ping":
            return {}
        if method == "initialize":
            if self.initialized:
                raise ProtocolError(-32600, "This mock session is already initialized")
            info = params.get("clientInfo")
            if (not isinstance(params.get("protocolVersion"), str)
                    or not isinstance(params.get("capabilities"), dict)
                    or not isinstance(info, dict)
                    or not isinstance(info.get("name"), str)
                    or not isinstance(info.get("version"), str)):
                raise ProtocolError(-32602, "initialize requires protocolVersion, capabilities and clientInfo")
            self.initialized = True
            return {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}, "resources": {"subscribe": False, "listChanged": False}},
                "serverInfo": {"name": "engineering-process-mock", "version": VERSION},
                "_meta": self.meta(),
            }
        if not self.ready:
            raise ProtocolError(-32600, "Complete initialize and notifications/initialized first")
        if method in ("tools/list", "resources/list", "resources/templates/list"):
            if "cursor" in params:
                raise ProtocolError(-32602, "This mock has one page and no continuation cursor")
            if method == "tools/list":
                if self.options.fault == "changed-default":
                    self.application = OTHER_APPLICATION
                return {"tools": deepcopy(TOOLS), "_meta": self.meta()}
            if method == "resources/templates/list":
                return {"resourceTemplates": []}
            resources = [] if self.options.resource_state == "absent" else [{
                "uri": RESOURCE_URI, "name": "mock-plate", "mimeType": "application/json",
                "description": "Synthetic plate inputs and session-scoped recorded measurement; not a CAD model.",
            }]
            return {"resources": resources}
        if method == "resources/read":
            if not isinstance(params.get("uri"), str):
                raise ProtocolError(-32602, "resources/read requires a URI string")
            self.audit("resource_read", uri=params["uri"])
            self.check_resource(params["uri"])
            return {"contents": [{"uri": RESOURCE_URI, "mimeType": "application/json", "text": compact_json(self.resource_data())}]}
        if method == "tools/call":
            return self.call_tool(params, request["id"])
        raise ProtocolError(-32601, "Method not found", {"method": method})

    def call_tool(self, params: dict, request_id: Any) -> dict:
        name, arguments = params.get("name"), params.get("arguments", {})
        if not isinstance(name, str) or not isinstance(arguments, dict):
            raise ProtocolError(-32602, "tools/call requires a tool name and object arguments")
        if "task" in params:
            raise ProtocolError(-32602, "This mock does not negotiate task-augmented calls")
        if name not in {tool["name"] for tool in TOOLS}:
            raise ProtocolError(-32602, "Unknown tool", {"name": name})
        self.tool_calls += 1
        self.audit("tool_call", name=name, arguments=arguments, requestId=request_id)
        if self.tool_calls > self.options.max_tool_calls:
            return self.tool_error("Mock session tool-call limit exceeded")
        fault = self.options.fault if self.options.fault_tool in (None, name) else "none"
        if fault == "tool-error":
            return self.tool_error("Deliberate mock tool execution failure")
        if fault == "rpc-error":
            raise ProtocolError(-32603, "Deliberate mock protocol failure", {"name": name})
        try:
            if name == "engineering.volume":
                check_keys(arguments, {"length", "width", "thickness"})
                value = Decimal(1)
                for key in ("length", "width", "thickness"):
                    value *= quantity(arguments[key], {"m": "1", "mm": "0.001"}, "length")
                output = {"quantity": "volume", "value": float(value), "unit": "m3"}
            elif name == "engineering.mass":
                check_keys(arguments, {"volume", "density"})
                volume = quantity(arguments["volume"], {"m3": "1", "mm3": "0.000000001"}, "volume")
                density = quantity(arguments["density"], {"kg/m3": "1", "g/cm3": "1000"}, "density")
                output = {"quantity": "mass", "value": float(volume * density), "unit": "kg"}
            else:
                check_keys(arguments, {"measurement"})
                measurement = checked_measurement(arguments["measurement"])
                self.check_resource(RESOURCE_URI)
                self.measurement = measurement
                self.revision += 1
                output = {"stored": True, "measurement": deepcopy(measurement), "resource": self.resource_identity()}
                self.audit("mutation", name=name, requestId=request_id, resource=self.resource_data())
                if fault == "disconnect-after-mutation":
                    self.audit("disconnect_after_mutation", requestId=request_id)
                    raise DisconnectAfterMutation()
            if "value" in output and (not finite_number(output["value"]) or output["value"] <= 0):
                raise ToolInputError("Computed result is outside the positive finite numeric range")
        except (ToolInputError, OverflowError) as error:
            return self.tool_error(str(error))
        if fault == "malformed-output":
            output = {"deliberatelyInvalid": True}
        elif fault == "wrong-unit" and "unit" in output:
            output["unit"] = "s"
        elif fault == "wrong-value" and "value" in output:
            output["value"] *= 1000
            if not finite_number(output["value"]):
                return self.tool_error("Fault would create non-finite output; refused")
        return {"content": [{"type": "text", "text": compact_json(output)}], "structuredContent": output, "isError": False}

    @staticmethod
    def tool_error(message: str) -> dict:
        return {"content": [{"type": "text", "text": message}], "isError": True}


def error_message(error: ProtocolError, request_id: Any = None) -> dict:
    response = {"jsonrpc": "2.0", "error": {"code": error.code, "message": error.message}}
    if request_id is not None:
        response["id"] = request_id
    if error.data is not None:
        response["error"]["data"] = error.data
    return response


def reject_constant(value: str) -> None:
    raise ValueError(f"Non-JSON numeric literal {value}")


def strict_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def finite_tree(value: Any) -> bool:
    if type(value) in (int, float):
        return finite_number(value)
    if isinstance(value, dict):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(finite_tree(item) for item in value)
    return True


def decode_request(raw: bytes) -> dict:
    try:
        request = json.loads(raw.decode("utf-8"), parse_constant=reject_constant, object_pairs_hook=strict_object)
        if not finite_tree(request):
            raise ValueError("Non-finite or unrepresentable numeric value")
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ProtocolError(-32700, "Cannot parse a finite UTF-8 JSON message", {"reason": str(error)}) from error
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
        raise ProtocolError(-32600, "Expected one JSON-RPC request or notification")
    if "result" in request or "error" in request:
        raise ProtocolError(-32600, "Request cannot also contain a response")
    if "id" in request and not (isinstance(request["id"], str) or finite_number(request["id"])):
        raise ProtocolError(-32600, "Request ID must be a string or finite number")
    return request


def dispatch(provider: MockProvider, request: dict) -> dict | None:
    notification = "id" not in request
    try:
        result = provider.handle(request)
        if notification:
            return None
        return {"jsonrpc": "2.0", "id": request["id"], "result": result}
    except ProtocolError as error:
        return None if notification else error_message(error, request["id"])


def serve(options: argparse.Namespace) -> int:
    provider = MockProvider(options)
    while True:
        raw_line = sys.stdin.buffer.readline(1024 * 1024 + 1)
        if not raw_line:
            return 0
        try:
            if len(raw_line) > 1024 * 1024:
                # A bounded test provider closes on oversized frames rather than consuming arbitrary data.
                raise ProtocolError(-32600, "Mock frame size limit exceeded")
            response = dispatch(provider, decode_request(raw_line))
            if response is None:
                continue
        except DisconnectAfterMutation:
            return 0
        except ProtocolError as error:
            response = error_message(error)
        sys.stdout.buffer.write((compact_json(response) + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()
        if len(raw_line) > 1024 * 1024:
            return 0


class MockHTTPHandler(BaseHTTPRequestHandler):
    """Bounded JSON-response Streamable HTTP; one isolated MCP state per session."""

    # Close each HTTP connection after its response; MCP state is in the explicit session.
    protocol_version = "HTTP/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_payload(self, status: int, payload: dict | None = None, session: str | None = None) -> None:
        body = b"" if payload is None else compact_json(payload).encode("utf-8")
        self.send_response(status)
        if payload is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if session:
            self.send_header("Mcp-Session-Id", session)
        if status == 405:
            self.send_header("Allow", "POST, DELETE")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def permit_origin_and_path(self) -> bool:
        origin = self.headers.get("Origin")
        if origin:
            parsed = urlparse(origin)
            if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost"):
                self.send_payload(403, error_message(ProtocolError(-32600, "Origin is not an allowed mock loopback origin")))
                return False
        if self.path != "/mcp":
            self.send_payload(404)
            return False
        return True

    def do_GET(self) -> None:
        if self.permit_origin_and_path():
            self.send_payload(405)

    def do_DELETE(self) -> None:
        if not self.permit_origin_and_path():
            return
        if self.headers.get("MCP-Protocol-Version") != PROTOCOL_VERSION:
            self.send_payload(400, error_message(ProtocolError(-32602, "Expected MCP-Protocol-Version 2025-11-25")))
            return
        token = self.headers.get("Mcp-Session-Id")
        if not token:
            self.send_payload(400)
        elif token not in self.server.sessions:
            self.send_payload(404)
        else:
            del self.server.sessions[token]
            self.send_payload(204)

    def do_POST(self) -> None:
        if not self.permit_origin_and_path():
            return
        accepted = {part.strip().split(";")[0].strip().lower() for part in self.headers.get("Accept", "").split(",")}
        if not {"application/json", "text/event-stream"} <= accepted:
            self.send_payload(406, error_message(ProtocolError(-32600, "Accept must include application/json and text/event-stream")))
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            self.send_payload(415)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 1024 * 1024:
                raise ValueError("Unsupported content length")
            request = decode_request(self.rfile.read(length))
        except (ValueError, ProtocolError) as error:
            protocol_error = error if isinstance(error, ProtocolError) else ProtocolError(-32600, str(error))
            self.send_payload(400, error_message(protocol_error))
            return
        token = self.headers.get("Mcp-Session-Id")
        initializing = request["method"] == "initialize" and "id" in request
        if not initializing and self.headers.get("MCP-Protocol-Version") != PROTOCOL_VERSION:
            self.send_payload(400, error_message(ProtocolError(-32602, "Expected MCP-Protocol-Version 2025-11-25"), request.get("id")))
            return
        created = False
        if initializing and not token:
            if len(self.server.sessions) >= 128:
                self.send_payload(503)
                return
            token = secrets.token_urlsafe(24)
            self.server.session_count += 1
            provider = MockProvider(self.server.options, f"http-{self.server.session_count}")
            created = True
        elif not token:
            self.send_payload(400, error_message(ProtocolError(-32600, "Mcp-Session-Id required"), request.get("id")))
            return
        elif token not in self.server.sessions:
            self.send_payload(404, error_message(ProtocolError(-32600, "Mock session not found"), request.get("id")))
            return
        else:
            provider = self.server.sessions[token]
        try:
            response = dispatch(provider, request)
        except DisconnectAfterMutation:
            # Keep the mutated session for deliberate recovery inspection, but send no response.
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()
            return
        if created and response is not None and "result" in response:
            self.server.sessions[token] = provider
        if response is None:
            self.send_payload(202)
        else:
            self.send_payload(200, response, token if created and "result" in response else None)


def serve_http(options: argparse.Namespace) -> int:
    server = HTTPServer(("127.0.0.1", options.http_port), MockHTTPHandler)
    server.options = options
    server.sessions = {}
    server.session_count = 0
    print(compact_json({"event": "listening", "url": f"http://127.0.0.1:{server.server_port}/mcp", "protocolVersion": PROTOCOL_VERSION}), file=sys.stderr, flush=True)
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def positive_int(value: str) -> int:
    result = int(value)
    if result < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, help="Append mock request/mutation JSONL here; parent directory must exist")
    parser.add_argument("--application", default=APPLICATION, help="Advertised mock application identity; a mismatch fixture")
    parser.add_argument("--execution-platform", default=sys.platform, help="Controlled mock target-platform metadata; not proof of real platform support")
    parser.add_argument("--http-port", type=int, help="Serve JSON-response Streamable HTTP on 127.0.0.1:/mcp; 0 chooses a free port")
    parser.add_argument("--resource-state", choices=["present", "absent", "denied", "revision-mismatch"], default="present")
    parser.add_argument("--fault", choices=["none", "tool-error", "rpc-error", "malformed-output", "disconnect-after-mutation", "wrong-unit", "wrong-value", "changed-default"], default="none")
    parser.add_argument("--fault-tool", choices=[tool["name"] for tool in TOOLS], help="Limit tool faults to this tool; otherwise all matching tools")
    parser.add_argument("--max-tool-calls", type=positive_int, default=256, help="Bound accepted tool requests in this session")
    options = parser.parse_args()
    if not options.application:
        parser.error("--application must not be empty")
    if options.http_port is not None and not 0 <= options.http_port <= 65535:
        parser.error("--http-port must be between 0 and 65535")
    try:
        return serve_http(options) if options.http_port is not None else serve(options)
    except (OSError, RecursionError) as error:
        print(f"Mock provider stopped: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
