# Reason codes

Reason codes are coarse, stable, and safe to return to agents. They MUST NOT encode private claims, raw issuer errors, or fraud-model features.

| Code | Typical decision | Meaning |
|---|---|---|
| `evidence.sufficient` | `allow`, `allow_with_obligations` | Required evidence verified |
| `policy.bounded_read` | `allow_with_obligations` | Origin policy admits a limited read |
| `evidence.missing` | `deny` | A mandatory requirement was absent |
| `evidence.expired` | `deny` | Evidence or challenge was outside its validity window |
| `evidence.untrusted_issuer` | `deny` | Issuer or key is not in origin policy |
| `evidence.invalid` | `deny` | Cryptographic or structural verification failed |
| `binding.mismatch` | `deny` | Request binding or digest did not match |
| `origin.mismatch` | `deny` | Audience or origin did not match |
| `replay.nonce` | `deny` | Challenge nonce was already used |
| `mandate.scope` | `deny` | Mandate does not cover the requested action or bounds |
| `mandate.expired` | `deny` | Mandate is expired or too old |
| `obligation.unsupported` | `deny` or `indeterminate` | A critical obligation cannot be enforced |
| `challenge.expired` | `deny` | Challenge is outside its validity window |
| `evaluation.indeterminate` | `indeterminate` | A dependency or parser failure prevented a safe decision |
| `policy.denied` | `deny` | Origin policy affirmatively refused |
| `step_up.required` | `step_up` | Additional evidence or current approval is required |
