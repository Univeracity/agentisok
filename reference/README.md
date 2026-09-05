# Reference loop

Prototype origin verifier, agent responder, and conformance runner for Agent Clearance Protocol `0.1`.

This is an in-process research prototype. It exercises the challenge → presentation → decision loop with public fixture keys, two evidence profiles, and negative cases. It does not run an HTTP server or authorize application traffic.

```text
fixture challenge + signed presentation request object
  -> local verification and policy
  -> decision + obligations + illustrative artifact
```

## What it implements

- Prototype canonical JSON and request-binding digests
- RFC 9421 subset (`ed25519`, `tag="agent-clearance"`) for the presentation POST
- Origin-scoped mandate verification
- Replay, expiry, audience, action-scope, and critical-obligation checks
- A single origin policy: bounded `availability.read`, step-up before `reservation.commit`

## Implementation limits

- **Approval and keys:** Test keys are derived from public seeds. The approval record is fabricated. No WebAuthn, real mandate issuance, key provisioning, or key rotation is implemented. Omitted keyrings use fixture keys; explicitly empty keyrings trust nobody.
- **HTTP and signatures:** Requests are Python objects. The parser implements a narrow RFC 9421 subset, not a complete Structured Fields implementation. The Web Bot Auth profile is a sketch and is rejected by this verifier.
- **Enforcement:** Returned obligations describe policy. The code does not rate-limit traffic, truncate results, redeem artifacts, retry a protected request, or complete step-up. `supported_obligations` models a deployment's claimed capabilities; it does not prove enforcement.
- **Replay:** A lock makes nonce consumption atomic within one shared `Origin` instance. Other instances, processes, and restarts do not share its in-memory set. There is no durable store or expiry cleanup.
- **Revocation:** Normal fixtures assume the test mandate is not revoked. The `fail_closed_on_unknown_revocation` switch exercises an indeterminate result; it is not a live status check.
- **Packaging:** Run from a source checkout with an editable install. Schema and vector lookup requires the repository tree; this is not a standalone distributable verifier package.

The protocol's HTTP exchange and sender-constrained retry are proposed in the [specification](../spec/agent-clearance-protocol.md). Production work is gated by [origin evidence and independent review](../ROADMAP.md).

## Setup

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e "./reference[test]"
pytest -q reference/tests
agent-clearance-conformance
```

Regenerate signed examples and vectors after protocol changes:

```bash
agent-clearance-generate
```

Test keys are derived from documented seeds. They are not secrets and MUST NOT be used outside this repository.
