"""Independent MCP 2025-11-25 client for the declared stdio/HTTP-JSON subset."""

from __future__ import annotations

import os
from pathlib import Path
import queue
import subprocess
import threading
import urllib.error
import urllib.parse
import urllib.request

from . import VERSION
from . import jsonio
from .errors import Problem, invalid, unavailable

PROTOCOL = "2025-11-25"
META_KEY = "engineering-process-provider"


class RpcFailure(Exception):
    def __init__(self, error):
        super().__init__(str(error))
        self.error = error


class LostResponse(Exception):
    pass


class Client:
    def __init__(self, local, timeout=10):
        self.local = local
        self.transport = local["transport"]
        self.timeout = timeout
        self.next_id = 0
        self.session = None
        self.process = None
        self.responses = queue.Queue()
        self.last_call_sent = False
        if self.transport["kind"] == "stdio":
            try:
                self.process = subprocess.Popen(
                    [self.transport["command"], *self.transport["arguments"]],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                )
            except OSError as exc:
                raise unavailable("PROVIDER_START", "BIND-002", "Cannot start configured MCP provider", cause=str(exc)) from exc
            def receive():
                try:
                    for line in self.process.stdout:
                        self.responses.put(line)
                finally:
                    self.responses.put(None)
            threading.Thread(target=receive, daemon=True).start()

    def close(self):
        if self.process:
            try:
                self.process.stdin.close()
                self.process.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired):
                self.process.kill()
                self.process.wait(timeout=2)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def send(self, message, expect_response):
        payload = jsonio.encode(message).replace(b"\n", b"") + b"\n"
        # JSON string newlines remain escaped; remove only encoder formatting.
        if self.transport["kind"] == "stdio":
            try:
                self.process.stdin.write(payload)
                self.process.stdin.flush()
                if message.get("method") == "tools/call":
                    self.last_call_sent = True
            except OSError as exc:
                raise LostResponse("MCP connection closed while sending") from exc
            if not expect_response:
                return None
            while True:
                try:
                    line = self.responses.get(timeout=self.timeout)
                except queue.Empty as exc:
                    raise LostResponse("MCP response timed out") from exc
                if line is None:
                    raise LostResponse("MCP connection closed before its response")
                try:
                    response = jsonio.loads(line)
                except ValueError as exc:
                    raise RpcFailure({"message": "Invalid MCP JSON response", "detail": str(exc)}) from exc
                if isinstance(response, dict) and "method" in response and "id" not in response:
                    continue
                return response
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": PROTOCOL}
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        if self.transport.get("tokenEnv"):
            token = os.environ.get(self.transport["tokenEnv"])
            if not token:
                raise unavailable("CREDENTIAL_UNAVAILABLE", "BIND-002", "Receiving credential environment variable is absent")
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(self.transport["url"], data=payload, headers=headers, method="POST")
        try:
            if message.get("method") == "tools/call":
                self.last_call_sent = True
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                self.session = response.headers.get("Mcp-Session-Id", self.session)
                content = response.read()
                if not expect_response:
                    return None
                if response.headers.get_content_type() != "application/json":
                    raise RpcFailure({"message": "Only the declared MCP HTTP JSON-response subset is supported"})
                return jsonio.loads(content)
        except urllib.error.HTTPError as exc:
            body = exc.read()
            try:
                error = jsonio.loads(body)
            except ValueError:
                error = {"message": "HTTP failure", "status": exc.code}
            raise RpcFailure(error) from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            raise LostResponse("MCP HTTP connection failed before a verified response") from exc
        except ValueError as exc:
            raise RpcFailure({"message": "Invalid MCP JSON response", "detail": str(exc)}) from exc

    def request(self, method, params=None):
        self.next_id += 1
        message = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        if params is not None:
            message["params"] = params
        result = self.send(message, True)
        if not isinstance(result, dict) or result.get("jsonrpc") != "2.0" or result.get("id") != self.next_id:
            raise RpcFailure({"message": "Invalid JSON-RPC response envelope or request identity"})
        if "error" in result:
            raise RpcFailure(result["error"])
        if "result" not in result:
            raise RpcFailure({"message": "Missing JSON-RPC result"})
        return result["result"]

    def initialize(self):
        response = self.request("initialize", {
            "protocolVersion": PROTOCOL, "capabilities": {},
            "clientInfo": {"name": "epx-python", "version": VERSION},
        })
        if response.get("protocolVersion") != PROTOCOL:
            raise unavailable("PROTOCOL_MISMATCH", "BIND-003", "MCP protocol did not match", expected=PROTOCOL, observed=response.get("protocolVersion"))
        if "tools" not in response.get("capabilities", {}):
            raise unavailable("CAPABILITY_UNAVAILABLE", "BIND-003", "MCP provider does not declare tools capability")
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"}, False)
        return response


