# AgentIsOK

## An Open, Request-Bound Clearance Layer for Authorized Agents

- **Draft:** 0.1
- **Date:** August 31, 2026
- **Revised:** September 4, 2026
- **Authors:** AgentIsOK contributors
- **Status:** Public working paper; not a production specification or security assessment

## Abstract

The web's anti-automation boundary was designed around a simplifying assumption: desirable visitors are human, while automated visitors are suspicious. Software agents acting for people and organizations invalidate that assumption. They need a legitimate way to browse, search, schedule, submit, reserve, and transact without pretending to be human, inheriting unrestricted user credentials, or bypassing an origin's policy.

AgentIsOK proposes an open challenge and clearance layer for that boundary. An origin requests bounded evidence about an agent, the principal it represents, its mandate, and the exact action. The agent returns only the evidence required. Verification produces provenance-preserving facts. The origin combines those facts with its own account, risk, rate, inventory, and business policy, then returns a request-specific decision.

The proposal is deliberately not a universal agent identity, safety badge, or global trust score. It is also deliberately not a mandatory hosted gate. Any origin must be able to verify locally, select its own issuers, and use competing implementations. Preventing monopoly or duopoly control over agent gatekeeping is a protocol and governance requirement, not merely an open-source aspiration.

The intended result is a machine-verifiable alternative to CAPTCHA for authorized agents:

> AgentIsOK verifies and composes evidence. The receiving service decides what is OK.

## 1. The boundary problem

CAPTCHA and bot-management systems protect real interests: availability, inventory, privacy, security, fair access, fraud reduction, and infrastructure capacity. An agent should not evade those controls merely because a person instructed it.

At the same time, a human challenge is a poor interface for software legitimately acting for a principal. Requiring the software to masquerade as a human makes accountability worse. Giving it the human's complete session or credentials expands the compromise radius. Creating a bespoke API and bilateral identity integration for every service does not cover the open web and does not scale across agents and origins.

The missing capability can be stated narrowly:

```text
When an origin would otherwise challenge or block an automated request,
let it ask for bounded evidence and make a locally enforceable,
request-specific decision without forcing a human CAPTCHA.
```

This is not “CAPTCHA bypass.” A bypass defeats the origin's policy. A clearance exchange gives an agent a machine-appropriate path to satisfy it.

## 2. The central design thesis

The name AgentIsOK is useful because it states the origin's question directly. It also reduces naturally:

```text
Agent Is OK -> A I OK -> AI OK
```

The friendly compression creates a necessary design responsibility. `AI OK` cannot mean that an AI system is generally safe, correct, aligned, or trustworthy. The defensible statement is contextual:

> AI OK for this action, on this origin, under this policy, at this time.

The decision can be modeled as:

```text
Clearance(
  agent evidence,
  principal evidence,
  mandate,
  action,
  request,
  origin policy,
  time,
  revocation state
) -> decision
```

It cannot be reduced safely to:

```text
trust_score(agent) -> universally_safe
```

The protocol therefore treats trust as a request-bound relationship among evidence, authority, policy, and time—not as an attribute possessed by an actor.

### 2.1 The testable claim

The product hypothesis is that, for an origin with desirable automation currently challenged or blocked, explicit delegation and request-bound limits add enough information to improve admission decisions at an acceptable abuse, privacy, and operating cost. A valid signature or a successful demo cannot establish that claim.

The first experiment should compare three policies on the same eligible workflow: the incumbent control, a simpler signed-agent rule with existing account/API authorization where available, and AgentIsOK's request-bound mandate policy. The incremental question is whether the mandate and obligations change useful decisions beyond recognition alone. If the simpler integration meets the origin's goals, a new exchange is unnecessary for that workflow.

Before collecting data, the origin chooses a minimum useful improvement, abuse guardrails, label sources, latency and engineering budgets, and stop conditions. Report label coverage, uncertainty, and the denominator for every rate. Principal-backed traffic is not automatically desirable traffic; outcome labels must have a basis independent of the evidence being evaluated.

Shadow mode estimates disagreements and hypothetical admission of labeled requests. Because existing controls still decide, it cannot establish recovered task completion, prevented abandonment, or abuse after a counterfactual admission. Missing outcomes for blocked requests remain unknown. Any later enforcement experiment needs its own origin approval, controls, and evaluation; shadow success alone is insufficient.

Three outcomes would reshape or stop this approach for the initial workflow: no additional benefit over the simpler baseline; delegation setup costing more than the recovered value; or reproducible origin verification requiring unacceptable disclosure or operational dependence. The [roadmap](ROADMAP.md) turns these questions into evidence gates, not feature-count milestones.

