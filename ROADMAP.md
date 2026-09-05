# Evidence gates

AgentIsOK is a pre-alpha experiment in origin-controlled clearance for authorized agents. A working signature exchange establishes feasibility, not origin value. Advancement depends on evidence, not a release date or the number of supported profiles.

## Current baseline

The public [`draft-01` prerelease](https://github.com/Univeracity/agentisok/releases/tag/draft-01) established the candidate protocol, Python reference, conformance fixtures, pilot packet, and TypeScript shadow adapter. Changes on `main` may go beyond that immutable release.

The current repository has two implemented evidence profiles, 26 conformance vectors, and additional verifier and adapter regression tests. It has no production enforcement path, completed origin study, independent verifier, or independent security assessment. The [reference limits](reference/README.md) describe the implementation boundary.

## What advances the project

| Gate | Evidence needed | If the evidence is absent or negative |
|---|---|---|
| Qualified workflow | Named bounded action; origin owner for abuse policy and rollback; cooperating agent; workable mandate issuance; usable outcome labels | Continue origin discovery; avoid generalizing the protocol |
| Incremental value | Same-workflow comparison with the incumbent and a simpler signed-agent/API baseline; pre-registered benefit and cost thresholds | Use the simpler approach or reshape the workflow |
| Reproducible shadow evaluation | Origin can reconstruct decisions from exact proof bytes and local policy; known label coverage; bounded latency; approved disclosure and retention | Fix the insertion point or stop the pilot |
| Independent interoperability | Separately authored verifier and responder consume shared vectors and exchange fresh messages; ambiguous cases documented | Resolve semantics before adding evidence profiles |
| Enforcement readiness | Independent security review; real keys and issuance; durable replay and revocation policy; tested obligation enforcement, step-up, and rollback | Remain in shadow mode |
| Measured enforcement | Separately approved bounded experiment measuring actual completion and abuse, with uncertainty and guardrails | Roll back, reshape, or stop at the origin's discretion |

None of these gates has been completed merely because CI passes. The TypeScript adapter is not an independent implementation of the verifier. Interoperability work can proceed alongside origin discovery, but neither substitutes for the other.

## Questions the first origin must answer

- Which desirable requests are currently blocked, and how is desirability established independently of an AgentIsOK decision?
- Does explicit delegation change the decision beyond bot recognition and existing authorization?
- Who issues the mandate, what does approval cost, and can an agent answer the challenge while incumbent controls remain in force?
- Can the origin reproduce verification without accepting an opaque edge verdict?
- What remains unobserved because the incumbent blocked the action?
- What minimum benefit would justify operating the integration, and what result would cause the origin to stop?

The [pilot packet](pilot/README.md), [shadow deployment contract](pilot/SHADOW-MODE.md), and [metrics contract](pilot/METRICS.md) are the working instruments for these questions. Partner-specific thresholds, credentials, and raw evidence stay in origin-controlled storage. Publish outcome claims only with partner authorization.

## Useful contributions now

Use the [origin workflow issue template](https://github.com/Univeracity/agentisok/issues/new?template=origin-workflow.md) for a non-sensitive workflow description. Independent implementers can begin with the [protocol](spec/agent-clearance-protocol.md) and [vector manifest](conformance/vectors/manifest.json). Reproducible bugs, ambiguous semantics, and evidence that an existing standard already solves a proposed gap are valuable contributions.

Formal standardization should follow interoperability evidence. The protocol must remain independently implementable without the AgentIsOK name, service, directory, or reference code becoming a mandatory dependency.
