# AgentIsOK Threat Model

## Status and method

This is an initial threat model for protocol design and prototyping. It is not a completed security assessment. Threats are grouped across technical, privacy, operational, governance, and market layers because a cryptographically correct token can still participate in an unsafe gatekeeping system.

## Security objectives

The system should:

- bind evidence to the intended origin, request, action, presenter, and time;
- prevent unauthorized replay, scope expansion, and credential transfer;
- preserve origin policy authority;
- minimize disclosure and cross-origin linkability;
- distinguish denial from operational uncertainty;
- enforce every decision obligation;
- support prompt revocation and bounded failure;
- avoid mandatory dependence on one provider; and
- provide sufficient evidence for audit, correction, and recourse without central surveillance.

## Assets

- Agent and harness signing keys.
- Principal credentials and approval mechanisms.
- Delegations, mandates, and authorization scopes.
- Origin policy and sensitive fraud logic.
- Challenge nonces and replay state.
- Issuer keys, trust metadata, and revocation state.
- Pairwise identifiers and rate-limit state.
- Request content and task intent.
- Clearance artifacts and application sessions.
- Decision, enforcement, and outcome records.
- Ecosystem registries and conformance marks.
- The availability and neutrality of the agent-access path.

## Adversaries and failure sources

- An unaffiliated attacker with network access.
- A malicious or compromised agent.
- A compromised harness or exported key.
- A malicious but validly represented principal.
- A deceptive origin or verifier.
- A compromised, negligent, or dishonest issuer.
- A malicious intermediary or metadata host.
- An insider at an issuer, origin, operator, or provider.
- A dominant platform seeking discriminatory control.
- Colluding ecosystem providers.
- Misconfiguration, stale caches, software defects, and outages.
- Prompt injection or untrusted content steering an agent across authority boundaries.

## Assumptions

- Transport security is correctly deployed, but TLS alone does not provide end-to-end request binding through all intermediaries.
- Cryptographic primitives and libraries are sound when correctly used.
- Origins can maintain local policy and enforcement, though misconfiguration remains in scope.
- Issuer trust is a policy decision, not an intrinsic property of a signed credential.
- Agents and principals can behave abusively while holding valid credentials.
- No hosted service is perfectly available, neutral, or immune from capture.

## Technical threats

| Threat | Failure | Required mitigation |
|---|---|---|
| Replay | A valid response is reused | Unpredictable nonce, short expiry, request binding, atomic replay state |
| Parallel redemption | One-time evidence is consumed concurrently | Atomic compare-and-set or equivalent transaction semantics |
| Request substitution | Evidence is attached to a different method, path, body, or origin | Cover method, authority, target, content digest, challenge, and time in the proof |
| Scope escalation | A narrow mandate is interpreted broadly | Structured actions, exact resource/quantity bounds, deny unknown semantics |
| Audience confusion | Evidence for one service is accepted by another | Exact origin/audience validation and pairwise subjects |
| Stolen presenter key | An attacker impersonates a known agent | Protected key storage, proof of possession, short lifetimes, rotation, revocation, optional attestation |
| Bearer leakage | A clearance or mandate is copied | Sender-constrained artifacts and no credentials in model/prompt context |
| Algorithm downgrade | Participants negotiate a weak or ambiguous profile | Versioned profiles, origin minimums, no silent fallback |
| Key substitution | Discovery points to attacker keys | Authenticated metadata, issuer pinning/trust policy, rotation rules, cache bounds |
| Signature coverage gap | Security-relevant components are unsigned | Profile-defined mandatory covered components and conformance vectors |
| Canonicalization ambiguity | Signer and verifier interpret a request differently | Reuse mature canonicalization standards and test intermediary transformations |
| Revocation race | Recently revoked authority remains accepted | Bounded cache freshness, event updates where available, risk-tiered fail behavior |
| Policy mismatch | Decision uses stale or unintended policy | Bind policy identifier/version into challenge and receipt |
| Obligation loss | Middleware allows but fails to apply a limit | Typed enforcement contract; reject unsupported obligations |
| Retry confusion | A challenge retry creates duplicate application actions | Idempotency keys and clear separation of verification from action execution |
| Step-up phishing | Approval is obtained for a different action | Human-readable structured approval bound to origin, action, limits, and nonce |
| Parser differential | Implementations interpret evidence differently | Strict schemas, reject duplicates/unknown critical fields, multi-implementation vectors |
| Resource exhaustion | Expensive verification becomes a denial-of-service vector | Size/count limits, cheap checks first, caching, quotas, bounded algorithms |
| Trust MITM | An edge or vendor verifies and the origin only sees a header or score | Origin reconstructs the decision from the same presentation bytes; edge enforcement is not a substitute for origin verification |
| Observation MITM | A TLS terminator, hosted verifier, or shared replay store sees destinations, mandates, and timing | Local data plane; no protocol-critical vendor call; treat shared nonce/rate stores as an activity graph |
| Key-identifier join key | A pairwise `keyid` encodes the relying origin | Opaque presented key IDs; do not put the origin host in the wire identifier |

