# Vision and agreed boundaries

Status: project direction agreed with the owner on 2026-09-07. This is not yet a
normative language specification or a claim about implemented behavior.

## Goal

Enable people and AI systems to create, share, inspect, and execute engineering
work processes without inventing their own language or having to use Wright.
A process created in Wright should be usable by an independent future tool,
provided that tool implements the required language features and has access to
the specified applications, MCPs, resources, and permissions.

Wright is the initial implementation and test environment. The specification
must work with its real engineering workflows. While the language is evolving,
Wright's versioned implementation contracts describe current behavior; this
repository separates that behavior from proposed portable contracts. Do not
silently create a competing definition or claim proposed behavior already works.

## Preserve the author's actual tool choices

A process explicitly using the Solid Edge MCP for sheet-metal work remains a
process using that MCP and CAD application when saved, shared, and reopened.
Portability must not rewrite it as a generic CAD capability or silently replace
it with a different CAD provider. Preserve the intended MCP/provider identity,
operation, relevant version requirements, configuration, inputs, outputs, and
connections. The precise representation and identity/version rules need research.

Provider identity and installation-specific connection details are different:
retain the intended provider/application contract without assuming a server URL,
local path, or credential from the author's installation works elsewhere. How
references are packaged or rebound is an open design question, not permission
to substitute another provider.

## Valid definition versus available execution environment

A process can be a valid, faithfully preserved definition while not executable
in the receiving environment. Different Wright installations can have different
MCPs and CAD applications. This problem exists even before external adoption.

Example: a process contains a Solid Edge MCP sheet-metal block. A recipient
opens it on Linux without access to a supported Solid Edge execution environment.
The application should display the block and preserve its settings, promptly
explain the missing dependency/platform issue, and identify affected execution.
The user may configure access to the intended provider or explicitly replace the
block with another CAD block. Replacement is an intentional process edit, with
configuration and connections checked again; it is not transparent portability.
Do not turn this example into an unverified claim about current vendor OS support.

The language/interchange contract needs to retain requirements and distinguish
an unavailable dependency from an invalid definition. Application behavior owns
environment detection, installation/connection guidance, warning presentation,
execution gating, replacement UI, and recovery assistance. Whether a particular
runtime policy belongs in an optional interoperability profile is for research.

Cloud services can reduce platform coupling but still require the correct service,
resource identity, API compatibility, connectivity, and permissions. A service
being reachable is not evidence that the intended model or dataset is accessible.
Credentials should be supplied by the receiving environment rather than embedded
as secrets in a shared process.

## Outcomes to demonstrate

- A human or AI authors a process in Wright and another tool understands it.
- A supported executor uses the same specified provider and intended resources.
- A missing provider or unsupported environment does not erase or corrupt blocks.
- Opening and saving without edits preserves process meaning, including blocks
  unavailable to the receiving application.
- Explicit provider replacement preserves unaffected work and exposes any broken
  mappings, configuration, or connections for repair.
- Failure reports distinguish missing prerequisites, execution failures, partial
  results, and acceptance checks that did not pass or were never performed.
- Success is supported by defined engineering acceptance criteria, not merely a
  successful API call, an AI's narrative, or a file existing.

## What remains open

Do not assume we must invent an entirely new language. Research whether the best
fit is a small specification, a profile/extension of existing standards, an
interchange package, or a combination. Recommend an approach based on the goals
above and concrete Wright examples. Standardization route, governance, licensing,
packaging, syntax, versioning, and compatibility commitments remain undecided.

The first milestone is a small, independently understandable process exchange
with declared dependencies and verifiable outcomes. Stable 1.0 and formal
standards-body submission should follow implementation and interoperability evidence.
