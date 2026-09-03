# Draft schemas

These JSON Schemas express the exploratory `0.1` object shapes described in [the protocol skeleton](../agent-clearance-protocol.md).

| File | Object |
|---|---|
| [challenge.schema.json](challenge.schema.json) | Origin challenge |
| [presentation.schema.json](presentation.schema.json) | Agent presentation body (HTTP signature is separate) |
| [decision.schema.json](decision.schema.json) | Origin decision |
| [discovery.schema.json](discovery.schema.json) | `/.well-known/agent-clearance` |
| [fact.schema.json](fact.schema.json) | Verifier-to-policy fact |
| [mandate.schema.json](mandate.schema.json) | Origin-scoped mandate evidence |

They are design aids, not stable APIs. Schema validation is not security verification. Semantic rules implemented by the reference verifier include:

- `expires_at` after `created_at`;
- exact-origin form (`https` host and optional port, no path);
- presentation endpoint on the challenge origin;
- unique evidence requirement identifiers;
- evidence for every mandatory requirement;
- request-binding digest consistency;
- mandate audience, presenter, action, and constraint matching;
- decision/obligation/artifact consistency beyond what the schema encodes;
- HTTP Message Signature coverage and nonce replay; and
- enforcement of critical obligations.

`$id` values use `https://agentisok.org/spec/0.1/` as a namespace. That host is not a protocol-critical service.

The schemas reject unknown top-level fields to expose extension questions early. A future specification must define critical-extension behavior explicitly.