def configuration(path: Path):
    value = jsonio.read(path)
    jsonio.validate(value, jsonio.load_schema("bindings"), code="BINDINGS_INVALID", requirement="BIND-002")
    return value


def verify_local(required, local, ref):
    for key, fields in (("implementation", ("id", "revision")), ("application", ("id", "version"))):
        for field in fields:
            if local[key][field] != required[key][field]:
                raise unavailable("PROVIDER_IDENTITY_MISMATCH", "BIND-001", "Configured provider differs from author requirement", dependency=ref, expected=required[key], observed=local[key])
    if required["protocolVersion"] != PROTOCOL:
        raise unavailable("PROTOCOL_UNSUPPORTED", "BIND-003", "Adapter does not implement the required MCP revision", dependency=ref, expected=required["protocolVersion"], observed=PROTOCOL)
    trust, transport = local["trust"], local["transport"]
    if transport["kind"] == "stdio":
        if trust["kind"] != "launcher-sha256" or not required["implementation"].get("artifactSha256"):
            raise unavailable("IDENTITY_EVIDENCE_MISSING", "BIND-002", "Stdio requires author-pinned launcher evidence", dependency=ref)
        path = Path(trust["path"]).resolve()
        try:
            actual = jsonio.digest(path.read_bytes())
        except OSError as exc:
            raise unavailable("LAUNCHER_UNAVAILABLE", "BIND-002", "Configured launcher cannot be read", dependency=ref) from exc
        arguments = [Path(arg).resolve() for arg in transport["arguments"] if not arg.startswith("-")]
        if actual != trust["sha256"] or actual != required["implementation"]["artifactSha256"] or path not in arguments:
            raise unavailable("LAUNCHER_IDENTITY_MISMATCH", "BIND-002", "Launcher invocation/digest does not establish intended implementation", dependency=ref, observed=actual, expected=required["implementation"]["artifactSha256"])
    else:
        url = urllib.parse.urlparse(transport["url"])
        if url.username or url.password:
            raise unavailable("CONNECTION_CREDENTIALS", "BIND-002", "Use receiving environment credentials, not URL userinfo", dependency=ref)
        if trust["kind"] != "configured-service" or trust["subject"] != required["implementation"]["id"]:
            raise unavailable("SERVICE_TRUST_MISSING", "BIND-002", "Remote service requires explicit intended-provider trust", dependency=ref)


def verify_metadata(required, message, ref):
    observed = message.get("_meta", {}).get(META_KEY)
    expected = {
        "implementation": required["implementation"]["id"],
        "revision": required["implementation"]["revision"],
        "application": required["application"]["id"],
        "applicationVersion": required["application"]["version"],
    }
    if not isinstance(observed, dict) or any(observed.get(key) != value for key, value in expected.items()):
        raise unavailable("PROVIDER_METADATA_MISMATCH", "BIND-003", "Observed MCP/application identity differs or is unverifiable", dependency=ref, expected=expected, observed=observed)
    if observed.get("executionPlatform") not in required["executionPlatforms"]:
        raise unavailable("PLATFORM_UNAVAILABLE", "BIND-005", "Intended execution platform is unsupported", dependency=ref, expected=required["executionPlatforms"], observed=observed.get("executionPlatform"))
    return observed


