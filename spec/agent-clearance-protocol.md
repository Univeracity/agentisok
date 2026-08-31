# Agent Clearance Protocol

- **Working name:** Agent Clearance Protocol (ACP)
- **Draft:** `00`
- **Protocol version in examples:** `0.1`
- **Status:** Exploratory skeleton; incomplete and not suitable for production

## Abstract

This document sketches a protocol through which an HTTP origin can challenge an automated agent for request-bound evidence, evaluate that evidence under local policy, and return a typed clearance decision.

The protocol does not create a universal trusted-agent status. A decision is limited to an origin, action, request or bounded request class, policy, and time. Application authentication, resource authorization, transaction authority, and abuse controls remain separate.

This draft defines an abstract data model and a candidate HTTP binding for experimentation. Header names, media types, discovery paths, identifier namespaces, and assurance classes are provisional and have not been registered.

## 1. Requirements language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** describe intended interoperability requirements for this exploratory draft. They do not imply standards status.

## 2. Design requirements

The protocol must:

1. Leave final acceptance policy with the origin.
2. Bind evidence to the intended origin, request, action, presenter, and time.
3. Permit more than one evidence profile or issuer ecosystem.
4. Preserve evidence provenance through verification.
5. Minimize identity and task disclosure.
6. Distinguish denial, step-up, and operational uncertainty.
7. Express enforceable obligations.
8. Permit local and self-hosted verification without a protocol-critical AgentIsOK service.
9. Support competing implementations through public schemas and conformance vectors.
10. Compose existing security and authorization standards.

## 3. Non-goals

This protocol does not define:

- a universal agent identifier;
- a global trust or reputation score;
- one required identity or proof-of-personhood provider;
- a general delegation credential format;
- payment or other domain-specific transactional authority;
- a policy language;
- a mandatory registry or hosted verifier; or
- proof that an agent will behave safely after clearance.

## 4. Terminology

**Action:** A structured operation and optional resource or quantity bounds evaluated by the origin.

**Agent:** Software attempting the protected action.

**Challenge:** A short-lived origin request for specified evidence bound to an action and protected request.

**Clearance artifact:** An optional, short-lived, sender-constrained origin artifact representing a prior local decision. It is not a portable reputation credential.

**Decision:** The origin's request-specific policy output.

**Evidence:** A proof or credential supplied under an identified evidence profile.

**Evidence profile:** A versioned specification defining evidence semantics, validation, normalized facts, privacy properties, and failure behavior.

**Harness:** The environment operating the agent and mediating keys or credentials.

**Issuer:** An entity that makes and secures claims represented by evidence.

**Obligation:** A structured condition that the policy enforcement point must enforce for a decision to remain valid.

**Origin:** The relying HTTP origin controlling the protected resource and final policy.

**Presenter:** The key-holding agent or harness instance that binds a response to the request.

**Principal:** A person, organization, account, workload operator, or other authority represented in the request.

**Verifier:** The component that validates evidence and emits provenance-preserving facts.

## 5. Abstract protocol

```text
REQUESTED -> CHALLENGED -> PRESENTED -> VERIFIED -> DECIDED -> ENFORCED
                    ^                         |
                    +-------- STEP_UP <-------+
```

An origin can skip a challenge when a valid clearance artifact or ordinary policy already permits the request. Any parse, verification, or dependency failure transitions to a safe `indeterminate` or denial path according to explicit origin policy; it must not silently grant access.

## 6. Protocol objects

### 6.1 Challenge

A challenge contains:

- `protocol_version` — selected protocol version;
- `challenge_id` — globally unambiguous identifier for this challenge instance;
- `nonce` — unpredictable, single-use value with at least 128 bits of entropy;
- `origin` — exact origin issuing the challenge;
- `created_at` and `expires_at` — challenge lifetime;
- `request_binding` — method, target, action, and optional content digest;
- `evidence_requirements` — typed requirements and acceptable profiles;
- `policy` — origin policy identifier and version;
- `privacy` — disclosure and linkability constraints; and
- `response_uri` — endpoint for the candidate detached-response binding.