### 2.2 The mandate bootstrap

An origin must have a legitimate basis for issuing or trusting a mandate before the agent can present one. In draft `0.1`, issuance is origin-scoped: a hypothetical origin approval flow binds an existing principal relationship to the agent's key and explicit action limits. The reference uses public fixture keys and a fabricated approval record. It does not implement passkeys, account enrollment, an approval ceremony, key delivery, or proof of current human intent.

The pilot must identify who can issue the mandate, how the principal approves it, and what happens when no mandate or trusted issuer exists. This setup friction belongs in the experiment's cost. A mandate from an unfamiliar origin is not portable authority, and an agent cannot mint its own acceptable delegation merely by signing JSON.

## 3. Separate the trust dimensions

At least eight independent dimensions may affect a decision:

1. **Agent or workload identity:** What software, operator, or instance controls the presenting key?
2. **Principal backing:** Is the agent associated with a person, organization, account, or other acceptable authority?
3. **Delegation:** Did that principal grant authority to this agent or harness?
4. **Action scope:** Which resource, operation, quantity, value, duration, or delegation depth is included?
5. **Current intent:** Is the request consistent with a sufficiently recent instruction or approval?
6. **Request integrity:** Is the proof bound to the origin, method, target, content, nonce, presenter, and time?
7. **Origin policy:** Do rate, inventory, account, abuse, fraud, and business rules permit the request?
8. **Current state:** Has the mandate, key, issuer, account, or relevant observed outcome changed?

None automatically implies the others. Known software can lack authority. A verified principal can direct abuse. A valid delegation can exclude the requested action. A signed request can be replayed. A legitimate request can exceed an origin's rate or inventory policy.

This separation also protects higher-impact actions. Recognition does not imply account access. Account access does not imply permission to commit funds, sign an agreement, change healthcare data, or operate a physical system. Those authorities may reuse the clearance rail but require distinct scopes, approvals, and policies.

## 4. Clearance is not application authorization

AgentIsOK sits at an automation or preliminary risk boundary. It may permit a request to enter the origin's ordinary application path. It does not replace every control behind that path.

An origin might decide:

- this request is sufficiently accountable to perform a public availability search;
- it may return no more than 100 results;
- the pairwise principal may make 20 searches per hour;
- account authentication is still required for saved preferences; and
- current human approval and payment authorization are still required before booking.

This layered model limits both accidental authority transfer and developer overconfidence in an “OK” result.

## 5. Proposed protocol model

The protocol has five central objects.

### 5.1 Challenge

The origin describes the protected request, structured action, acceptable evidence profiles, disclosure requirements, policy version, nonce, and expiry.

The challenge is origin-generated because the origin owns the decision and knows the action's risk. It should ask for the minimum facts needed rather than demand a complete identity dossier.

### 5.2 Presentation

The agent or harness selects compatible evidence and POSTs a presentation to the origin's single presentation endpoint. The HTTP request is the proof (HTTP Message Signatures in the first profile). The presentation JSON does not contain a second signature. Where current approval is required, the principal approves a structured description of the origin, action, resource, limits, and expiry—not merely a vague natural-language task.

### 5.3 Normalized facts

Evidence adapters validate different formats and produce facts for local policy. Normalization preserves issuer, subject semantics, audience, freshness, proof-of-possession binding, revocation state, disclosure properties, and evidence digest.

Cryptographic verification shows that a proof is valid under a key and format. It does not establish that the issuer is honest or that the claim is sufficient. The Verifiable Credentials model makes the same verifier-side distinction: a verifier applies its own business rules after checking claims and proofs.[^vc]

### 5.4 Decision and obligations

The origin emits one decision:

- `allow`;
- `allow_with_obligations`;
- `step_up`;
- `deny`; or
- `indeterminate`.

`challenge` is a protocol state, not a decision. `indeterminate` separates an inability to evaluate safely from an affirmative judgment about an agent.

Obligations are structured and enforceable. Core draft types include rate limits, maximum results, action restrictions, one-time execution, and step-up before a later action. Unknown *critical* obligations fail closed. If an enforcement point cannot apply every required critical obligation, the broader permission is invalid.

### 5.5 Clearance artifact

An origin may issue a short-lived sender-constrained artifact to avoid repeating the same evidence exchange. The artifact remains origin-local, action-scoped, and bound to the presenter. It cannot become a transferable global trust badge.

## 6. Compose existing standards

The difficult part of AgentIsOK is not inventing a signature algorithm. Mature building blocks already address important portions of the problem:

