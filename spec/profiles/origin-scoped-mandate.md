# Origin-scoped mandate profile

- **Identifier:** `urn:agent-clearance:profile:origin-scoped-mandate:0.1`
- **Class:** `delegation`
- **Status:** Prototype profile for draft `0.1`

This is the novel evidence object in draft `0.1`. HTTP signatures prove that a key sent this request. A mandate proves that a principal approved a structured action for that key at this origin.

## What this profile establishes

A mandate issuer trusted by the origin attested that:

- a pairwise subject approved a structured action;
- the approval was bound to this origin as audience;
- the presenter key is the only key that may use the mandate;
- the action, resource, and constraints cover the challenged request; and
- the mandate has not expired.

It does not establish that the principal is civilly identified, that the principal is benign, or that the origin's rate and abuse policy should allow the request.

## Approval UX

The principal approves a structured preview, not a natural-language task:

- origin
- action type
- resource if any
- quantity or result bounds
- expiry
- agent or harness identifier the origin will see

The prototype treats a phishing-resistant authenticator (passkey) as the intended approval method. The reference implementation does not speak WebAuthn. It consumes the mandate that would be issued after such an approval.

## Mandate object

The evidence envelope `value` is this JSON object:

```json
{
  "mandate_id": "urn:uuid:...",
  "profile": "urn:agent-clearance:profile:origin-scoped-mandate:0.1",
  "issuer": "https://travel.example",
  "audience": "https://travel.example",
  "subject": {
    "kind": "pairwise_principal",
    "id": "urn:uuid:43ff2d65-a302-4b52-9f80-f1f3776d8b71"
  },
  "presenter_key_id": "https://harness.example/keys/k/8f3a1c",
  "actions": [
    {
      "type": "availability.read",
      "resource": "hotel_inventory",
      "constraints": {
        "maximum_results": 100
      }
    }
  ],
  "created_at": "2026-08-31T15:50:00Z",
  "expires_at": "2026-08-31T16:15:00Z",
  "approval": {
    "method": "passkey",
    "displayed": {
      "origin": "https://travel.example",
      "action": "availability.read",
      "resource": "hotel_inventory",
      "expires_at": "2026-08-31T16:15:00Z",
      "presenter_key_id": "https://harness.example/keys/k/8f3a1c"
    }
  },
  "signature": {
    "alg": "ed25519",
    "key_id": "https://travel.example/.well-known/agent-clearance/keys/mandate-issuer",
    "value": "<base64url signature>"
  }
}
```

`signature.value` is Ed25519 over the prototype canonical JSON of the mandate with `signature.alg` and `signature.key_id` present but `signature.value` absent. This protects the algorithm and key-selection metadata as well as the mandate claims. The prototype serialization sorts object keys, removes insignificant whitespace, and emits UTF-8; it is not yet an RFC 8785 implementation.

## Audience and isolation

`issuer` and `audience` MUST be exact origins. A mandate for `https://travel.example` MUST be rejected at any other origin, including `https://travel.example:443` if the challenge origin omitted the port, and including sibling hosts.

The pairwise subject identifier MUST be meaningful only at this origin. Implementations MUST NOT reuse it as a global account handle.

## Action matching

The challenged `request_binding.action` is covered when a mandate action has:

- the same `type`;
- the same `resource`, including whether a resource is present; and
- the same constraint names, with requested values within the approved bounds.

Unknown action types do not match. `availability.read` does not cover `reservation.commit`. Absence of `constraints` does not mean unlimited; it means no additional attested bound. Origins that need a maximum MUST require it in the challenge and the mandate.

For the prototype's `maximum_results`, both values MUST be positive JSON integers and the requested value MUST be no greater than the approved value. Booleans are not integers. Other constraint values match by exact prototype canonical JSON equality; no numeric ordering is inferred for an unknown constraint. For example, lowering a `minimum_age` is not attenuation. An omitted resource or constraint MUST NOT erase a restriction in the mandate. The bounded-read policy requires an explicit `maximum_results` in both objects; it does not insert a wider default after verification.

Starter action types for the first workflow are listed in [../vocabulary/actions.md](../vocabulary/actions.md). Action types are origin-local unless an origin explicitly adopts the starter list. They are not a global capability ontology.

## Presenter binding

`presenter_key_id` MUST equal the presentation `presenter.key_id` and the HTTP signature `keyid`. A stolen mandate JSON without the presenter key is useless. A stolen presenter key with an expired or audience-mismatched mandate is also useless.

## Freshness

Origins SHOULD set `max_age_seconds` on the delegation requirement. The verifier MUST reject a mandate whose `expires_at` is in the past or whose age exceeds `max_age_seconds` when that field is present.

The verifier MUST also reject a future `created_at` or an `expires_at` that is not later than `created_at`. These invalid validity windows return `evidence.invalid` in the prototype; expired or stale mandates return `mandate.expired`.

## Revocation

The prototype has no live revocation list. A production profile MUST define one of:

- short enough expiry that revocation is expiry;
- an origin-local mandate identifier denylist; or
- an issuer status endpoint bound to `mandate_id`.

Until then, operators MUST treat stolen presenter keys as requiring mandate re-issuance and key retirement.

## Normalized facts

Successful verification emits facts including:

- `mandate.action` for each covered action type;
- `mandate.resource` when present;
- `mandate.expires_at`;
- `subject.pairwise_id`;
- `presenter.key_id`;
- issuer, audience, profile, and evidence digest.

Disclosures requested by the challenge MUST be a subset of these facts. The verifier MUST NOT copy `approval.displayed` into logs as a natural-language task substitute if it is identical to the structured action.

## Negative cases

Reject when:

- audience is not the challenge origin;
- presenter key does not match;
- the mandate does not cover the requested action or resource;
- requested constraints exceed the mandate (for example 500 results when 100 were approved);
- the mandate is expired or too old;
- `subject.kind` is not `pairwise_principal` when the challenge requires pairwise subjects;
- the issuer key is unknown; or
- the signature does not verify.

## Privacy

The mandate MUST NOT include a natural-language goal, destination list, civil name, or global subject identifier. Pairwise identifiers and action types are the intended disclosure.

The mandate issuer in this profile is the origin (or a key the origin already trusts). That is a deliberate first-workflow simplification: the origin does not learn a new civil identity, and no third-party issuer learns the destination. Cross-origin portable mandates are explicitly out of scope for `0.1`.

This is scoped disclosure to the origin, not unlinkability from the origin’s TLS terminator. A CDN that terminates HTTPS still sees the mandate. Blind issuance and unlinkable redemption are not properties of this profile.
