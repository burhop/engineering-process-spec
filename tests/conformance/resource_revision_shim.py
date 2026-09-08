"""Pinned test-only MCP provider variant: omit observed resource revisions.

This explicit variant keeps the base provider's actual protocol handlers and
audit, verifies its immutable source bytes, and uses its own mock implementation
identity. It is never an implicit replacement for the ordinary mock or any CAD.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

BASE_SHA256 = "bdc4173533f1c7d265947f5cae51cb91131af74e110312cbd0685bde4c31446f"
IMPLEMENTATION = "urn:engineering-process-spec:mock-mcp-unverifiable-resource"


def main():
    source = Path(__file__).resolve().parents[1] / "providers" / "mock_mcp_server.py"
    if hashlib.sha256(source.read_bytes()).hexdigest() != BASE_SHA256:
        print("Pinned base mock provider digest differs", file=sys.stderr)
        return 1
    specification = importlib.util.spec_from_file_location("epx_resource_fault_base", source)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.IMPLEMENTATION = IMPLEMENTATION
    original = module.MockProvider.handle

    def handle(self, request):
        result = original(self, request)
        if request["method"] == "initialize":
            result["serverInfo"]["name"] = "engineering-process-mock-unverifiable-resource"
        if request["method"] == "resources/read":
            for content in result["contents"]:
                value = json.loads(content["text"])
                value.pop("revision", None)
                content["text"] = module.compact_json(value)
            self.audit("resource_revision_omitted", uri=request["params"]["uri"])
        return result

    module.MockProvider.handle = handle
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