- HTTP Message Signatures define signatures over selected HTTP message components and explicitly require applications to choose sufficient coverage and address replay.[^http-signatures]
- Digest Fields provide representation digests that can bind security decisions to message content.[^digest-fields]
- OAuth DPoP sender-constrains tokens to a key, reducing bearer-token replay risk.[^dpop]
- OAuth Rich Authorization Requests represent fine-grained authorization details instead of relying only on flat scope strings.[^rar]
- OAuth Token Exchange supports security-token exchange and delegation contexts.[^token-exchange]
- Privacy Pass separates clients, origins, issuers, and attesters and provides an architectural precedent for privacy-preserving challenge alternatives.[^privacy-pass]

AgentIsOK should profile these tools where appropriate and define the missing challenge negotiation, evidence composition, local decision, obligation, and conformance semantics.

No single credential format should be mandatory. OAuth-based, verifiable-credential, signed-agent, enterprise, passkey-backed, privacy-token, or future evidence systems can participate through versioned profiles. Origin integration remains stable while evidence ecosystems evolve.

## 7. Privacy by topology

An agent's destination, task, timing, repetition, and requested authority can reveal medical concerns, purchases, negotiations, research, travel, customers, or competitive strategy. A central clearance service that observes all of these facts would become a surveillance system and high-value breach target.

The architecture should minimize what each role can learn:

- Use origin-specific or pairwise principal and agent identifiers.
- Avoid civil identity when an attribute, commitment, or accountable pseudonym suffices.
- Avoid natural-language task descriptions when a structured action is sufficient.
- Prevent issuers from learning destinations where the evidence profile permits blind or pre-issued proofs.
- Let origins verify locally or at their own edge.
- Keep decision and outcome records local by default.
- Treat cross-origin outcome sharing as a separate, consented act.
- Make retention explicit and bounded.
- Do not treat a TLS-terminating CDN as the origin. Draft `0.1` discloses structured facts to whoever terminates HTTPS.
- Do not put the relying origin in presented key identifiers.

Fraud defense sometimes benefits from continuity while privacy benefits from unlinkability. The answer should be scoped linkability—for example, a stable pseudonym or rate bucket for one origin—not a concealed universal identifier.

Privacy Pass is particularly important as an architectural precedent because it separates issuance and redemption roles rather than making long-lived identity the default answer to abuse.[^privacy-pass] Draft `0.1` does not implement that split. Origin-issued mandates prevent a third-party issuer dossier; they do not make presentations unlinkable from the origin or its edge.

If an edge forwards only a verdict, the origin depends on the edge's judgment. A shared nonce or rate store can also correlate activity across deployments. Origin-authoritative verification means the origin can reproduce the decision from the same presentation bytes with its own trust configuration and policy. These are deployment trust and disclosure boundaries, including when the intermediary is an authorized service provider.

## 8. Security model

The protocol must assume that valid agents, principals, and issuers can still participate in harmful requests.

Primary technical threats include:

- replay and concurrent one-time redemption;
- request, origin, or action substitution;
- signature coverage and canonicalization gaps;
- stolen presenter keys and bearer leakage;
- over-broad or stale mandates;
- confused-deputy and prompt-injection paths;
- key-discovery and issuer-metadata substitution;
- downgrade and parser-differential attacks;
- stale revocation and policy state;
- unenforced obligations;
- resource-exhaustion attacks against expensive verification; and
- fail-open behavior during outages.

Primary sociotechnical threats include:

- legitimate but abusive principals;
- dishonest issuers;
- origins that over-collect identity;
- opaque vendor-global trust scores;
- discriminatory registries;
- inaccessible approval flows;
- missing recourse; and
- ecosystem capture by dominant infrastructure providers.

The full initial analysis is in [THREAT-MODEL.md](THREAT-MODEL.md). Production use requires independent review, multiple implementations, negative conformance vectors, and bounded real-world evaluation.

## 9. Preventing an agent-gatekeeping monopoly

Agent access may become an essential layer of participation in the digital economy. If one company or a stable duopoly controls the accepted agent directory, verifier, identity rail, or compatibility mark, it can determine which agents may cross the web's boundaries. It can also observe activity, tax transactions, privilege affiliated agents, or make provider exit impractical.

Source availability alone does not prevent this. A nominally open protocol can still centralize around:

- a required hosted verification endpoint;
- a proprietary issuer allowlist;
- a global identifier controlled by one provider;
- private conformance tests;
- exclusive distribution through a dominant edge network;
- a registry whose inclusion rules are opaque or pay-to-play;
- trademark rules that prohibit truthful independent compatibility claims; or
- a reference implementation whose undocumented quirks become normative.

AgentIsOK therefore treats competitive implementability as a protocol invariant.

