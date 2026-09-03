# Origin design-partner pilot

AgentIsOK is seeking one origin-side design partner for a bounded shadow evaluation. The goal is to learn whether request-bound agent clearance improves a real origin decision—not to deploy a new production authorization gate.

## Good first partners

A useful partner operates a service that:

- receives legitimate automated requests that CAPTCHA or bot controls sometimes block;
- owns measurable abuse, conversion, support, or infrastructure outcomes;
- can identify one low-consequence, bot-sensitive action such as availability or inventory search;
- can run an origin-side or origin-controlled verifier in shadow mode; and
- has a security, fraud, identity, bot-management, or platform owner able to judge the result.

The first pilot excludes payment commitment, legal agreement, healthcare writes, physical control, account recovery, and other high-impact actions.

## What shadow mode means

The incumbent WAF, CAPTCHA, bot product, or application policy remains authoritative. AgentIsOK evaluates in parallel and cannot change the user-visible response or cause the protected action to execute.

The origin retains the presentation bytes, trust configuration, policy version, and decision record needed to reconstruct an AgentIsOK result. A CDN classification header or remote verdict alone is insufficient.

See [SHADOW-MODE.md](SHADOW-MODE.md) for the deployment contract.

## Proposed pilot

### Phase 1: workflow evidence

- Review the most recent desirable automated request that existing controls mishandled.
- Select one action and write its structured scope and consequence boundary.
- Record current control behavior, ownership, privacy constraints, and available outcome labels.
- Pre-register success, guardrail, stop, and deletion conditions.

### Phase 2: offline replay

- Map captured or synthetic requests into the Agent Clearance objects.
- Verify that prohibited data never enters presentations or metrics.
- Exercise every negative conformance vector.
- Confirm the origin can reproduce decisions without an AgentIsOK service.

### Phase 3: live shadow

- Start with a small sampled slice of eligible requests.
- Compare incumbent and AgentIsOK decisions without affecting traffic.
- Increase sampling only after security, privacy, latency, and labeling checks pass.
- Stop immediately on sensitive-data leakage, unexplained decision drift, or operational instability.

### Phase 4: decision

- Publish or privately deliver a result report agreed with the partner.
- Decide whether to continue, reshape, or stop.
- Production enforcement is a separate authorization and security-review decision.

## What the partner supplies

- One bounded origin workflow and internal owner.
- A safe integration point and rollback owner.
- Existing decision and outcome labels with known limitations.
- Origin policy and accepted evidence requirements.
- Security, privacy, and data-retention review.
- A decision on whether findings may be published or anonymized.

## What AgentIsOK supplies

- The open protocol draft, schemas, examples, and conformance vectors.
- A reference verifier and agent responder.
- A deployable edge shadow adapter.
- A minimized metrics contract.
- Assistance mapping the action and evidence profiles.
- A reproducible result report that distinguishes measured evidence from inference.

## Data boundary

The default pilot does not collect:

- natural-language tasks;
- request or response bodies;
- full URLs or query strings;
- civil identities or account identifiers;
- principal, mandate, key, nonce, or signature values;
- IP addresses or raw user-agent strings; or
- payment or other transaction credentials.

Metrics remain origin-controlled by default. Central collection is neither required nor presumed.

## Success gate

The pilot succeeds only if the origin concludes that the clearance evidence materially improves its decision while preserving or improving its abuse posture and meeting privacy and operational constraints.

Technical validity alone is not success.

## Stop or reshape

Stop or materially reshape when:

- the origin has no meaningful desirable agent traffic;
- direct API access or ordinary OAuth solves the workflow more simply;
- reliable outcome labels cannot be obtained;
- useful decisions require a global identifier or central activity history;
- the origin cannot reconstruct decisions locally;
- the integration increases abuse or sensitive-data exposure; or
- no origin owner wants to retain the path after evaluation.

## Start a conversation

Use the repository's **Origin workflow** issue template without posting confidential traffic or customer data. Sensitive deployment details should move to a partner-approved private channel.

The interview guide is [ORIGIN-INTERVIEW.md](ORIGIN-INTERVIEW.md), the outreach plan is [OUTREACH.md](OUTREACH.md), and the measurement contract is [METRICS.md](METRICS.md) with a machine-readable [event schema](schema/shadow-observation.schema.json).
