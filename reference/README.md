# Reference loop

Prototype origin verifier, agent responder, and conformance runner for Agent Clearance Protocol `0.1`.

This is not a production implementation. It exists to prove the challenge → presentation → decision loop, exercise two evidence profiles, and fail the documented negative cases.

```text
protected request
  -> 401 + challenge
  -> POST presentation (HTTP Message Signature)
  -> decision + obligations
  -> retry with sender-constrained artifact
```

## What it implements

- Prototype canonical JSON and request-binding digests
- RFC 9421 subset (`ed25519`, `tag="agent-clearance"`) for the presentation POST
- Origin-scoped mandate verification
- Replay, expiry, audience, action-scope, and critical-obligation checks
- A single origin policy: bounded `availability.read`, step-up before `reservation.commit`

It does not implement WebAuthn, Web Bot Auth directory discovery, distributed replay, or a general policy language.

## Setup

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e "./reference[test]"
pytest -q
agent-clearance-conformance
```

Regenerate signed examples and vectors after protocol changes:

```bash
agent-clearance-generate
```

Test keys are derived from documented seeds. They are not secrets and MUST NOT be used outside this repository.