The origin MUST NOT issue a challenge whose `expires_at` is earlier than `created_at`. The verifier MUST reject a challenge outside its validity window.

The challenge SHOULD request the minimum evidence needed for the action. A natural-language task description SHOULD NOT be required when a structured action, limit, or commitment is sufficient.

### 6.2 Request binding

The request binding identifies the attempted operation:

- uppercase HTTP method;
- absolute target URI;
- structured action type;
- optional resource and constraints; and
- content digest for any representation whose content affects authorization.

Profiles MUST define how redirects, query normalization, intermediary rewriting, retries, and bodies are handled. Origins MUST reject ambiguous bindings.

### 6.3 Evidence requirement

Each requirement includes:

- an origin-local `id` referenced by the response;
- a semantic `class`;
- one or more acceptable versioned `profiles`;
- whether the requirement is mandatory;
- maximum acceptable evidence age where applicable; and
- explicitly requested disclosures.

The initial classes are provisional:

- `request_integrity`;
- `principal`;
- `delegation`;
- `human_presence`;
- `workload`;
- `operator`; and
- `rate_accountability`.

These classes describe evidence purpose, not assurance level. The protocol does not define a single assurance ladder in draft `00`.

### 6.4 Presentation

A presentation contains:

- `protocol_version`;
- `response_id`;
- `challenge_id`;
- `created_at`;
- a request-binding digest;
- presenter key and proof profile;
- one evidence envelope per satisfied requirement; and
- a proof over the presentation and protected request binding.

An evidence envelope identifies the `requirement_id`, evidence `profile`, representation format, and embedded value or reference. Evidence profiles define size limits, retrieval security, issuer discovery, validation, revocation, and normalized output.

A presentation MUST NOT contain evidence for a different origin or broader action and rely on the verifier to attenuate it implicitly.

### 6.5 Normalized facts

Normalized facts are an internal verifier-to-policy contract in this draft. Each fact SHOULD preserve:

- semantic claim and value or commitment;
- subject semantics;
- issuer and trust path;
- audience and action binding;
- issuance, freshness, and expiration;
- presenter-key binding;
- revocation result and freshness;
- evidence profile and digest; and
- warnings or residual uncertainty.

The policy decision point MUST be able to distinguish facts with different provenance even when their simple values are equal.

### 6.6 Decision

A decision contains:

- `decision_id`;
- `challenge_id`;
- request-binding digest;
- evaluation time;
- policy identifier and version;
- one decision value;
- zero or more obligations;
- stable reason codes; and
- optional continuation or clearance artifact.

Allowed values are:

| Value | Meaning |
|---|---|
| `allow` | The challenged request may proceed as bound |
| `allow_with_obligations` | The request may proceed only if every obligation is enforceable and applied |
| `step_up` | Additional evidence or current approval is required |
| `deny` | Local policy affirmatively rejects the request |
| `indeterminate` | Safe evaluation could not be completed |

`challenge` is a protocol state, not a decision value.

Reason codes SHOULD be stable and coarse enough not to expose private evidence or sensitive fraud logic. Detailed diagnostic records belong in appropriately protected origin logs.

### 6.7 Obligations

An obligation contains a versioned `type` and profile-defined parameters. Candidate obligation types include:

- rate or concurrency limit;
- action, route, or resource restriction;
- maximum result, quantity, or value;
- one-time execution;
- idempotency requirement;
- mandatory application authentication;
- step-up before a named later action; and
- audit-record requirement.

The enforcement point MUST reject or narrow an `allow_with_obligations` decision if it cannot interpret and enforce every required obligation.

### 6.8 Clearance artifact

An optional clearance artifact MUST be:

- issued by or for the origin;
- short-lived;
- scoped to an exact request or explicit action class;
- sender-constrained to the presenter's key;
- protected against replay as appropriate;
- revocable or tightly time-bounded; and
- unusable as a cross-origin trust badge.

