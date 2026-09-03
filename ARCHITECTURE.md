# AgentIsOK Architecture

## Status

This document describes the intended architecture of an exploratory protocol. It is not a production specification or security guarantee.

## System objective

AgentIsOK provides a stable boundary between agents that can present heterogeneous evidence and origins that must make local, request-specific decisions.

```text
                         optional evidence services
                     +-------------------------------+
                     | issuers | revocation | metadata|
                     +-------------+-----------------+
                                   |
                                   v
+-----------+   protected    +-----------+   facts   +------------+
| agent and |---- request -->| verifier  |---------->| origin     |
| harness   |<-- challenge --| adapters  |           | policy     |
+-----------+                +-----------+           +-----+------+
      |                                                   |
      | request-bound proof                               | decision + obligations
      +---------------------------------------------------v
                                                    +------------+
                                                    | enforcement|
                                                    +-----+------+
                                                          |
                                                          v
                                                    application
```

The origin controls the verifier trust configuration, policy decision, and enforcement. External services can supply evidence and metadata but cannot force acceptance.

## Roles

### Principal

The person, organization, account, workload operator, or other authority represented in a request. The principal need not be civilly identified unless origin policy requires it.

### Agent

The software actor attempting an action. An agent identity may identify software, an operator, an instance, or a workload, depending on the evidence profile. These meanings must not be conflated.

### Harness

The execution environment that operates the agent, mediates credentials, and creates request-bound proofs. The harness should keep signing keys and bearer credentials outside untrusted model or prompt context.

### Origin

The relying service that owns the resource, challenges the request, selects acceptable evidence, and retains final policy authority.

### Issuer

A party that issues evidence about a principal, agent, harness, mandate, presence event, quota, or other attribute. Issuers are trusted only according to origin policy.

### Verifier

The origin-side component that validates evidence and emits normalized facts with provenance. Verification does not itself imply acceptance.

### Policy decision point

The origin-controlled component that combines verified facts with account, abuse, rate, inventory, business, and legal rules.

### Policy enforcement point

The component that enforces the decision and every obligation before the application performs the action.

## Trust boundaries

The architecture does not assume that:

- an agent is trustworthy because its software or operator is identified;
- a harness is uncompromised because it holds a valid key;
- a principal is benign because it is a real person or organization;
- a mandate includes an action merely because delegation exists;
- an issuer's claims are sufficient because their signatures validate;
- an origin configured its policy correctly;
- an AgentIsOK-hosted service is available or neutral; or
- a clearance result authorizes an application resource or transaction.

Every transition across a boundary requires explicit validation and policy.

## Logical components

### Capability advertisement

An origin needs a discoverable way to announce supported protocol versions, challenge profiles, evidence profiles, endpoints, and key material. The first implementation uses `/.well-known/agent-clearance` and issues challenges as `401 Unauthorized` with `WWW-Authenticate: AgentClearance` and a JSON body. Standardization would require formal registration and security review. DID resolution is not a prerequisite; prototype key identifiers are HTTPS URLs.

### Challenge issuer

The challenge issuer converts an attempted action and risk class into a short-lived evidence request. Challenges contain a nonce, audience, action and request binding, accepted evidence profiles, policy identifier, privacy constraints, and expiry.

### Agent responder

The responder selects compatible evidence, obtains step-up approval when needed, and binds the response to both the challenge and the protected request. It must not silently expand scope or disclose optional identity attributes without authorization.

### Evidence adapters

Adapters validate specific formats and translate them into a common fact envelope. The envelope retains evidence profile, issuer, audience, timestamps, proof binding, revocation method, and assurance context.

An adapter is a parser and verifier, not a source of universal trust.

### Replay and state service

Challenge nonces, one-time proofs, quota consumption, and redemption state require atomic handling. A single-node prototype may use a local store. Distributed deployments need a bounded consistency model that is documented and tested.

### Policy engine

The engine accepts facts and origin-local context and emits one typed decision:

- `allow`;
- `allow_with_obligations`;
- `step_up`;
- `deny`; or
- `indeterminate`.

Unknown critical obligations fail closed. Policy language is deliberately not standardized in the initial protocol. The input and output contracts are the interoperability boundary.

### Enforcement adapter

The adapter maps obligations into concrete controls such as rate buckets, result limits, route restrictions, transaction ceilings, or required approvals. If an obligation is unsupported, the request cannot receive the broader permission.

### Audit and recourse record

An origin may store a minimized record of the challenge, evidence digests, decision, policy version, obligations, and enforcement result. Natural-language task content and cross-origin identifiers should not be logged by default.

## Data model

### Challenge

A challenge describes:

- which origin and action are in scope;
- which request is being challenged;
- which evidence classes and profiles are acceptable;
- how fresh the evidence must be;
- whether current principal interaction is required;
- what privacy constraints apply;
- when the challenge expires; and
- where the response is presented.

### Evidence envelope

An evidence envelope carries or references a proof and describes its profile. Embedded claims remain profile-specific. The verifier emits normalized facts instead of requiring the protocol core to understand every credential format.

### Normalized fact

A fact contains:

- a typed claim;
- a value or commitment;
- subject semantics;
- issuer and trust path;
- audience and action binding;
- issuance and expiration;
- presenting-key binding;
- revocation status;
- evidence digest; and
- validation result or warning.

### Decision

A decision binds its value and obligations to the challenge, request digest, policy version, and time. Optional reasons use stable machine codes and must avoid disclosing sensitive fraud logic.

### Clearance artifact

