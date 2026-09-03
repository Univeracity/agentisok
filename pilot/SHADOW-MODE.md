# Shadow-mode deployment contract

## Invariant

Shadow mode observes and compares. It does not authorize, block, redirect, challenge, mutate, retry, or execute the protected action.

The incumbent control and application response remain authoritative and byte-for-byte unchanged by the shadow adapter.

## Required properties

- The adapter is removable without changing the application path.
- Evaluation has a strict timeout and cannot delay the incumbent response beyond an agreed budget.
- Evaluation errors are recorded as `indeterminate`; they never become an allow.
- The origin can reconstruct a result from the same presentation bytes, trust configuration, policy version, and verifier version.
- Raw credentials and presentation bodies are not exported to a metrics sink.
- Sampling and retention are explicit.
- A kill switch is owned and tested by the origin.

## Placement

The adapter may run in an edge worker, reverse proxy, service mesh, or application middleware. Placement must document:

- which component terminates TLS;
- which component sees the original request bytes;
- whether a CDN rewrites authority, path, query, headers, or body;
- where verification occurs;
- where nonce and rate state reside; and
- which third parties can observe presentations or decisions.

“Local” means under origin control with reproducible verification. A vendor header that says an agent is verified is evidence input, not a locally reconstructable decision.

## Evaluation flow

```text
incoming request
      |
      +--------------------------> incumbent control/application
      |                                      |
      |                                      v
      |                              authoritative response
      |
      +--> sampled shadow context --> AgentIsOK evaluator
                                             |
                                             v
                                      minimized observation

return authoritative response unchanged
```

The evaluator should receive only the bytes and local context needed to reproduce the proposed clearance decision. The metrics sink receives the minimized observation in [METRICS.md](METRICS.md), not the evidence.

## Incumbent decision mapping

Map existing outcomes into a small local vocabulary:

- `allow`;
- `challenge`;
- `block`;
- `rate_limit`;
- `error`; or
- `unknown`.

Preserve the raw vendor reason only in protected origin logs if needed. Do not export proprietary fraud features to the public metrics format.

## AgentIsOK decision mapping

Use the protocol values:

- `allow`;
- `allow_with_obligations`;
- `step_up`;
- `deny`; or
- `indeterminate`.

Record separately whether every critical obligation would have been enforceable. Do not relabel an unenforceable conditional allow as `allow`.

## Rollout

### 0. Offline validation

- Validate schemas and all conformance vectors.
- Reproduce decisions on synthetic or approved historical inputs.
- Inspect emitted observations for prohibited fields.
- Exercise timeout, sink failure, and kill-switch behavior.

### 1. Minimal live sample

- Sample the smallest useful portion of one action.
- Compare event counts with origin logs.
- Confirm no user-visible response difference.
- Confirm the origin can reconstruct sampled decisions.

### 2. Expanded sample

- Increase sampling only after privacy, latency, error, and label-quality review.
- Keep the action and policy version fixed long enough for comparison.
- Record every configuration change.

### 3. Evaluation close

- Freeze the analysis interval.
- Measure against pre-registered success and guardrail criteria.
- Delete or aggregate event-level data on schedule.
- Decide whether to stop, reshape, extend shadowing, or begin a separately authorized enforcement review.

## Immediate stop conditions

- Any change to the incumbent response attributable to the adapter.
- Collection of a prohibited field.
- Unbounded verifier latency or resource consumption.
- Decisions that cannot be reconstructed by the origin.
- Unexpected cross-origin identifiers.
- A material increase in application or edge errors.
- Loss of audit, sampling, or deletion controls.

## Not production authorization

A successful shadow result does not authorize production enforcement. That transition requires a fresh threat review, independent implementation evidence, obligation-enforcement tests, incident response, and explicit origin approval.
