# AgentIsOK Principles

These principles are constraints on the protocol, implementations, governance, and business model. A convenient implementation that violates them is not the intended system.

## 1. The receiving service decides

Issuers and verifiers can establish that evidence is authentic, current, and bound to a request. They cannot decide that an origin must accept it. The receiving service remains the final policy authority.

> Evidence may travel; authority does not.

## 2. “OK” is contextual

Clearance is a function of evidence, principal, mandate, action, request, origin policy, time, and revocation state. It is not a permanent property of an agent.

An `AI OK` result means only:

> The origin found the supplied evidence sufficient for this action under its current policy.

It does not certify that an agent is generally safe, correct, aligned, beneficial, or authorized for another action.

## 3. Trust is a vector, not a score

Agent identity, operator identity, human or organizational backing, delegation, request integrity, current intent, reputation, rate limits, and transactional authority are separate dimensions. Evidence at one layer does not silently grant authority at another.

The protocol must preserve this structure rather than emit an opaque universal trust score.

## 4. Authentication, clearance, and application authorization are distinct

Clearance can permit a request to enter an application's ordinary access path. It does not automatically replace account authentication, resource authorization, business rules, fraud controls, or approval for consequential actions.

Payment, legal agreement, healthcare consent, physical control, and other high-impact authorities require their own explicit scope and policy.

## 5. No mandatory gatekeeper

No conforming origin or agent should be required to use one vendor, registry, directory, issuer, control plane, or hosted verifier. An edge that is the only party able to verify a presentation is a hosted verifier, whatever hostname appears on the wire.

The standard must support:

- local and self-hosted verification;
- multiple independently operated issuers;
- competing agent and origin implementations;
- origin-controlled trust configuration;
- exportable configuration and practical provider exit;
- public conformance tests; and
- interoperable operation without an AgentIsOK account.

Any registry needed for interoperability must use transparent, reviewable, nondiscriminatory rules. Inclusion cannot be conditioned on purchasing unrelated services.

This requirement exists specifically to prevent monopoly or duopoly control over agent access to the web.

## 6. Disclose the minimum

An agent's destination, task, timing, repetition, and requested authority can reveal intimate or commercially sensitive activity. Challenges must request only the facts needed for the action.

Prefer structured action classes, commitments, pairwise identifiers, and scoped quota proofs over civil identity, global identifiers, or natural-language task descriptions.

## 7. Linkability is scoped and explicit

Fraud controls sometimes need continuity while users need privacy. The design should not resolve this tension with a hidden global identifier.

Where continuity is justified, use an explicit origin-specific pseudonym, mandate identifier, or privacy-preserving rate bucket. Cross-origin correlation must not be a default side effect.

## 8. Verification preserves provenance

Normalized facts must retain their issuer, evidence type, audience, freshness, proof binding, revocation method, and assurance context. Cryptographic validity alone does not make a claim true or sufficient.

The origin evaluates both the fact and why it should trust that fact.

## 9. Bind evidence to the request

Proofs must be short-lived and bound to the intended origin, action, method, target, content, nonce, and presenting key as appropriate. A valid proof for one request must not be reusable at another origin or for a broader action.

## 10. Failure is typed and safe

An explicit denial, insufficient evidence, malformed input, policy error, and unavailable dependency are different events. Implementations must preserve those distinctions while preventing unsafe fallback.

## 11. Obligations are enforceable

`allow_with_obligations` is authorization only when a policy enforcement point can apply every *critical* rate, quantity, scope, logging, or step-up constraint. Unknown critical obligations fail closed. Failure to enforce a required obligation must stop or narrow the action.

## 12. Compose established standards

AgentIsOK should define the smallest missing challenge, evidence-negotiation, decision, and conformance layer. It should reuse established cryptography, HTTP semantics, OAuth profiles, and credential systems instead of creating parallel primitives.

## 13. Open implementation is proven, not promised

Publication of source code alone does not prevent capture. Protocol maturity requires independent implementations, public test vectors, documented interoperability, open governance, and the ability to operate without the founding project's infrastructure.

## 14. Safety arguments remain defeasible

Delegations expire, keys are compromised, issuers fail, policies change, and seemingly legitimate actors abuse systems. “OK” must remain a living and revocable argument about a request, not a timeless certificate.

## 15. Recourse is part of the system

Origins, issuers, operators, agents, and represented principals need paths to correct errors, revoke authority, investigate abuse, and appeal ecosystem-level qualification decisions. Cryptographic correctness does not eliminate governance responsibilities.
