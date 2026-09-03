# HTTP Message Signatures profile

- **Identifier:** `urn:agent-clearance:profile:http-message-signatures:rfc9421:0.1`
- **Class:** `request_integrity`
- **Status:** Prototype profile for draft `0.1`
- **Depends on:** [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421), [RFC 9530](https://www.rfc-editor.org/rfc/rfc9530)

## What this profile establishes

The presenter controls the key identified by `keyid` and signed a specific HTTP request at a specific time.

It does not establish who the principal is, what the principal authorized, that the key is uncompromised, or that the origin should accept the request.

## Where it is used

In the candidate HTTP binding this profile signs:

1. The presentation POST to `presentation_endpoint`.
2. The later retry of the protected request when a clearance artifact is used.

It is **not** also embedded inside the presentation JSON.

## Key identifiers

`keyid` MUST be an `https` URL or a stable opaque string chosen by the harness. It MUST NOT be a DID in this profile. DID resolution is an optional future adapter, not a prerequisite.

The identifier on the wire MUST NOT include the relying origin (host, origin URL, or a reversible encoding of it). A path such as `/keys/travel.example/k1` is a join key for any TLS terminator, WAF, or log pipeline. Harnesses MAY isolate keys per origin internally; the presented identifier should be an opaque pairwise handle, for example `https://harness.example/keys/k/8f3a1c`.

Draft `0.1` fixtures use an opaque path such as `https://harness.example/keys/k/8f3a1c`. The value is still a public test identifier, not a production key directory.

## Algorithms

The prototype requires `ed25519` as defined for HTTP Message Signatures. Origins MAY later advertise additional algorithms in discovery. Agents MUST NOT silently fall back to an unsigned request.

## Covered components

### Presentation POST

The signature MUST cover:

| Component | Rule |
|---|---|
| `@method` | `POST` |
| `@authority` | Host and optional port of `presentation_endpoint`, lowercase |
| `@path` | Path of `presentation_endpoint` |
| `@query` | Included if and only if the URL has a query |
| `content-digest` | RFC 9530 `sha-256` of the exact presentation body |
| `content-type` | `application/agent-clearance-presentation+json` |

Parameters:

| Parameter | Rule |
|---|---|
| `created` | Unix timestamp; reject if more than 60 seconds in the future |
| `expires` | MUST be present, later than `created`, not expired, and no later than the challenge `expires_at` |
| `keyid` | Presenter key |
| `alg` | `ed25519` |
| `nonce` | Exact challenge nonce |
| `tag` | `agent-clearance` |

### Protected-request retry

The signature MUST cover `@method`, `@authority`, `@path`, `@query` when present, and `content-digest` when the request has a body that affects authorization. `tag` remains `agent-clearance`. `keyid` MUST equal the artifact's `key_confirmation`.

## Validation algorithm

1. Reject if any required component or parameter is missing.
2. Reconstruct the request target from the challenge or retry; reject on mismatch.
3. Verify `content-digest` against the received body.
4. Verify `nonce` equals the unused challenge nonce for a presentation POST.
5. Verify `created` is no earlier than the challenge, no more than 60 seconds in the future, and equal to the presentation body's `created_at`.
6. Verify `expires` is later than `created`, has not passed, and is no later than the challenge expiry.
7. Resolve `keyid` from origin-local policy, a trusted key directory, or the test keyring. Do not dereference an unknown URL unless the origin's trust policy says to.
8. Verify the Ed25519 signature over the RFC 9421 signature base.
9. Emit a `request_integrity` fact with the presenter key, covered components, and evidence digest.

Unknown signature labels other than the Agent Clearance signature MAY exist (for example a Web Bot Auth signature). They are not used by this profile.

## Intermediaries

This profile assumes the verifier sees the same `@authority`, `@path`, `@query`, and body the signer covered. CDN rewrites, HTTP/2 vs HTTP/1 authority differences, and reconstructed trailing slashes are out of scope for `0.1`. Origins SHOULD terminate this verification at the component that sees the raw request, or canonicalize before signing and verifying using a documented intermediary profile.

Unsigned query parameters MUST NOT affect authorization decisions.

## Replay

The challenge nonce in the presentation signature is single-use. The origin MUST record it atomically when a presentation is accepted for evaluation, including when the later policy decision is `deny`. Retry artifacts have their own replay rules.

## Normalized facts

Successful verification emits at least:

```text
claim: presenter.controls_key
value: keyid
subject.kind: presenter
audience: challenge origin
evidence_profile: this profile
```

## Negative cases

Reject when:

- the nonce was already used;
- `tag` is missing or not `agent-clearance`;
- `keyid` is unknown;
- the content digest does not match;
- `@path` or `@authority` does not match the presentation endpoint;
- the signature base uses a different component order than the `Signature-Input` header; or
- the algorithm is absent or not `ed25519`.

## Privacy

A stable `keyid` reused across origins is a cross-site identifier. Harnesses SHOULD generate pairwise keys. Origins that require pairwise keys MUST say so in `privacy.pairwise_subject_required` and in policy, not by inferring pairwise-ness from the key URL format.

A pairwise key whose `keyid` contains the origin host is still a join key for intermediaries. Opacity of the presented identifier is part of the privacy property, not an implementation detail.
