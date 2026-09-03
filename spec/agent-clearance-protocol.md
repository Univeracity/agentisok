# Agent Clearance Protocol

- **Working name:** Agent Clearance Protocol
- **Draft:** `00`
- **Protocol version in examples:** `0.1`
- **Status:** Exploratory skeleton with a candidate HTTP binding and two evidence profiles; incomplete and not suitable for production

Do not abbreviate the protocol as “ACP.” That short name is already used by unrelated agent protocols. Use **Agent Clearance Protocol**, or the token `agent-clearance`, in technical identifiers.

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
7. Express enforceable obligations, with unknown *critical* obligations failing closed.
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

**Origin:** The relying HTTP origin controlling the protected resource and final policy. In this draft an origin is an `https` scheme, host, and optional port with no userinfo, path, query, or fragment.

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

The candidate HTTP mapping for this state machine is in [Section 8](#8-candidate-http-binding). In short:

1. The agent makes the protected request.
2. The origin returns `401` with a challenge.
3. The agent POSTs a presentation to the origin's single presentation endpoint.
4. The origin returns a decision and may issue a sender-constrained artifact.
5. The agent retries the protected request with that artifact.

The presentation HTTP request carries the proof. The presentation JSON object does not contain a second signature.

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
- `presentation_endpoint` — the origin's single HTTPS endpoint for presentations.

`presentation_endpoint` MUST be on the same origin as `origin`, MUST use HTTPS, and MUST match the discovery document when discovery is used. Origins MUST NOT mint a distinct presentation URL per challenge.

The origin MUST NOT issue a challenge whose `expires_at` is earlier than or equal to `created_at`. The verifier MUST reject a challenge outside its validity window.

The challenge SHOULD request the minimum evidence needed for the action. A natural-language task description SHOULD NOT be required when a structured action, limit, or commitment is sufficient.

### 6.2 Request binding

The request binding identifies the attempted operation:

- uppercase HTTP method;
- absolute target URI;
- structured action type;
- optional resource and constraints; and
- content digest for any representation whose content affects authorization.

The **request-binding digest** is `sha-256=:base64digest:` over the UTF-8 JSON object containing `method`, `target_uri`, `action`, and `content_digest` when present. Object keys are serialized in lexicographic order, JSON objects use no insignificant whitespace, and Unicode is unescaped except for the characters JSON must escape. This is a prototype canonicalization. A later draft should adopt [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) unless interoperability testing shows a reason not to.

Profiles MUST define how redirects, query normalization, intermediary rewriting, retries, and bodies are handled. Origins MUST reject ambiguous bindings.

### 6.3 Evidence requirement

Each requirement includes:

- an origin-local `id` referenced by the response;
- a semantic `class`;
- one or more acceptable versioned `profiles`;
- whether the requirement is mandatory;
- maximum acceptable evidence age where applicable; and
- explicitly requested disclosures.

Requirement `id` values MUST be unique within a challenge.

The initial classes are provisional:

- `request_integrity`;
- `principal`;
- `delegation`;
- `human_presence`;
- `workload`;
- `operator`; and
- `rate_accountability`.

These classes describe evidence purpose, not assurance level. The protocol does not define a single assurance ladder in draft `00`.

Draft `0.1` profiles:

| Class | Profile | Document |
|---|---|---|
| `request_integrity` | `urn:agent-clearance:profile:http-message-signatures:rfc9421:0.1` | [http-message-signatures.md](profiles/http-message-signatures.md) |
| `request_integrity` | `urn:agent-clearance:profile:web-bot-auth:0.1` | [web-bot-auth.md](profiles/web-bot-auth.md) |
| `delegation` | `urn:agent-clearance:profile:origin-scoped-mandate:0.1` | [origin-scoped-mandate.md](profiles/origin-scoped-mandate.md) |

An origin MAY accept more than one profile for a class. The agent selects one.

### 6.4 Presentation

A presentation contains:

- `protocol_version`;
- `response_id`;
- `challenge_id`;
- `created_at`;
- a request-binding digest;
- presenter key and proof profile; and
- one evidence envelope per satisfied requirement.

It does **not** contain an embedded proof field. The HTTP request that carries the presentation is signed according to the selected `request_integrity` profile, which in the candidate binding is HTTP Message Signatures.

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

Consistency rules:

- `allow` MUST NOT include obligations.
- `allow_with_obligations` MUST include at least one obligation.
- `step_up` MUST include a `continuation_uri` or a replacement challenge.
- `deny` and `indeterminate` MUST NOT include a clearance artifact that would grant access.

Reason codes SHOULD be stable and coarse enough not to expose private evidence or sensitive fraud logic. Detailed diagnostic records belong in appropriately protected origin logs. A starter list is in [vocabulary/reason-codes.md](vocabulary/reason-codes.md).

### 6.7 Obligations

An obligation contains a versioned `type`, a `critical` flag, and profile-defined parameters.

`critical` defaults to `true`. If an enforcement point cannot interpret and enforce a critical obligation, it MUST reject or narrow the request. If it cannot enforce a non-critical obligation, it MUST ignore that obligation and MUST NOT treat the remainder as a broader permission than the enforceable subset allows.

Draft `0.1` core obligation types are critical by default:

- `urn:agent-clearance:obligation:rate-limit:0.1`
- `urn:agent-clearance:obligation:maximum-results:0.1`
- `urn:agent-clearance:obligation:one-time:0.1`
- `urn:agent-clearance:obligation:action-restriction:0.1`
- `urn:agent-clearance:obligation:step-up-before:0.1`

See [vocabulary/obligations.md](vocabulary/obligations.md). Origins that emit types outside this core SHOULD mark them `critical` unless a partial enforcement point can safely ignore them. The core exists so a first middleware implementation can interoperate; it is not a complete obligation language.

### 6.8 Clearance artifact

An optional clearance artifact MUST be:

- issued by or for the origin;
- short-lived;
- scoped to an exact request or explicit action class;
- sender-constrained to the presenter's key;
- protected against replay as appropriate;
- revocable or tightly time-bounded; and
- unusable as a cross-origin trust badge.

The prototype format is an origin-signed JSON object transported as the `value` of the decision's `clearance_artifact`. The retry MUST prove possession of `key_confirmation` using the HTTP Message Signatures profile.

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

1. Verifies the challenge origin, expiry, presentation endpoint, and intended action.
2. Rejects unsupported, excessive, or unauthorized disclosure requirements.
3. Selects one acceptable profile for each required evidence class.
4. Obtains current approval or evidence when necessary.
5. Builds a presentation bound to the challenge and request.
6. POSTs the presentation to `presentation_endpoint` using a key that is also bound to sender-constrained evidence where required.

The agent SHOULD make requested disclosures inspectable to the represented principal when practical.

### 7.3 Verification order

Implementations SHOULD perform inexpensive structural and freshness checks before expensive cryptographic or network operations.

The verifier:

1. Parses with strict size, depth, duplicate-key, and count limits.
2. Validates protocol version and critical fields.
3. Validates challenge state, origin, nonce, and expiry.
4. Reconstructs and compares the request binding.
5. Verifies the presentation HTTP signature and proof-of-possession relationships.
6. Validates each evidence profile, issuer trust, and revocation state.
7. Emits facts with provenance and warnings.
8. Marks one-time state atomically before or with enforcement where needed.

Unknown critical fields or requirement semantics MUST cause safe rejection for this draft.

The draft `0.1` presentation body limit is 65,536 bytes. Duplicate requirement identifiers and evidence envelopes not requested by the challenge are rejected; they are not collapsed, ignored, or copied into logs.

### 7.4 Policy and enforcement

The origin combines verified facts with local context. An AgentIsOK implementation MUST NOT replace an origin's policy with an issuer or vendor-global verdict.

The enforcement point verifies that the decision matches the current request digest and policy context, applies all critical obligations, and prevents duplicate action execution.

### 7.5 Step-up

`step_up` returns a continuation URI or a new challenge whose additional requirement is explicit. Approval UI MUST identify the origin, action, resource, quantity or value bounds, expiration, and agent or harness where applicable.

### 7.6 Indeterminate handling

Origins define risk-tiered behavior for `indeterminate`. A failure MUST NOT be converted to `allow` merely for availability. An origin MAY offer an ordinary human path, a narrower action, or a later retry.

## 8. Candidate HTTP binding

This section is the prototype binding. Names are unregistered. It exists so a first implementation can be written without inventing a second private protocol.

The prototype uses **detached presentation** rather than attaching rich evidence to the original request. That costs extra round trips compared with Web Bot Auth. It is the correct cost for a CAPTCHA-shaped challenge that carries a mandate. Web Bot Auth remains a request-integrity profile, not a substitute for this exchange.

Do not mix this binding with a second JSON-embedded presentation signature. Parser differentials follow immediately.

### 8.1 Discovery

A prototype MAY expose an HTTPS configuration resource at:

```text
/.well-known/agent-clearance
```

The path is not registered. Production standardization would require the applicable IANA and HTTP review.

The resource advertises protocol versions, the presentation endpoint, supported evidence profiles, HTTP signature algorithms, and size limits. Fetches require TLS. Responses may be cached with conservative `max-age`, but challenge objects themselves are not cacheable.

See [schema/discovery.schema.json](schema/discovery.schema.json).

### 8.2 Challenge response

When an otherwise protected request requires clearance, the origin returns `401 Unauthorized` with:

- `WWW-Authenticate: AgentClearance` carrying at least `challenge_id` and `profile`;
- `Content-Type: application/agent-clearance-challenge+json`;
- `Cache-Control: no-store`; and
- the challenge object as the JSON body.

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: AgentClearance profile="agent-clearance-0.1", challenge_id="urn:uuid:0d191f2f-73ae-4d41-b662-e1f45a968762"
Content-Type: application/agent-clearance-challenge+json
Cache-Control: no-store

{ ...challenge... }
```

`401` is used because this is an authentication-shaped challenge, not an application authorization failure. Origins SHOULD still provide an ordinary human or application-auth path. That path MAY be another `WWW-Authenticate` challenge, an HTML body for browsers, or both.

`403 Forbidden` is reserved for an affirmative `deny` after evaluation, not for issuing the initial challenge.

The media type and scheme name are provisional and unregistered.

### 8.3 Presentation endpoint

The agent POSTs the presentation JSON to `presentation_endpoint`. The HTTP request is signed using the HTTP Message Signatures profile and covers at least:

- `@method`;
- `@authority`;
- `@path`;
- `@query` when the presentation URL has a query;
- `content-digest`;
- `content-type`;
- `created` and `expires`;
- `keyid`;
- `alg`;
- `nonce` equal to the challenge nonce; and
- `tag="agent-clearance"`.

The presentation body is the JSON object in [Section 6.4](#64-presentation). It does not repeat the HTTP signature.

The origin MUST reject a presentation POST that is not signed under an accepted `request_integrity` profile, even if embedded evidence looks valid.

### 8.4 Decision and retry

The presentation endpoint returns `200` with `Content-Type: application/agent-clearance-decision+json` on a completed evaluation, including `deny` and `indeterminate`. Transport success is not application success.

On `allow` or `allow_with_obligations` the origin MAY include a short-lived sender-constrained clearance artifact. The agent retries the protected request with:

```http
Authorization: AgentClearance artifact="<artifact-value>"
```

and an HTTP Message Signature proving possession of the confirmed presenter key, covering the original protected request's method, authority, path, query if present, and content digest if the body affects authorization.

Malformed presentations return `400`. Unauthenticated presentation POSTs return `401`. The origin MUST NOT perform the protected application action as a side effect of handling a presentation.

### 8.5 Why this shape

| Choice | Reason |
|---|---|
| `401` + `WWW-Authenticate` | HTTP authentication challenge, composable with a human path |
| Challenge in the body | Challenge objects are too large and structured for a header |
| Single presentation endpoint | Avoids per-challenge URL state, open redirects, and cache confusion |
| Detached presentation | Mandates and selective disclosure do not belong in the original request body |
| RFC 9421 on the presentation POST | One proof layer; no nested JSON signature |
| Artifact on retry | Keeps verification off the application action path |

Exact request canonicalization through CDNs remains an open issue. The first profile therefore covers a conservative component set and treats rewritten queries, redirected hosts, and unsigned bodies as out of scope for `0.1`.

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
- Presented key identifiers MUST NOT include the relying origin as a correlatable join key.
- Issuers should not learn destinations unless necessary. The `0.1` mandate issuer is the origin, which avoids a third-party destination dossier.
- Origins should not receive civil identity when an attribute or scoped pseudonym suffices.
- Natural-language tasks should not enter protocol messages or default logs.
- Diagnostic reasons must not expose private claims.
- Outcome sharing is a separate consented action, not an automatic consequence of clearance.
- A TLS-terminating CDN or reverse proxy sees the presentation in plaintext. Draft `0.1` is scoped disclosure to the origin (and whoever terminates HTTPS), not unlinkability from the edge.

Boolean evidence negotiation without fingerprinting remains unsolved. Listing acceptable issuers in a challenge can leak policy. The `0.1` profiles accept that leak for a first origin-scoped mandate and treat a Privacy Pass-style rate proof as future work rather than a fake solution.

## 12. Security considerations

Implementers must address the complete [threat model](../THREAT-MODEL.md), particularly replay, concurrent redemption, signature coverage, intermediary transformations, key substitution, revocation, delegation attenuation, obligation enforcement, parser differentials, resource exhaustion, and fail-open behavior.

A valid signature proves control of a key over covered data. It does not prove that the signer is benign, the issuer is honest, the principal's intent is current, or the action is permitted.

The prototype replay store is origin-local and single-node. Distributed edge replay is a centralization risk if it requires a hosted nonce service. That store is an observation MITM for presenter/origin/time even when signatures verify locally. Deployments MUST document their consistency model before using one-time proofs at more than one enforcement point.

A deployment is origin-authoritative only if the origin can verify the same presentation bytes with its own keys and policy. An edge that verifies and forwards a header, or a vendor API that classifies the agent, is a hosted verifier. Edge MAY enforce. It MUST NOT be the only party that saw the proof.

## 13. Interoperability and anti-capture requirements

Before the protocol is described as mature, the project should demonstrate:

- two independent origin/verifier implementations;
- two independent agent/harness implementations or responders;
- two materially different evidence profiles;
- public positive and negative conformance vectors;
- operation with no AgentIsOK-hosted dependency; and
- documented switching between compatible providers.

No normative step may depend on an AgentIsOK account, API key, proprietary allowlist, private conformance server, or exclusive registry.

This repository contains one reference verifier/responder and two evidence profiles. That is not protocol maturity.

## 14. Open issues

Decided for the `0.1` prototype, still unregistered and reversible:

1. Candidate HTTP status is `401` with `WWW-Authenticate` and a JSON challenge body.
2. Proof is the presentation request's HTTP Message Signature, not a second JSON signature.
3. Presentation URLs are origin-global, not per-challenge.
4. Core obligations are critical by default; unknown critical obligations fail closed.
5. The protocol is not abbreviated ACP.

Still open:

1. Final protocol name and identifier namespace.
2. IANA registration of scheme, headers, media types, and well-known path.
3. Discovery and downgrade-resistant version negotiation.
4. Exact request canonicalization and intermediary profile.
5. Challenge state: server-side, self-contained, or both.
6. Clearance artifact format beyond the prototype JSON object.
7. Boolean evidence requirements and selective disclosure negotiation.
8. Obligation registry beyond the core five types.
9. Pairwise key and identifier mechanisms.
10. Distributed replay-state guarantees.
11. Privacy-preserving per-principal rate limits.
12. Revocation freshness by action risk.
13. Error disclosure and recourse semantics.
14. Migration path to a vendor-neutral standards registry.

## 15. References

- [RFC 9421: HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
- [RFC 9530: Digest Fields](https://www.rfc-editor.org/rfc/rfc9530)
- [RFC 8785: JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785)
- [RFC 9449: OAuth 2.0 Demonstrating Proof of Possession](https://www.rfc-editor.org/rfc/rfc9449)
- [RFC 9396: OAuth 2.0 Rich Authorization Requests](https://www.rfc-editor.org/rfc/rfc9396)
- [RFC 8693: OAuth 2.0 Token Exchange](https://www.rfc-editor.org/rfc/rfc8693)
- [RFC 9576: The Privacy Pass Architecture](https://www.rfc-editor.org/rfc/rfc9576)
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