## Delegation and agent threats

### Confused deputy

Untrusted content may induce an agent to apply legitimate authority to an attacker's goal. Origin binding alone does not prove that the request matches the principal's intent.

Mitigations include structured mandates, tool-bound policy enforcement outside model context, action previews, scope attenuation, and step-up for irreversible actions.

### Over-broad delegation

Convenient wildcard scopes can allow unintended actions. Profiles should prefer explicit action, resource, quantity, duration, and delegation-depth bounds. Origins must not infer broad authority from the mere existence of a mandate.

### Legitimate principal abuse

A real person or organization can authorize spam, scalping, fraud, harassment, or denial of service. Human backing is an accountability signal, not a benignness proof. Origins still need rate, inventory, economic, behavioral, and business controls.

### Agent composition

An authorized agent may delegate to sub-agents or tools. Downstream authority must be attenuated, provenance must remain intelligible, and the immediate presenter must prove possession. The initial protocol may reject delegation chains it cannot evaluate safely.

## Issuer and verifier threats

### Malicious issuer

A cryptographically valid issuer can assert false, misleading, or over-broad claims. Origins need explicit trust configuration, qualification evidence, issuer-specific limits, revocation, transparency, and the ability to require multiple independent proofs.

### Verifier overreach

A verifier can request unnecessary identity data, retain task histories, or return opaque scores. Challenges and logs should be inspectable, disclosure minimized, and universal scores outside the protocol.

### Hosted verifier compromise

A hosted verifier can leak evidence, falsify facts, or become unavailable. Local verification, evidence digests, signed metadata, provider replacement, and minimized hosted inputs reduce the blast radius.

Accepting a CDN or WAF classification as the only request-integrity result is a hosted verifier, even when no AgentIsOK API is called. The origin must still be able to verify the presentation (or an equivalent Web Bot Auth signature) with its own trust configuration.

### Shared replay and rate state

Atomic nonce and pairwise quota state at many enforcement points requires a consistent store. Whoever operates that store learns that a presenter hit an origin at a time. That is enough to reconstruct a cross-site or cross-route activity graph without a global subject identifier. Single-origin, origin-held replay state is the `0.1` assumption. A vendor nonce service must be documented as observation risk, not as local verification.

## Privacy threats

| Threat | Impact | Mitigation direction |
|---|---|---|
| Global subject identifier | Cross-origin activity graph | Pairwise or origin-specific identifiers |
| Issuer learns destination | Central browsing history | Blind/unlinkable issuance where profiles permit; pre-issued bounded evidence |
| Origin learns civil identity | Unnecessary exposure and discrimination | Attribute proofs, commitments, pseudonyms, policy minimization |
| Natural-language task disclosure | Reveals sensitive intent | Structured action classes or hashes |
| Stable agent key everywhere | Cross-site linkability | Origin-specific keys whose *presented* identifiers do not encode the origin |
| TLS terminator sees presentations | CDN or reverse proxy learns mandates and pairwise IDs | Architecture is scoped disclosure to whoever terminates HTTPS; do not claim unlinkability from the edge |
| Edge-only verdict | Origin cannot reproduce allow/deny | Origin-authoritative verification: same bytes, origin keys, origin policy |
| Central outcome collection | Surveillance and breach concentration | Local records; separate, consented, minimized outcome sharing |
| Diagnostic leakage | Reveals fraud logic or private claims | Stable coarse reason codes, protected detailed logs |
| Timing and quota correlation | Re-identification across services | Scoped buckets, aggregation, retention limits, privacy review |

