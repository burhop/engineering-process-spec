# Required human approval: preservation-only example

This package deliberately requires the unknown core feature `human-approval`.
It preserves an illustrative quality-inspector role and an ungranted approval
subject in its requirements extension. **It must not execute under the current
core profile.** A core reader may copy the package; validation/preflight must
report `unsupported` and make zero engineering calls.

```sh
epx validate examples/inspection-approval
epx inspect examples/inspection-approval
```

Both commands should report the unsupported required feature. Preservation can
still retain the received package bytes. The enclosed calculation graph only
shows what evidence might be an approval subject in a future profile. It is
not an implemented inspection workflow, approval engine or authorization service.
No user has granted approval, and a passed mass check cannot grant it.

A future executable inspection profile needs named part/plan revisions,
identified measured features/datums, provider and measurement evidence, the
human actor/role, an exact subject digest, and stale/rejected/withdrawn decision
rules. Those richer semantics need their own independently passing tests.
An AI verdict or mock measurement does not fill these gaps.
