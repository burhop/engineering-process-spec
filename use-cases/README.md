# Engineering cases for the first exchange

These cases reuse Wright's existing examples and requirements. They are proposed
interoperability experiments; this review did not run them or qualify a second
executor. Readiness, engineering correctness and product-demonstration value are
separate assessments. A long graph or many valid files alone proves neither.

## A. Calculation with units and acceptance evidence

**Job:** evaluate heating behavior and select a heater under the existing assignment.
Use the existing
[water-heater sizing template](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/engineering_workflow_templates/templates/water-heater-sizing.workflow.wflow)
and its retained
[output fixture](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/tests/fixtures/retained-process-validation/water-heater-sizing-01/attempt-005/artifacts/energy-summary.csv)
and [validation profile](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/process_validation/profiles/water-heater-sizing-01.json).
Template and retained campaign are separate artifacts; do not assume the template
alone reproduces that historical run or silently bind it to a campaign profile.

Preserve the selected source's actual calculation/solver bindings, declared
parameters and units. Carry its numerical outputs to the downstream engineering
decision, with the same criteria and exact output identities. Verify quantities
and checks independently; a generated explanation is not calculation evidence.

**Exchange controls:** differing receiver defaults, unavailable solver, changed
input/reference, unit mismatch and failed check. This is a bounded technical
interoperability case, not automatically a flagship multi-tool demonstration.

## B. CAD → measured geometry → thermal comparison

**Job:** compare two heat-spreader sizes using actual CAD and solver handoffs.
The existing [heat-spreader example](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/examples/process-interfaces/heat-spreader-sizing/README.md)
uses AgentCAD for STEP creation/read-back and OASiS/scikit-fem for temperature
fields, consuming measured rectangular dimensions and exact STEP hashes. It
compares the existing 100×40×2 and 100×60×2 mm plates, heat balance and refinement
under the unchanged validation profile.

Preserve the chosen CAD/solver providers, resource/project identities, path
mappings, data handoffs, profile/baseline and declared reviews. Keep both original
failed and revised evidence. The documented solver scope is rectangular geometry,
not arbitrary STEP meshing, general FEA or physical thermal qualification.

The example records a later CAD provider rejecting the previously supported
manual STEP export despite exposing the `run` tool/schema. This is a concrete
reason schema equality alone cannot establish provider compatibility. Rebind to a
qualified compatible provider or explicitly revise the process; do not suppress
the incompatibility.

**Exchange controls:** exact same-provider execution, missing application, changed
provider semantics, mismatched STEP hash, failed thermal check and stale review.
This supplies a substantive multi-tool contrast to the calculation case.

## C. Declared input and review before downstream action

**Job:** collect a declared decision, inspect exact engineering outputs, and permit
only the subsequent action defined by the process. Use the existing
[sheet-metal supplier handoff template](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/engineering_workflow_templates/templates/sheet-metal-supplier-handoff.workflow.wflow)
as a source for a bounded fixture, after resolving its actual dependencies.
The original [Solid Edge case](../VISION.md#preserve-the-authors-actual-tool-choices)
remains a proposed provider-specific case; this review does not claim it is the
provider bound by every sheet-metal example or that a new live run passed.

Distinguish preparation inputs, declared Request input responses, automatic
validation, engineering review and external-action approval. For input-specific
fixtures, reuse the implemented
[first-step tests](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/tests/test_process_first_human_input.py)
and [conditional-input tests](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/tests/test_process_conditional_human_input.py),
without representing those isolated tests as a complete engineering chain.

**Exchange controls:** close/reopen at a wait, invalid/stale/duplicate answer,
changed output after review, missing downstream capability and unconfirmed action.
First qualify a digital/no-effect continuation; real supplier or machine actions
retain separate authorization. Importing historical answers or approvals is not
part of the experiment.

## Shared evidence required

For each case record the engineering objective, exact existing source/profile,
substantive tools and their contributions, ordered artifact handoffs, final useful
result, acceptance evidence and limitations. Both implementations must use the same
specified provider contract or disclose an explicit process revision. A portable
package should still be inspectable when its provider is unavailable.

Select and freeze the minimal useful subset before running it. These cases do
not authorize rewriting Wright's 30 examples, changing their assignments,
relaxing checks or resuming protected historical campaigns.