Privacy and fraud prevention can conflict. Linkability must be explicit, scoped, and justified rather than hidden inside an allegedly anonymous identifier.

Draft `0.1` privacy is scoped disclosure to the origin, not unlinkability from the origin or its TLS terminator. Origin-issued, origin-audience mandates prevent a third-party issuer from building a destination dossier. They do not hide the presentation from the box that terminates TLS.

## Availability and operational threats

- Issuer, revocation, or hosted-verifier outage.
- Stale metadata after key compromise.
- Replay-store partition or inconsistent edge state.
- Policy rollout that unexpectedly denies legitimate traffic.
- Adapter update that changes claim interpretation.
- Concentrated dependency on one CDN, cloud, or identity provider.

Deployments need bounded cache rules, explicit `indeterminate` handling, safe rollback, policy versioning, circuit breakers, shadow evaluation, and observability that does not defeat privacy.

## Governance and ecosystem threats

### Gatekeeper capture

One or two providers could control a required directory, dominant verifier, conformance mark, or distribution channel and decide which agents may access the web.

Mitigations:

- no mandatory central service or proprietary directory;
- origin-controlled trust lists and local verification;
- open-source reference implementations and at least one independent implementation;
- public, vendor-neutral conformance tests;
- transparent, appealable registry rules;
- portable configuration and data;
- royalty-free implementation rights;
- governance representation across origins, agents, issuers, users, and independent experts; and
- movement of mature protocol work into an established open standards process.

### Pay-to-play qualification

An issuer or agent might be recognized only after purchasing services or entering a private commercial arrangement. Compatibility and qualification criteria must be public, objective, proportionate, and separable from commercial offerings.

### Conformance-mark abuse

A trademark can help users identify tested implementations but can also become a private licensing choke point. Mark rules must test observable compatibility, be nondiscriminatory, and permit truthful statements about independent implementation even when a formal mark is not used.

### Governance capture

A nominally open project can be dominated through maintainer concentration, meeting access, funding, or opaque decision-making. Public records, conflict disclosure, review periods, multiple maintainers, appeals, and explicit anti-capture rules are required.

### Protocol ossification

A dominant early implementation can turn accidental behavior into the de facto standard. Independent implementations and test vectors must distinguish specified behavior from implementation quirks.

## Abuse cases the protocol does not solve alone

- A validly authorized scalper exhausting inventory.
- A person directing an agent to harass or spam.
- A compromised origin intentionally discriminating among users or agents.
- An agent performing a permitted sequence whose combined effect is harmful.
- Fraud based on true identity and valid payment credentials.
- Unsafe application behavior after clearance.

These require origin policy, domain-specific controls, monitoring, recourse, and sometimes law or institutional governance.

## Required security evidence before production

- A complete protocol specification with unambiguous processing rules.
- At least two independent implementations.
- Published positive and negative conformance vectors.
- Threat-model review by origin, agent, identity, abuse, accessibility, and privacy practitioners.
- Independent cryptographic and application security assessment.
- Replay, race, downgrade, privacy, and parser-differential testing.
- Incident response and revocation exercises.
- Measured behavior during a bounded shadow deployment.
- Clear residual-risk documentation for operators.

## Residual risk

AgentIsOK can improve evidence and policy at an automation boundary. It cannot prove that software will behave well after admission, that a principal's goals are benign, or that an origin's policy is fair. The name must never obscure those residual risks.
