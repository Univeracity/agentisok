# Draft schemas

These JSON Schemas express the exploratory `0.1` object shapes described in [the protocol skeleton](../agent-clearance-protocol.md).

They are design aids, not stable APIs. In particular, they do not yet express every semantic requirement, including:

- `expires_at` occurring after `created_at`;
- exact-origin rather than general URI validation;
- uniqueness of evidence requirement identifiers;
- evidence satisfying all mandatory requirements;
- consistency between decision type and obligations or continuation;
- cryptographic proof, digest, or nonce correctness; and
- profile-specific validation.

Implementations must not treat schema validation as security verification or policy authorization.

The schemas currently reject unknown top-level fields to expose extension and versioning questions early. A future specification must define critical-extension behavior explicitly.
