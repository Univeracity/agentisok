# AgentIsOK

**A machine-verifiable alternative to CAPTCHA for authorized agents.**

AgentIsOK lets a website ask an automated agent for bounded evidence about who or what it represents, what it may do, and whether its exact request satisfies the website's policy. The website remains the final decision-maker.

```text
Agent Is OK  ->  A I OK  ->  AI OK
```

`AI OK` is always contextual: OK for this action, on this origin, under this policy, at this time. It is not a universal safety label or global trust score.

> **Status:** Pre-alpha. There is a candidate HTTP binding, two evidence profiles, a reference loop, and failing negative vectors. The protocol is incomplete, has not received a security review, and must not be used to authorize production actions.

## Why this exists

CAPTCHAs were designed for a web where useful visitors were assumed to be human and automated visitors were assumed to be hostile. Agents acting for people and organizations need a legitimate path through that boundary without impersonating humans, inheriting unrestricted credentials, or defeating an origin's controls.

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

This is not CAPTCHA bypass, and it is not a replacement for Web Bot Auth. Web Bot Auth can recognize a signed agent. AgentIsOK is the challenge, mandate, obligation, and origin-policy layer that recognition does not provide.

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
5. Seventeen conformance vectors cover replay, expiry, signature time and coverage, wrong audience, binding mismatch, excess scope, duplicate or unsolicited evidence, missing evidence, unenforceable obligations, untrusted issuers, and indeterminate revocation.

Run it:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e "./reference[test]"
pytest -q reference/tests
agent-clearance-conformance
```

The test is not whether signatures validate. The test is whether an origin can admit desirable agent traffic while preserving or improving its abuse posture and disclosing less sensitive information. That origin evidence does not exist yet.

## What to do next

Protocol completeness is not the remaining work. The remaining work is:

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

## Standards posture

The protocol profiles HTTP Message Signatures and composes adjacent work such as Digest Fields, OAuth proof of possession and rich authorization, Privacy Pass architecture, and Web Bot Auth as an optional request-integrity adapter. Unstable drafts are not treated as settled foundations.

The project will seek interoperability experience before pursuing formal standardization in an appropriate existing venue.

## License

Copyright 2026 the AgentIsOK contributors.

Licensed under the [Apache License 2.0](LICENSE). The license applies to code, specifications, documentation, examples, and test material in this repository unless a file states otherwise.
