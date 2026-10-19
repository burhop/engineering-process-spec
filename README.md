# Engineering Process Specification

Share an engineering process between tools without losing its intended operations,
chosen providers, inputs, instructions, checks or human decisions.

**Status: experimental draft, reviewed 19 October 2026.** This repository now
contains proposed interchange requirements and a documented Wright implementation
profile. It does not yet define a stable independent language or demonstrate a
second executor. No compatibility guarantee or standards-body endorsement is claimed.

## Start here

| You want to… | Read |
|---|---|
| Understand the sharing contract | [Interchange draft](spec/interchange-draft.md) |
| Export or implement support for today's Wright files | [Wright implementation profile](profiles/wright.md) |
| See what was found in published and unpublished code | [Code review and evidence](research/wright-code-review.md) |
| Choose an interoperability experiment | [Engineering use cases](use-cases/README.md) |
| Evaluate an importer, editor or executor | [Conformance plan](conformance/README.md) |
| Understand project direction and unresolved choices | [Vision](VISION.md), [research agenda](RESEARCH.md) |

## The intended journey

1. Author and accept a process in Wright or another supporting tool.
2. Export its definition and selected declared dependencies.
3. Inspect it in the receiving tool, preserving unavailable blocks and explaining
   missing capabilities. Importing does not start the process.
4. Configure access to the **same specified providers**, resolve inputs and check
   readiness. Replacing a provider is an explicit process edit.
5. Execute locally, inspect exact outputs and checks, and answer declared questions
   or reviews. The receiving runtime owns its new run and permissions.

A process can be a valid definition while unavailable for execution on a particular
machine. Shared definitions carry no credentials, live runs, prior answers,
approval authority or trusted executable UI builds.

## What exists today

Wright implements `wright.workflow-bundle/1`: a JSON envelope containing accepted
`.workflow.wflow` source, dependency declarations, optional assets/layout and
optional editable process-interface source. Saved AI instructions, validation
profile identities and declared human-input semantics are already represented.
Import inspection explicitly returns `can_run: false`.

The reviewed development baseline is
[`bcb5b52f`](https://github.com/burhop/wright/commit/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94)
(15 October). The review also includes a published feature candidate at
[`7e603294`](https://github.com/burhop/wright/commit/7e60329435cb28d8647f71477a6d7d2675e7b941),
the local integration checkout at `7a123ca5` (19 October), and relevant uncommitted
prototype source. Their status and content identities are recorded separately in the
[review](research/wright-code-review.md). Local work is not presented as a release.

These are Wright contracts, not yet a portable standard. Another UI, model or
MCP client using Wright's backend is still using the same executor.

## Next milestone

Have an independent reader preserve a real Wright package, then qualify an
independent executor for a deliberately bounded subset. Start with engineering
calculation, a specific CAD operation and a declared human decision. Compare
actual handoffs and acceptance evidence; round-tripping JSON alone is insufficient.

Specification changes go through pull requests. Implementation stays in Wright
while its language evolves. Licensing and external contribution terms remain
undecided; this update does not choose them or announce a stable release.
