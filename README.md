# AgentIsOK

**A machine-verifiable alternative to CAPTCHA for authorized agents.**

AgentIsOK lets a website ask an automated agent for bounded evidence about who or what it represents, what it may do, and whether its exact request satisfies the website's policy. The website remains the final decision-maker.

```text
Agent Is OK  ->  A I OK  ->  AI OK
```

`AI OK` is always contextual: OK for this action, on this origin, under this policy, at this time. It is not a universal safety label or global trust score.

> **Status:** Pre-alpha design and interoperability work. The protocol is incomplete, has not received a security review, and must not be used to authorize production actions.

## Why this exists

CAPTCHAs were designed for a web where useful visitors were assumed to be human and automated visitors were assumed to be hostile. Agents acting for people and organizations need a legitimate path through that boundary without impersonating humans, inheriting unrestricted credentials, or defeating an origin's controls.

AgentIsOK is a challenge and clearance layer:

```text
protected request
  -> origin challenge
  -> request-bound evidence
  -> local verification and policy
  -> allow / allow with obligations / step up / deny / indeterminate
```

The central boundary is simple:

> AgentIsOK verifies and composes evidence. The receiving service decides what is OK.

## Why it is open

Agent access to the web is too consequential to depend on one company's permission, directory, hosted verifier, or private policy. An open standard with competing implementations is an explicit design goal, so that no monopoly or duopoly can become the unavoidable gatekeeper between agents and the services they use.

A conforming implementation must be independently implementable and deployable. Compatibility cannot require an AgentIsOK account, a commercial API key, a proprietary allowlist, or an AgentIsOK-operated control plane.

AgentIsOK aims to be an integral player by building excellent reference software, integrations, conformance tests, policy tooling, and ecosystem stewardship—not by making provider exit impractical.

## Design principles

- **Origin authority:** Evidence informs; the receiving service decides.
- **Request-bound trust:** “OK” applies to one action and context, not an actor forever.
- **Separation of powers:** Identity, delegation, request integrity, risk, rate limits, and payment authority remain distinct.
- **No mandatory gatekeeper:** Local verification, self-hosting, multiple issuers, and competing implementations are first-class requirements.
- **Minimum disclosure:** Participants learn only what the action requires.
- **Protocol reuse:** Existing Internet and identity standards are composed rather than replaced.
- **Explicit failure:** Denial, insufficient evidence, and operational failure are not conflated.
- **Enforceable obligations:** Limits returned by policy must be applied by the enforcement point.

See [PRINCIPLES.md](PRINCIPLES.md) for the complete set.

## Repository map

| Document | Purpose |
|---|---|
| [PRINCIPLES.md](PRINCIPLES.md) | Non-negotiable design and ecosystem invariants |
| [SCOPE.md](SCOPE.md) | What AgentIsOK does and deliberately does not do |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Roles, trust boundaries, data flow, and deployment modes |
| [THREAT-MODEL.md](THREAT-MODEL.md) | Technical, privacy, governance, and ecosystem threats |
| [WHITEPAPER.md](WHITEPAPER.md) | Motivation, thesis, proposed design, and adoption path |
| [spec/agent-clearance-protocol.md](spec/agent-clearance-protocol.md) | Initial protocol skeleton and candidate HTTP binding |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to participate |
| [IPR-POLICY.md](IPR-POLICY.md) | Contribution, patent, and standards commitments |
| [GOVERNANCE.md](GOVERNANCE.md) | Open decision-making and anti-capture safeguards |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and security status |

Machine-readable draft schemas and examples live under [`spec/schema/`](spec/schema/) and [`examples/`](examples/).

## What to build first

The first proof should protect one low-consequence but bot-sensitive action, such as availability search. It should accept more than one evidence profile, bind proofs to the exact request, enforce replay and quota limits, and require step-up before a consequential write.

The test is not whether signatures validate. The test is whether an origin can admit desirable agent traffic while preserving or improving its abuse posture and disclosing less sensitive information.

## Standards posture

The protocol will profile and compose mature building blocks such as HTTP Message Signatures, OAuth proof of possession and rich authorization, Privacy Pass architecture, and established credential formats. Agent-specific drafts may be explored through adapters, but unstable drafts will not be treated as settled foundations.

The working technical name **Agent Clearance Protocol** is descriptive and provisional. The project will seek interoperability experience before pursuing formal standardization in an appropriate existing venue.

## Contributing

Agent developers, origin operators, abuse and fraud teams, identity providers, privacy engineers, accessibility experts, implementers, and standards participants are all needed. Start with [CONTRIBUTING.md](CONTRIBUTING.md), the [scope](SCOPE.md), and the [IPR policy](IPR-POLICY.md).

By contributing, you agree that participation is governed by the repository's license and contribution terms.

## License

Copyright 2026 the AgentIsOK contributors.

Licensed under the [Apache License 2.0](LICENSE). The license applies to code, specifications, documentation, examples, and test material in this repository unless a file states otherwise.