### 9.1 Technical safeguards

- No protocol-critical call to an AgentIsOK service.
- Local and self-hosted verification.
- Origin-controlled trust and issuer policy.
- Multiple evidence profiles and issuers.
- No global AgentIsOK principal identifier.
- Public schemas, examples, and positive and negative conformance vectors.
- Portable configuration and machine-readable registry exports.
- Cached or offline-bounded metadata paths.
- At least two independent implementations before protocol maturity.

### 9.2 Governance safeguards

- Public technical decisions and change history.
- Apache-2.0 implementation and patent rights.
- DCO-certified contributions without copyright assignment.
- Early disclosure of known essential patent claims.
- Royalty-free standards objective.
- Nondiscriminatory registry and compatibility criteria.
- Conflict disclosure, appeals, and future multi-constituency governance.
- No permanent normative role for Univeracity, AgentIsOK, or a commercial service.

### 9.3 Commercial compatibility

Open infrastructure does not exclude strong businesses. Providers can compete on managed verification, integration quality, policy tooling, issuer compatibility, abuse intelligence, support, availability, and certification services.

The boundary is that convenience cannot become compulsory. AgentIsOK should become integral by being the best implementation and steward—not by making itself impossible to replace.

## 10. Reference architecture

```text
Agent/harness
    |
    | protected request
    v
Origin challenge issuer  -- 401 + WWW-Authenticate + JSON challenge
    |
    | request-bound challenge
    v
Agent evidence selection and approval
    |
    | POST presentation (HTTP Message Signature)
    v
Origin-side verifier adapters ---> optional issuer metadata/revocation
    |
    | provenance-preserving facts
    v
Origin policy decision point
    |
    | decision + obligations + optional artifact
    v
Policy enforcement point ---> application auth and business logic
```

The preferred hosted deployment keeps the data plane local. A managed provider can distribute signed adapter, issuer, and policy metadata without observing every request. Fully hosted verification remains possible for convenience but cannot be normative. A CDN worker that is the only verifier, or a vendor API that classifies the agent, is hosted verification even when no AgentIsOK hostname appears on the wire.

## 11. The first discriminating implementation

The first proof protects one low-consequence but bot-sensitive workflow: availability search.

This repository now contains a toy version of that loop:

1. A test origin that challenges automation with `401` and a structured challenge.
2. An agent responder that signs the presentation HTTP request.
3. An origin-scoped mandate bound to a pairwise subject, presenter key, action, and expiry.
4. A challenge requesting only structured action facts.
5. HTTP Message Signatures for request integrity, plus a Web Bot Auth adapter sketch; the second trust dimension is the mandate.
6. Local policy returning `allow_with_obligations` for bounded reads.
7. Atomic nonce consumption within one reference `Origin` instance; no shared or durable replay store.
8. Step-up before `reservation.commit`.
9. No natural-language task field in protocol messages.
10. Negative vectors for replay, expiry, wrong origin, wrong action, excessive scope, missing evidence, untrusted issuer, unenforceable obligations, and indeterminate revocation.

What it does not contain is a qualified origin. The next experiment is a **shadow evaluation**: existing CAPTCHA, WAF, or bot controls still decide; AgentIsOK emits a parallel would-allow / would-limit / would-deny that is logged, not enforced. The origin—not AgentIsOK—judges whether the conversion-to-abuse tradeoff moved.

The reference stops at an in-process decision and illustrative artifact issuance. It does not serve the proposed HTTP exchange, redeem an artifact, execute a protected retry, enforce rate or result limits, or complete human step-up. The TypeScript adapter supplies comparison plumbing, not a second verifier. Its header-only Worker example needs an origin-owned path to the signed presentation bytes and stored challenge before it can evaluate real evidence.

A qualified origin has a named bot-sensitive workflow, someone who owns rollback, a way to label good versus abusive traffic after the fact, and a verifier path it controls (origin process or its own proxy, not only a CDN checkbox). The first partner must not be a deployment where the edge is the only party that saw the proof.

Cooperating agents still have to answer the challenge while the old control remains authoritative, or there is nothing to compare. If the experiment only works by logging raw presentations and pairwise identifiers in a vendor cloud, it has failed the privacy test.

Measure authorized completion, false positives, abuse on traffic that would have been allowed, human step-up, latency, integration effort, support cost, and what each party learned. Predefine stop conditions.

The decisive result is not “the cryptography worked.” It is that a qualified origin sees desirable agent traffic, improves its conversion-to-abuse tradeoff, retains the integration, and can still reconstruct the decision without an edge verdict.

## 12. Adoption strategy