def verify_session(package, config, ref, client):
    required = package.requirements["bindings"][ref]
    observed = verify_metadata(required, client.initialize(), ref)
    tools = []
    cursor = None
    seen = set()
    while True:
        listing = client.request("tools/list", {"cursor": cursor} if cursor else {})
        verify_metadata(required, listing, ref)
        tools.extend(listing.get("tools", []))
        cursor = listing.get("nextCursor")
        if not cursor:
            break
        if cursor in seen:
            raise unavailable("TOOL_LIST_INVALID", "BIND-004", "Provider repeats discovery cursor", dependency=ref)
        seen.add(cursor)
    names = [tool.get("name") for tool in tools]
    if len(set(names)) != len(names):
        raise unavailable("TOOL_LIST_INVALID", "BIND-004", "Provider lists duplicate tool identities", dependency=ref)
    by_name = {tool["name"]: tool for tool in tools}
    for node, operation in package.requirements["operations"].items():
        if operation["binding"] != ref:
            continue
        actual = by_name.get(operation["tool"])
        expected = jsonio.read(package.payload(operation["toolContract"]))
        if actual is None:
            raise unavailable("TOOL_UNAVAILABLE", "BIND-004", "Required tool is not available on intended provider", node=node, dependency=ref, expected=operation["tool"])
        for field in ("name", "inputSchema", "outputSchema"):
            if not jsonio.equal(expected.get(field), actual.get(field)):
                raise unavailable("TOOL_CONTRACT_MISMATCH", "BIND-004", "Discovered tool contract changed", node=node, dependency=ref, field=field)
    resources = []
    for resource_id, requirement in package.requirements["resources"].items():
        if requirement["binding"] != ref:
            continue
        try:
            result = client.request("resources/read", {"uri": requirement["uri"]})
            contents = result["contents"]
            matching = [content for content in contents if content.get("uri") == requirement["uri"] and "text" in content]
            if len(matching) != 1:
                raise ValueError("Exactly one matching JSON resource representation is required")
            identity = jsonio.loads(matching[0]["text"])
        except (RpcFailure, KeyError, TypeError, ValueError) as exc:
            cause = exc.error if isinstance(exc, RpcFailure) else str(exc)
            raise unavailable("RESOURCE_UNAVAILABLE", "RES-002", "Required resource cannot be verified", dependency=resource_id, expected=requirement, cause=cause) from exc
        expected = {"id": requirement["uri"], "provider": required["application"]["id"], "revision": requirement["revision"]}
        if not isinstance(identity, dict) or any(identity.get(key) != value for key, value in expected.items()):
            raise unavailable("RESOURCE_REVISION_MISMATCH", "RES-001", "Observed resource identity/revision differs", dependency=resource_id, expected=expected, observed=identity)
        resources.append({"requirement": resource_id, **expected})
    return observed, resources


def preflight(package, config):
    observations = []
    for ref, required in package.requirements["bindings"].items():
        local = config["bindings"].get(ref)
        if local is None:
            raise unavailable("PROVIDER_UNAVAILABLE", "BIND-005", "No local connection is configured for the intended binding", dependency=ref, expected=required)
        verify_local(required, local, ref)
        try:
            with Client(local) as client:
                observed, resources = verify_session(package, config, ref, client)
                observations.append({"binding": ref, "provider": observed, "resources": resources})
        except (RpcFailure, LostResponse) as exc:
            cause = exc.error if isinstance(exc, RpcFailure) else str(exc)
            raise unavailable("PROVIDER_UNAVAILABLE", "BIND-005", "Provider preflight failed", dependency=ref, cause=cause) from exc
    return {"status": "ready", "bindings": observations, "diagnostics": [], "engineeringCalls": 0}
