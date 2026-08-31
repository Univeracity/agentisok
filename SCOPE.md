# AgentIsOK Scope

## Purpose

AgentIsOK is an open challenge and clearance layer for automated agents encountering an origin's anti-automation or risk boundary. It helps the origin request, verify, and evaluate bounded evidence for a specific action.

The protocol is intended to sit before or alongside ordinary application authentication and authorization. It does not grant an agent the represented principal's complete authority.

## In scope

- Origin advertisement and discovery of agent-clearance support.
- Origin-issued, request-bound challenges.
- Negotiation of acceptable evidence classes and profiles.
- Agent or workload proof of possession.
- Evidence of a person, organization, account, operator, or other principal where policy requires it.
- Scoped delegation or mandate evidence.
- Binding proofs to origin, action, request, nonce, and time.
- Normalized facts with preserved issuer and proof provenance.
- Origin-controlled policy evaluation.
- Typed decisions and enforceable obligations.
- Human or organizational step-up.
- Replay prevention, expiration, revocation, and key rotation.
- Privacy-preserving identifiers and rate limits.
- Short-lived origin clearance artifacts.
- Local, hosted, and federated deployment profiles.
- Interoperability, conformance, and adversarial testing.
- Transparent qualification metadata for optional evidence ecosystems.

## Out of scope

AgentIsOK is not initially:

- a CAPTCHA-breaking or challenge-circumvention tool;
- a universal identity provider;
- proof that an agent is universally safe;
- a global agent or human reputation score;
- a mandatory biometric or proof-of-personhood system;
- a wallet or payment authorization protocol;
- a replacement for OAuth, account authorization, or business policy;
- a general-purpose agent runtime;
- a behavioral alignment certification system;
- a centralized history of agent activity;
- a mandatory issuer directory or global allowlist; or
- an AgentIsOK-controlled gateway that every request must traverse.

## Clearance boundary

Clearance answers whether a request may cross an anti-automation or preliminary risk boundary. The application may still require additional controls.

| Layer | Example question | AgentIsOK responsibility |
|---|---|---|
| Request integrity | Did this key sign this exact request? | Verify or adapt evidence |
| Principal backing | Is this agent associated with an acceptable principal? | Verify requested evidence |
| Delegation | Does the mandate include this action? | Verify and normalize scope |
| Clearance policy | Is this evidence enough to proceed here? | Enable origin-controlled decision |
| Account authorization | Can this account access this record? | Existing application control |
| Transaction authority | May funds be committed? | Separate explicit authorization |
| Abuse/business policy | Is the rate, inventory use, or behavior acceptable? | Origin policy and obligations |

## Supported principals

The data model must not assume that every legitimate agent maps directly to a civilly identified person. Depending on origin policy, acceptable principals may include:

- a person using an agent;
- an organization delegating to an enterprise agent;
- an account holder represented by a service;
- a service workload or operator;
- an anonymous but rate-accountable principal; or
- an agent admitted on request integrity and bounded behavior alone.

The origin decides which evidence is necessary for the action.

## Initial risk envelope

The first implementation should focus on low-consequence, bot-sensitive actions where bounded automation has clear origin value, such as availability or inventory search.

It should demonstrate:

- `allow_with_obligations` for limited reads;
- replay-resistant request binding;
- more than one evidence profile;
- privacy-preserving logs;
- quota enforcement; and
- step-up before reservation, purchase, submission, or another consequential write.

High-impact actions may eventually use the same clearance rail, but only alongside domain-specific authority and policy.

## Compatibility posture

Identity, delegation, signed-agent, OAuth, privacy-token, and payment ecosystems may provide evidence to AgentIsOK. They are adapters or adjacent authorities, not automatically replaced by the protocol.

The protocol should define a stable origin integration surface while allowing evidence profiles to evolve independently.

## Maturity boundary

The initial specification is an exploratory skeleton. It is not production-ready and does not yet define a registered HTTP authentication scheme, media type, well-known URI, assurance taxonomy, issuer governance framework, or finalized wire format.

Those decisions require implementation experience, security review, and multi-party interoperability.
