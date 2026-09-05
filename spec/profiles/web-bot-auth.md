# Web Bot Auth adapter profile

- **Identifier:** `urn:agent-clearance:profile:web-bot-auth:0.1`
- **Class:** `request_integrity`
- **Status:** Adapter sketch for draft `0.1`

Web Bot Auth is IETF work on cryptographically authenticating automated clients and conveying operator information. The [working-group charter](https://datatracker.ietf.org/doc/charter-ietf-webbotauth/) covers agents acting for end users but excludes authenticating the end user and defining an intent vocabulary. Cloudflare documents [one deployment](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/) using HTTP Message Signatures, `tag="web-bot-auth"`, and a `Signature-Agent` directory. Vendor directory registration is a deployment policy, not an Agent Clearance protocol requirement.

This profile sketches how an Agent Clearance verifier could treat such a signature as `request_integrity` evidence. The Python reference does not implement it and rejects presentations that claim it. No Web Bot Auth interoperability has been demonstrated by this repository.

It is an adapter, not a second trust dimension. It does not replace an origin-scoped mandate.

## What this profile establishes

An HTTP request was signed by a key published in a Signature-Agent directory that the origin already trusts as an agent or operator identity.

It does not establish a user's mandate, pairwise principal, or permission to perform the challenged action.

## Relationship to the HTTP Message Signatures profile

Both profiles use RFC 9421. They MUST be distinguished by `tag`:

| `tag` | Profile |
|---|---|
| `agent-clearance` | [http-message-signatures.md](http-message-signatures.md) |
| `web-bot-auth` | this adapter |

An origin MAY accept either profile for a `request_integrity` requirement. A message MAY carry both signatures. Satisfying request integrity with Web Bot Auth does not satisfy `delegation`.

## Validation sketch

This adapter does not redefine Web Bot Auth. A verifier that claims this profile MUST:

1. Follow the origin's current Web Bot Auth verification policy, including trusted Signature-Agent directories and replay rules that policy already has.
2. Reject if `tag` is not `web-bot-auth`.
3. Reject if the directory or key is not in the origin's trust configuration.
4. Bind the verified agent/operator identity into a `request_integrity` fact whose subject kind is `agent_operator`, never `pairwise_principal`.
5. Still require whatever other evidence classes the challenge mandates.

If the origin cannot verify Web Bot Auth locally and would have to call a vendor API to classify the agent, that verification path is a hosted verifier under the architecture document. It is allowed only as a replaceable convenience. A CDN header or dashboard classification is not origin-authoritative request-integrity evidence, even when this profile identifier is attached to the requirement.

## What this profile deliberately omits

- Cloudflare (or any CDN) directory inclusion as a protocol requirement.
- Replay rules beyond what the origin's Web Bot Auth deployment already enforces.
- Treating a signed agent as authorized for writes, payments, or account access.

Automated-client authentication alone does not establish a principal's delegation or satisfy the receiving application's authorization policy. A future adapter must demonstrate local verification and request binding before claiming support.

## When to use it

Use this adapter when the protected request already carries a Web Bot Auth signature and the origin wants to avoid demanding a second request-integrity signature.

Do not use it as the only evidence for a bot-sensitive write. Pair it with [origin-scoped-mandate.md](origin-scoped-mandate.md) or another `delegation` profile.

## Negative cases

- `tag` missing or `agent-clearance` presented as Web Bot Auth.
- Signature-Agent directory not in origin policy.
- Using the operator identity as a pairwise principal or global user identifier.
- Skipping mandate verification because the agent is “verified.”
