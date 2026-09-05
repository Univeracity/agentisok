# AgentIsOK

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/agentisok-logo-dark.svg">
  <img src="assets/brand/agentisok-logo-light.svg" alt="AgentIsOK — gold AI above OK with a green checkmark" width="570">
</picture>

**Open clearance for authorized agents. Evidence travels. The origin decides.**

[![Conformance](https://github.com/Univeracity/agentisok/actions/workflows/conformance.yml/badge.svg)](https://github.com/Univeracity/agentisok/actions/workflows/conformance.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

AgentIsOK proposes a machine-verifiable alternative to a human CAPTCHA when a website is willing to admit authorized automation. The website asks for bounded evidence about the agent's authority and exact request, then applies its own policy. Ordinary account, abuse, and application controls still apply.

The name compresses to **AI / OK**. “OK” means OK for this action, on this origin, under this policy, at this time. The logo identifies the project; it is not a safety certification or global trust score.

> **Status: Pre-alpha research prototype.** The candidate protocol, two implemented evidence profiles, reference verifier, and shadow adapter are available. Production enforcement, independent interoperability, and origin outcome evidence are not. This code has not received an independent security review and must not authorize production actions. See [implementation limits](reference/README.md) and [evidence gates](ROADMAP.md).

## Start here

- **Understand the thesis:** [whitepaper](WHITEPAPER.md), especially the [testable claim](WHITEPAPER.md#21-the-testable-claim).
- **Run the prototype:** [quickstart below](#run-the-reference-loop) or the [edge shadow adapter](integrations/typescript-edge/).
- **Bring an origin workflow:** [pilot qualification](pilot/README.md) and the [open design-partner call](https://github.com/Univeracity/agentisok/issues/1).
- **Build or review independently:** [protocol](spec/agent-clearance-protocol.md), [conformance vectors](conformance/), and [contributing](CONTRIBUTING.md).

## Why this exists

Human challenges are an awkward interface for agents acting for people and organizations. When existing API access or signed-agent rules are insufficient, those agents need a legitimate path through the automation boundary without impersonating humans or inheriting unrestricted credentials.

AgentIsOK is a challenge and clearance layer:

```text
protected request
  -> 401 + origin challenge
  -> presentation POST (HTTP Message Signature + mandate)
  -> local verification and policy
  -> allow / allow with obligations / step up / deny / indeterminate
  -> optional sender-constrained retry
```

The central boundary is simple:

> AgentIsOK verifies and composes evidence. The receiving service decides what is OK.

Web Bot Auth addresses automated-client authentication; its [IETF charter](https://datatracker.ietf.org/doc/charter-ietf-webbotauth/) excludes end-user authentication and an intent vocabulary. AgentIsOK explores a complementary challenge, mandate, and obligation contract for origin policy. Its Web Bot Auth adapter remains a sketch, and this repo does not claim interoperability with a deployed Web Bot Auth service.

## Why it is open

Agent access to the web is too consequential to depend on one company's permission, directory, hosted verifier, or private policy. A conforming implementation must be independently implementable. Compatibility cannot require an AgentIsOK account, a commercial API key, a proprietary allowlist, or an AgentIsOK-operated control plane.

The working technical name is **Agent Clearance Protocol**. Do not abbreviate it ACP; that short name is already used by unrelated agent protocols. Identifiers use the token `agent-clearance`.

## Design principles

- **Origin authority:** Evidence informs; the receiving service decides.
- **Request-bound trust:** “OK” applies to one action and context, not an actor forever.
- **Separation of powers:** Identity, delegation, request integrity, risk, rate limits, and payment authority remain distinct.
- **No mandatory gatekeeper:** Local verification, self-hosting, multiple issuers, and competing implementations are first-class requirements.
- **Minimum disclosure:** Participants learn only what the action requires.
- **Protocol reuse:** Existing Internet and identity standards are composed rather than replaced.
- **Explicit failure:** Denial, insufficient evidence, and operational failure are not conflated.
- **Enforceable obligations:** Limits returned by policy must be applied by the enforcement point. Unknown *critical* obligations fail closed.

See [PRINCIPLES.md](PRINCIPLES.md) for the complete set.

## What exists now

The first discriminating loop is in this repository:

1. A test origin challenges a bounded `availability.read`.
2. An agent responder signs the presentation HTTP request ([HTTP Message Signatures profile](spec/profiles/http-message-signatures.md)).
3. It presents an origin-scoped mandate ([mandate profile](spec/profiles/origin-scoped-mandate.md)).
4. Local policy returns `allow_with_obligations` for the read and requires step-up before `reservation.commit`.
5. Twenty-six conformance vectors cover replay, validity windows, malformed mandates, exact request binding, omitted or excessive scope, profile confusion, missing evidence, unenforceable obligations, untrusted issuers, and indeterminate revocation.

| Surface | Implemented today | Still required |
|---|---|---|
| Python reference | In-process presentation verification, bounded decisions, test artifact issuance | HTTP serving, artifact redemption, actual rate/result enforcement, production keys and replay storage |
| Evidence profiles | RFC 9421 subset and origin-scoped test mandates | Approval/issuance integration, live revocation policy, independent security review |
| TypeScript edge adapter | Sampled comparison, bounded waits, minimized metrics | Origin evaluator with access to the actual signed bytes and challenge state |
| Conformance | Deterministic fixtures and negative cases | A materially independent verifier and responder |
| Pilot | Qualification, rollout, and measurement contracts | An origin-owned experiment with independent outcome labels |

### Run the reference loop

Requires Python 3.11+ and a repository checkout. The fixtures use a fixed evaluation time and public test keys; they do not contact an origin or issuer.

```bash
git clone https://github.com/Univeracity/agentisok.git
cd agentisok
python3 -m venv .venv
. .venv/bin/activate
pip install -e "./reference[test]"
pytest -q reference/tests
agent-clearance-conformance
```

Expected conformance summary: `26 passed, 0 failed`. The TypeScript adapter requires Node.js 24+; run `npm ci && npm test` from `integrations/typescript-edge`.

Passing fixtures establishes prototype behavior. The product hypothesis is whether an origin can recover desirable agent traffic within its abuse, privacy, and operating-cost budgets. Shadow mode can estimate decision disagreements; it cannot demonstrate recovered completion while the incumbent still blocks the request. That origin evidence does not exist yet.

## What to do next

The next work is evidence-driven:

- origin-side discovery: real workflows where legitimate agents are blocked or challenged;
- one shadow-mode design partner, with existing controls still deciding and the origin able to reconstruct the proof;
- a second independent verifier before anyone calls this mature.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository map

| Document | Purpose |
|---|---|
| [PRINCIPLES.md](PRINCIPLES.md) | Non-negotiable design and ecosystem invariants |
| [SCOPE.md](SCOPE.md) | What AgentIsOK does and deliberately does not do |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Roles, trust boundaries, data flow, and deployment modes |
| [THREAT-MODEL.md](THREAT-MODEL.md) | Technical, privacy, governance, and ecosystem threats |
| [WHITEPAPER.md](WHITEPAPER.md) | Motivation, thesis, proposed design, and adoption path |
| [ROADMAP.md](ROADMAP.md) | Evidence required to advance, reshape, or stop |
| [spec/agent-clearance-protocol.md](spec/agent-clearance-protocol.md) | Protocol skeleton and candidate HTTP binding |
| [spec/profiles/](spec/profiles/) | HTTP Message Signatures, origin-scoped mandate, Web Bot Auth adapter |
| [reference/](reference/) | Prototype origin, responder, and conformance runner |
| [conformance/](conformance/) | Positive and negative vectors |
| [pilot/](pilot/) | Design-partner, shadow-mode, outreach, and metrics package |
| [integrations/typescript-edge/](integrations/typescript-edge/) | Deployable Fetch-standard shadow adapter |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to participate |
| [IPR-POLICY.md](IPR-POLICY.md) | Contribution, patent, and standards commitments |
| [GOVERNANCE.md](GOVERNANCE.md) | Open decision-making and anti-capture safeguards |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and security status |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Conduct expectations |
| [MAINTAINERS.md](MAINTAINERS.md) | Current stewardship |
| [assets/brand/](assets/brand/) | Logo SVGs, PNGs, social preview, and usage guidance |

## Standards posture

The protocol profiles HTTP Message Signatures and composes adjacent work such as Digest Fields, OAuth proof of possession and rich authorization, Privacy Pass architecture, and Web Bot Auth as an optional request-integrity adapter. Unstable drafts are not treated as settled foundations.

The project will seek interoperability experience before pursuing formal standardization in an appropriate existing venue.

## License

Copyright 2026 the AgentIsOK contributors.

Licensed under the [Apache License 2.0](LICENSE). The license applies to code, specifications, documentation, examples, and test material in this repository unless a file states otherwise.