Agent developers receive obvious convenience, but origins bear integration and abuse risk. Adoption must begin with origin value:

- fewer desirable requests incorrectly blocked;
- better rate accountability;
- structured and enforceable action limits;
- lower CAPTCHA or manual-review cost;
- improved recourse through issuer and operator provenance;
- less unnecessary identity collection; and
- one integration surface across multiple agent and evidence providers.

The initial wedge should be origin or origin-controlled reverse-proxy middleware, not a new browser, universal identity provider, or payment network. It can run beside existing WAF, bot-management, application-auth, and fraud controls. A TLS-terminating CDN may enforce, but a first design partner that can only install a CDN checkbox cannot test origin-authoritative verification.

Distribution should expand through:

- edge and reverse-proxy integrations;
- popular application frameworks;
- agent and remote-browser harnesses;
- identity and delegation adapters;
- public conformance tooling; and
- design partnerships with origins that can measure real outcomes.

## 13. Standardization path

Protocol completeness should follow interoperability evidence, not precede it.

The proposed sequence is:

1. Publish the problem statement, principles, scope, threat model, and exploratory objects.
2. Build one end-to-end reference loop with two evidence profiles and negative vectors.
3. Interview origin operators and recruit a qualified origin design partner.
4. Run a shadow evaluation on one bounded workflow.
5. Produce a second independent verifier and responder.
6. Run public interoperability events and adversarial tests.
7. Refine ambiguous semantics using observed failures.
8. Submit the smallest missing profile or extension to the appropriate established standards venue.

Steps 1 and 2 are what this repository currently supports. Step 3 is the remaining scarce asset.

Formal standardization should not make the AgentIsOK brand, service, directory, or reference implementation normative. The technical protocol name should remain descriptive and vendor-neutral.

## 14. Project home

AgentIsOK is initially stewarded by Univeracity. That is a starting arrangement, not a protocol dependency.

The protocol must remain useful without Univeracity infrastructure, accounts, or sibling projects. Adjacent work on artifact portability or portable hosting may compose with AgentIsOK through explicit interfaces later. None of that is required to issue a challenge, verify a mandate, or enforce an obligation, and composition must not create a shared global identity or activity graph.

## 15. Limitations and open research

The proposal leaves important questions unresolved:

- the final HTTP binding and registration strategy;
- exact request canonicalization across intermediaries;
- privacy-preserving origin-scoped rate limits;
- boolean evidence negotiation without fingerprinting;
- usable and accessible step-up interfaces;
- issuer qualification and recourse;
- revocation freshness across risk classes;
- safe delegation through multiple agent hops;
- obligation composition and enforcement portability;
- resistance to discriminatory origin policy;
- sustainable funding for open governance and conformance; and
- preventing infrastructure concentration even when the protocol remains open.

AgentIsOK also cannot prove that an authorized agent will behave well after admission, that a principal's intent is benign, or that an origin's policy is fair. It improves evidence and control at one boundary; it does not solve all agent safety or digital-governance problems.

## 16. Conclusion

The agentic web needs a path between two bad defaults: treating every machine as hostile or giving authorized machines the human's unrestricted identity and credentials.

AgentIsOK proposes a third path: origin-issued challenges, minimum necessary evidence, exact request binding, local policy, enforceable limits, and explicit step-up. Its unit of trust is the request-specific relationship, not the agent as a permanent object of faith.

The protocol must also remain open at the layer where openness matters most. If agent clearance becomes essential infrastructure, no monopoly or duopoly should be able to decide unilaterally which agents, issuers, origins, or people may participate. Independent implementation, self-hosting, plural trust, public conformance, royalty-free rights, and anti-capture governance are therefore part of the security model.

The intended standard is one any origin can adopt, any qualified evidence provider can support, and any agent can answer—while AgentIsOK earns an integral role through implementation quality, integration, conformance, and trustworthy stewardship.

## References

[^http-signatures]: [RFC 9421: HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
[^digest-fields]: [RFC 9530: Digest Fields](https://www.rfc-editor.org/rfc/rfc9530)
[^dpop]: [RFC 9449: OAuth 2.0 Demonstrating Proof of Possession](https://www.rfc-editor.org/rfc/rfc9449)
[^rar]: [RFC 9396: OAuth 2.0 Rich Authorization Requests](https://www.rfc-editor.org/rfc/rfc9396)
[^token-exchange]: [RFC 8693: OAuth 2.0 Token Exchange](https://www.rfc-editor.org/rfc/rfc8693)
[^privacy-pass]: [RFC 9576: The Privacy Pass Architecture](https://www.rfc-editor.org/rfc/rfc9576)
[^vc]: [W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model-2.0/)