An origin may issue a short-lived sender-constrained artifact to avoid repeating verification for an identical bounded action class. It is origin-local and cannot be used as a portable AgentIsOK badge.

## Exchange sequence

```text
Agent                  Origin/Verifier             Issuers/Metadata
  |                           |                           |
  | protected request         |                           |
  |-------------------------->|                           |
  | 401 + challenge           |                           |
  |<--------------------------|                           |
  |                           |                           |
  | obtain/select evidence    |                           |
  |------------------------------------------------------>|
  |<------------------------------------------------------|
  |                           |                           |
  | POST presentation         |                           |
  | (HTTP Message Signature)  |                           |
  |-------------------------->| verify/revocation ------>|
  |                           |<--------------------------|
  | decision + artifact       |                           |
  |<--------------------------|                           |
  | signed retry + artifact   |                           |
  |-------------------------->| enforce obligations       |
  | application response      |                           |
  |<--------------------------|                           |
```

The presentation HTTP request is the proof. The presentation JSON does not contain a second signature. The presentation URL is an origin-global endpoint, not a per-challenge URL.

Step-up is a new, narrower challenge. It must not be an unstructured instruction to “ask the human.”

## Deployment modes

### Fully local

The origin hosts verification, policy, replay state, and metadata. Issuer keys and revocation data may be cached under bounded freshness rules. This mode minimizes dependency and observation by third parties.

### Managed control plane, local data plane

A provider distributes policy, adapter, and issuer metadata updates while requests and evidence are evaluated at the origin or edge. This is the preferred hosted model because the provider need not observe every task.

### Hosted verifier

The origin sends minimized evidence to a hosted verifier and receives facts, then applies local policy. This can simplify adoption but increases confidentiality, availability, and capture risk. It must remain optional and replaceable.

Calling a vendor API to classify an agent, or accepting an edge header as the only proof, is this mode even when it is branded as “local.”

### Federated evidence ecosystem

Origins select multiple issuers or qualification sources under local policy. Federation cannot become an implicit global allowlist. Trust lists need transparent provenance and practical override.

## Standards composition

The intended building blocks include:

- [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421) HTTP Message Signatures for request integrity;
- [RFC 9530](https://www.rfc-editor.org/rfc/rfc9530) Digest Fields for content binding;
- [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449) DPoP where OAuth sender-constrained tokens are appropriate;
- [RFC 9396](https://www.rfc-editor.org/rfc/rfc9396) Rich Authorization Requests for structured authority;
- [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693) OAuth Token Exchange where delegated token exchange is appropriate;
- [RFC 9576](https://www.rfc-editor.org/rfc/rfc9576) Privacy Pass architecture as a role-separation and privacy precedent;
- [Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/) when issuer-holder-verifier credentials add value; and
- Web Bot Auth as an optional request-integrity adapter, never as proof of a principal's mandate.

Use of a building block is profile-specific. The core protocol must not imply that all deployments use OAuth, verifiable credentials, or proof of personhood.

## Origin-authoritative verification

Two different middlebox failures have to stay distinct.

**Trust MITM.** An intermediary verifies the agent and tells the origin that the request is fine. The origin never sees a proof it can check.

**Observation MITM.** An intermediary sees destinations, timing, pairwise identifiers, mandates, and outcomes. Even without a global subject identifier, the traffic graph is the identifier.

AgentIsOK is origin-authoritative only when the origin can verify the same presentation bytes with its own keys and policy after any edge. Edge and reverse-proxy components MAY enforce obligations. They MUST NOT be the only party that saw the proof and the only party that can reproduce the decision.

“Origin-local” means the origin’s verifier, not “somewhere in front of the origin.” A TLS-terminating CDN still sees the presentation in plaintext. Draft `0.1` therefore gives the origin scoped disclosure, not unlinkability from the origin’s edge.

A multi-point replay or rate store is an observation surface. If one-time nonces are implemented as a vendor session service, that deployment is a hosted data plane for those facts, even when signatures verify locally.

Presented key identifiers MUST NOT include the relying origin as a correlatable join key. Internal pairwise isolation may still be per-origin; the identifier on the wire should be opaque.

A deployment that only works as a CDN product checkbox does not satisfy this section, however convenient it is.

## Anti-centralization architecture

Preventing gatekeeper concentration requires technical properties, not only governance promises:

- no protocol-critical call to an AgentIsOK domain;
- no global AgentIsOK identifier;
- no required proprietary directory;
- origin-controlled issuer trust;
- origin reconstruction of the decision from the same presentation bytes, so an edge verdict is never the sole proof;
- cached and offline-bounded metadata paths;
- portable policy and configuration formats where feasible;
- open schemas and conformance vectors;
- protocol version negotiation without vendor lock-in;
- multiple discovery and deployment operators; and
- receipts and logs that can be verified without the founding service.

Commercial services may provide convenience, support, intelligence, or managed operation. Conformance cannot depend on buying them.

## Relationship to adjacent systems

AgentIsOK can authorize a bounded external action or transfer. Artifact portability, provenance, and reuse systems may then represent the result. Infrastructure projects may provide portable deployment substrates. These integrations should use explicit interfaces and must not create a shared global identity or activity graph.

## Implementation sequence

1. Candidate HTTP binding, two evidence profiles, and a reference loop (this repository).
2. Origin-side discovery of real blocked or challenged agent workflows.
3. A shadow evaluation with a qualified origin: existing controls still decide, AgentIsOK decisions are compared, and the origin can reconstruct the proof without an edge verdict.
4. A second independent verifier and responder.
5. Interoperability events and refinement from observed failures.
6. Only then: the smallest profile or extension in an established standards venue.
