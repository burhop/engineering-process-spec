# Engineering Process Specification

Share an engineering process between tools without losing its intended operations,
chosen providers, inputs, instructions, checks or human decisions.

**Experimental draft, implementation profile updated 19 November 2026.** This
repository describes what tools should preserve when they exchange an engineering
process. The Wright profile records the source format, JSON bundle and fixed MCP
calls that developers can use today. An independent implementation is the next
interoperability milestone.

## Start here

| You want to… | Read |
|---|---|
| Understand the sharing contract | [Interchange draft](spec/interchange-draft.md) |
| Read a native workflow or its JSON bundle | [Current Wright implementation profile](profiles/wright.md) |
| Run a workflow and inspect a real result | [Wright quickstart](https://github.com/burhop/wright/tree/85f97930927b672ddf7da8cc65e89569236f4f44#run-the-example) |
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

The standalone Wright development version `0.1.0.dev2` reads native
`.workflow.wflow` files and the `wright.workflow-bundle/1` JSON envelope.
You can inspect a definition without a provider connection, then run its
supported steps against caller-configured MCP servers. A portable fixed-call
binding identifies the required provider, build, tool and contract digest.
Local executable paths and access belong to the receiving installation.
[Executable profile](profiles/wright.md) · [Wright schemas and source](https://github.com/burhop/wright/tree/85f97930927b672ddf7da8cc65e89569236f4f44/src/wright_workflow)

In the runnable example, one server writes two coordinates and another measures
the distance between them. The expected result is 5 mm. The receipt identifies
the writer’s output port and the exact file consumed by the reader. This makes
the example a starting point for testing another reader or executor.
[Example files](https://github.com/burhop/wright/tree/85f97930927b672ddf7da8cc65e89569236f4f44/examples/handoff) · [Conformance plan](conformance/README.md)

The October review records the earlier application’s import, authoring and review
contracts and identifies the code revisions examined at that time.
[October implementation snapshot](profiles/wright-october-2026.md) · [Evidence inventory](research/wright-code-review.md)

## Next milestone

Have an independent reader preserve a real Wright package, then qualify an
independent executor for a deliberately bounded subset. Start with engineering
calculation, a specific CAD operation and a declared human decision. Compare
actual handoffs and acceptance evidence; round-tripping JSON alone is insufficient.

Specification changes go through pull requests. Implementation stays in Wright
while its language evolves. Licensing and external contribution terms remain
undecided; this update does not choose them or announce a stable release.
