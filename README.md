# Engineering Process Specification

An experimental exchange profile and implementer kit for engineering processes
that independent applications can read and execute without Wright.

Use existing **CWL v1.2** for workflow/data flow, **MCP 2025-11-25** for named tool
communication, **RO-Crate 1.2** for exchange packaging, and JSON Schema for data
contracts. The added profile specifies provider/resource identity, preservation,
binding, diagnostics and acceptance evidence. There is no new workflow grammar.

A Solid Edge MCP process remains a Solid Edge MCP process when shared. A missing
provider produces an availability diagnostic and preserves the received package.
Changing provider is an explicit new process revision.

## Start here

| Your task | Entry point |
|---|---|
| Run the calculation without Wright | [Quickstart](docs/quickstart.md) |
| Author a process, as a person or AI | [Authoring guide](docs/authoring.md), [examples](examples/README.md) |
| Implement a receiving application | [Integration guide](docs/implementer-guide.md), [diagnostics](docs/diagnostics.md) |
| Understand the required behavior | [Core draft](spec/core-draft.md), [schemas](schemas/requirements.schema.json) |
| Evaluate interoperability claims | [Conformance guide](conformance/README.md), [goal audit](docs/goal-audit.md) |
| Understand Wright compatibility | [Versioned mapping and capture recipe](docs/wright-compatibility.md) |
| Compare supported environments and layers | [Compatibility matrix](docs/compatibility.md) |
| Change the draft | [Contribution rules](CONTRIBUTING.md), [maintenance](docs/maintenance.md) |

The two demonstration paths are Python/cwltool and Node/StreamFlow, with separate
provider resolvers and MCP adapters. They share the profile, fixtures and some
upstream CWL parsing libraries. Repository-authored demonstrations do not prove
independent organizational adoption. [Progress and evidence](PROGRESS.md) records
the actual tested scope; a successful example is not full conformance.

Both paths passed **60/60 mandatory core cases**; eight real-CAD/approval
observations remain explicitly not run. The installed-artifact walkthrough
passed 23 commands and five MCP runs without Wright. See the
[retained results](conformance/results/2026-09-07/README.md) and
[consumer evidence](docs/adopter-evidence.json).

## Repository map

- `spec/`, `schemas/`: normative experimental requirements and structural rules.
- `examples/`: minimal, quantity calculation, mock MCP handoff, explicit provider
  replacement, and clearly scoped Solid Edge/approval capture cases.
- `src/epx/`, `applications/node/`: locally installable CLI/library implementations.
- `conformance/`, `tests/`, `tools/`: test catalog, results, provider fixture,
  repository checks and adopter/capture utilities.
- `docs/`: onboarding, integration, maintenance and compatibility.
- `research/`, `use-cases/`, `decisions/`, `experiments/`: source-backed reasoning
  and the working experiment that selected the profile.

## Status and decisions

This is draft **0.1.0-draft.1**, not stable 1.0 or a recognized standard.
Real CAD execution, richer human approval, outside adoption, licensing,
contributor-IP terms and public distribution are separate readiness gates.
Nothing here chooses licensing terms or changes repository visibility.

The [comparison](research/comparison.md), [findings](research/findings.md) and
[source register](research/sources.md) preserve the research. The
[CWL decision](decisions/003-cwl-core.md) follows actual OWS/CWL experiments and
supersedes the earlier provisional OWS preference for this core. Wright was
inspected read-only; its `.wflow` files do not already conform to this profile.

Project boundaries remain in [VISION](VISION.md), [RESEARCH](RESEARCH.md),
[AGENTS](AGENTS.md) and the active [implementation goal](IMPLEMENTATION_GOAL.md).