The artifact format is not selected in draft `00`.

## 7. Processing rules

### 7.1 Origin challenge generation

The origin:

1. Determines the attempted action and preliminary risk class.
2. Generates an unpredictable nonce and challenge identifier.
3. Selects the minimum evidence requirements and compatible profiles.
4. Binds the challenge to the request, origin, policy version, and expiry.
5. Stores sufficient state or creates a protected self-contained challenge to detect tampering and replay.
6. Returns the challenge without caching it in a way that exposes it to unrelated clients.

### 7.2 Agent response creation

The agent or harness:

1. Verifies the challenge origin, expiry, and intended action.
2. Rejects unsupported, excessive, or unauthorized disclosure requirements.
3. Selects one acceptable profile for each required evidence class.
4. Obtains current approval or evidence when necessary.
5. Builds a presentation bound to the challenge and request.
6. Signs using a key that is also bound to sender-constrained evidence where required.

The agent SHOULD make requested disclosures inspectable to the represented principal when practical.

### 7.3 Verification order

Implementations SHOULD perform inexpensive structural and freshness checks before expensive cryptographic or network operations.

The verifier:

1. Parses with strict size, depth, duplicate-key, and count limits.
2. Validates protocol version and critical fields.
3. Validates challenge state, origin, nonce, and expiry.
4. Reconstructs and compares the request binding.
5. Verifies presenter proof and proof-of-possession relationships.
6. Validates each evidence profile, issuer trust, and revocation state.
7. Emits facts with provenance and warnings.
8. Marks one-time state atomically before or with enforcement where needed.

Unknown critical fields or requirement semantics MUST cause safe rejection for this draft.

### 7.4 Policy and enforcement

The origin combines verified facts with local context. An AgentIsOK implementation MUST NOT replace an origin's policy with an issuer or vendor-global verdict.

The enforcement point verifies that the decision matches the current request digest and policy context, applies all obligations, and prevents duplicate action execution.

### 7.5 Step-up

`step_up` returns a continuation URI or a new challenge whose additional requirement is explicit. Approval UI MUST identify the origin, action, resource, quantity or value bounds, expiration, and agent or harness where applicable.

### 7.6 Indeterminate handling

Origins define risk-tiered behavior for `indeterminate`. A failure MUST NOT be converted to `allow` merely for availability. An origin MAY offer an ordinary human path, a narrower action, or a later retry.

## 8. Candidate HTTP binding

This section is non-normative and exists to support a first implementation.

### 8.1 Discovery

A prototype may expose an HTTPS configuration resource at:

```text
/.well-known/agent-clearance
```

The path is not registered. Production standardization would require the applicable IANA and HTTP review.

The resource can advertise protocol versions, challenge endpoint patterns, evidence profiles, signing keys, and size limits. Fetches require TLS and conservative cache rules.

### 8.2 Challenge response

When an otherwise protected request requires clearance, a prototype may return `403 Forbidden` with a JSON challenge and `Cache-Control: no-store`.

```http
HTTP/1.1 403 Forbidden
Content-Type: application/agent-clearance-challenge+json
Cache-Control: no-store

{ ...challenge... }
```

The media type is provisional and unregistered. The response should also retain an ordinary human or application-auth path where appropriate.

### 8.3 Presentation endpoint

The agent POSTs the presentation to the challenge's `response_uri`. The HTTP request is signed using an evidence profile such as RFC 9421 HTTP Message Signatures and covers at least:

- `@method`;
- `@authority`;
- `@path` or a profile-approved target component;
- creation and expiration parameters;
- content type;
- content digest;
- challenge identifier; and
- nonce or a digest that commits to it.

The exact covered-component profile and header carrying challenge context remain to be specified.

### 8.4 Decision and retry

The presentation endpoint returns a decision. On success it may include a short-lived sender-constrained clearance artifact. The agent retries the protected request with that artifact and a request proof.

