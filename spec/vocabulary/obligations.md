# Core obligations

Unknown **critical** obligations fail closed. Unknown non-critical obligations are ignored. `critical` defaults to `true`.

These five types are the draft `0.1` core. A first enforcement point SHOULD implement all of them. Origins SHOULD NOT emit other critical types until cooperating enforcement points understand them.

## `urn:agent-clearance:obligation:rate-limit:0.1`

```json
{
  "type": "urn:agent-clearance:obligation:rate-limit:0.1",
  "critical": true,
  "parameters": {
    "requests": 20,
    "window_seconds": 3600,
    "bucket": "origin_pairwise_subject"
  }
}
```

`bucket` is `origin_pairwise_subject`, `presenter_key`, or `origin`. Cross-origin buckets are not permitted.

## `urn:agent-clearance:obligation:maximum-results:0.1`

```json
{
  "type": "urn:agent-clearance:obligation:maximum-results:0.1",
  "critical": true,
  "parameters": {
    "count": 100
  }
}
```

The application MUST NOT return more than `count` items for this request.

## `urn:agent-clearance:obligation:one-time:0.1`

```json
{
  "type": "urn:agent-clearance:obligation:one-time:0.1",
  "critical": true,
  "parameters": {
    "challenge_id": "urn:uuid:0d191f2f-73ae-4d41-b662-e1f45a968762"
  }
}
```

The bound request may execute once for this challenge.

## `urn:agent-clearance:obligation:action-restriction:0.1`

```json
{
  "type": "urn:agent-clearance:obligation:action-restriction:0.1",
  "critical": true,
  "parameters": {
    "actions": ["availability.read"]
  }
}
```

Only listed action types may proceed under this decision.

## `urn:agent-clearance:obligation:step-up-before:0.1`

```json
{
  "type": "urn:agent-clearance:obligation:step-up-before:0.1",
  "critical": true,
  "parameters": {
    "action": "reservation.commit"
  }
}
```

A later request whose action is `parameters.action` MUST NOT proceed on this clearance artifact. It needs a new challenge or current approval.

## Composition

If two obligations conflict, the enforcement point applies the intersection (the tighter bound) or rejects. It MUST NOT pick the looser bound.

If the enforcement point cannot apply a critical obligation, it rejects the request even when verification succeeded. Convenience middleware that understands only rate limits MUST fail closed on `maximum-results` rather than dropping that obligation.
