# Evidence profiles

Draft `0.1` ships three profiles so an origin can require request integrity and a mandate without depending on one vendor format.

| Identifier | Class | Role |
|---|---|---|
| `urn:agent-clearance:profile:http-message-signatures:rfc9421:0.1` | `request_integrity` | Presenter proof of possession over the presentation HTTP request |
| `urn:agent-clearance:profile:web-bot-auth:0.1` | `request_integrity` | Adapter for Cloudflare-style Web Bot Auth signed-agent recognition |
| `urn:agent-clearance:profile:origin-scoped-mandate:0.1` | `delegation` | Origin-audience mandate approved for a structured action |

HTTP Message Signatures and Web Bot Auth are **not** the two materially different profiles. They both prove control of an HTTP signing key. The independent second profile is the origin-scoped mandate.

Web Bot Auth is specified so an origin can accept an already-signed agent as request-integrity evidence instead of a second Agent Clearance signature. It does not prove a principal's mandate. A CDN classification API is not this adapter; the origin still has to verify the signature under its own trust configuration.

These profiles are implementable sketches. They are not production security specifications.