The candidate authorization scheme name and artifact syntax are deliberately unset pending review of HTTP authentication semantics and existing registrations.

## 9. Evidence profile requirements

Every evidence profile must specify:

- identifier and versioning policy;
- semantic claims and subject meaning;
- encoding and size limits;
- issuer or key discovery;
- validation algorithm and required inputs;
- audience, action, request, and presenter binding;
- freshness and expiration;
- replay and revocation behavior;
- normalized fact mapping;
- minimum-disclosure and correlation properties;
- errors and safe failure behavior;
- security and privacy considerations; and
- positive and negative test vectors.

A profile cannot require a commercial relationship with AgentIsOK merely to be technically implementable.

## 10. Versioning and extensibility

Protocol objects carry a major/minor version during experimentation. A future specification should define capability negotiation and critical-extension processing using established Internet patterns.

Implementations MUST NOT silently reinterpret unknown fields. Extension points must say whether unknown values are ignored, preserved, or rejected.

Identifiers should be decentralized where possible. Any common registry must follow [the project governance policy](../GOVERNANCE.md).

## 11. Privacy considerations

- Challenges reveal origin policy and may fingerprint routes; disclose only necessary requirements.
- Stable presenter keys can correlate activity; profiles should support origin-specific keys or pseudonyms where feasible.
- Issuers should not learn destinations unless necessary.
- Origins should not receive civil identity when an attribute or scoped pseudonym suffices.
- Natural-language tasks should not enter protocol messages or default logs.
- Diagnostic reasons must not expose private claims.
- Outcome sharing is a separate consented action, not an automatic consequence of clearance.

## 12. Security considerations

Implementers must address the complete [threat model](../THREAT-MODEL.md), particularly replay, concurrent redemption, signature coverage, intermediary transformations, key substitution, revocation, delegation attenuation, obligation enforcement, parser differentials, resource exhaustion, and fail-open behavior.

A valid signature proves control of a key over covered data. It does not prove that the signer is benign, the issuer is honest, the principal's intent is current, or the action is permitted.

## 13. Interoperability and anti-capture requirements

Before the protocol is described as mature, the project should demonstrate:

- two independent origin/verifier implementations;
- two independent agent/harness implementations or responders;
- two materially different evidence profiles;
- public positive and negative conformance vectors;
- operation with no AgentIsOK-hosted dependency; and
- documented switching between compatible providers.

No normative step may depend on an AgentIsOK account, API key, proprietary allowlist, private conformance server, or exclusive registry.

## 14. Open issues

1. Final protocol name and identifier namespace.
2. Correct HTTP status, authentication framework, headers, and media types.
3. Discovery and downgrade-resistant version negotiation.
4. Exact request canonicalization and intermediary profile.
5. Challenge state: server-side, self-contained, or both.
6. Detached presentation versus signed retry tradeoffs.
7. Clearance artifact format and sender constraint.
8. Boolean evidence requirements and selective disclosure negotiation.
9. Obligation registry and composition semantics.
10. Pairwise key and identifier mechanisms.
11. Distributed replay-state guarantees.
12. Privacy-preserving per-principal rate limits.
13. Revocation freshness by action risk.
14. Error disclosure and recourse semantics.
15. Migration path to a vendor-neutral standards registry.

## 15. References

- [RFC 9421: HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
- [RFC 9530: Digest Fields](https://www.rfc-editor.org/rfc/rfc9530)
- [RFC 9449: OAuth 2.0 Demonstrating Proof of Possession](https://www.rfc-editor.org/rfc/rfc9449)
- [RFC 9396: OAuth 2.0 Rich Authorization Requests](https://www.rfc-editor.org/rfc/rfc9396)
- [RFC 8693: OAuth 2.0 Token Exchange](https://www.rfc-editor.org/rfc/rfc8693)
- [RFC 9576: The Privacy Pass Architecture](https://www.rfc-editor.org/rfc/rfc9576)
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
