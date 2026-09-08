# Agent instructions

Read VISION.md and RESEARCH.md before working. Preserve the agreed distinction
between a portable process definition and availability of its specified tools.
Never reinterpret a specific MCP/CAD block as a generic substitute without an
explicit process edit by the user.

This repository owns research, the experimental portable specification, schemas,
examples, adopter tooling and conformance demonstrations authorized by
IMPLEMENTATION_GOAL.md. Wright owns its product implementation. Inspect Wright
read-only; do not launch or modify it or run its tests. Distinguish current
implemented behavior from proposals, and preserve uncommitted work.
Use authoritative sources and exact version/revision references. Keep the repo
minimal, recommendations evidence-backed, and uncertainties visible.

Keep the portable definition independent of Wright and installation-local state.
An unsupported feature is different from an invalid definition or unavailable
provider. Preserve received source and intended dependencies in every case.
Do not claim conformance from schema validity or a successful call alone.
Map mandatory draft requirements to executable tests and report exact tested
implementation versions. Keep mocks distinct from real CAD evidence.

Use bounded parallel agent work where it improves implementation or review;
give agents separate file ownership. Record decisions and verification in the
repository so independent implementers do not need conversation history.
Do not select project licenses, change visibility, publish packages/releases,
or claim stable standardization under this implementation goal. Retain notices
required by any reused upstream material.
