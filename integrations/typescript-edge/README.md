# TypeScript edge shadow adapter

A Fetch-standard adapter for comparing an Agent Clearance decision with an origin's incumbent response without changing that response.

> Pre-alpha pilot software. It does not implement a production verifier and must not enforce Agent Clearance decisions.

## Invariants

- The upstream response object is returned unchanged.
- Evaluation runs concurrently and has a hard timeout.
- A Worker `waitUntil` context keeps metrics off the response latency path.
- Evaluation and metrics failures never change the upstream result.
- Only a fixed, minimized observation reaches the metrics sink.
- No AgentIsOK service, account, directory, or API is required.
- The evaluator and metrics sink can be origin-controlled service bindings.

## Install and test

```bash
cd integrations/typescript-edge
npm ci
npm test
```

The package has no runtime dependencies. TypeScript, Node types, and Wrangler are development dependencies.

## Core use

```ts
import { createShadowHandler } from "@agentisok/edge-shadow";

const handler = createShadowHandler({
  deploymentId: "origin-pilot",
  sampleProbability: 0.01,
  evaluationTimeoutMs: 250,
  metricsTimeoutMs: 250,
  classify: (request) => ({
    routeTemplate: "/availability/search",
    actionType: "availability.read",
    riskTier: "bounded_read",
  }),
  buildEvaluationInput: (request, classification) => ({
    method: request.method,
    route: classification.routeTemplate,
    signature: request.headers.get("signature"),
  }),
  evaluate: (input, signal) => originControlledEvaluator(input, signal),
  fetchUpstream: (request) => fetch(request),
  incumbentDecision: (response) => response.status === 403 ? "block" : "allow",
  writeObservation: (observation) => originControlledMetrics.write(observation),
});
```

`buildEvaluationInput` is an explicit disclosure boundary. Do not return a whole `Request`, cookies, application authorization, bodies, full URLs, or query strings unless a reviewed origin-local verifier genuinely requires them. Raw evidence must never be passed to `writeObservation`.

When no `waitUntil` context is supplied, the handler waits for bounded evaluation and metrics completion before returning so observations are not silently lost. Edge deployments should supply the platform context to keep this work off the authoritative response path.

## Cloudflare Worker example

[`src/cloudflare-worker.ts`](src/cloudflare-worker.ts) shows one deployment. It:

- shadows only `/availability/search`;
- forwards the original request to `ORIGIN_BASE_URL`;
- sends an allowlisted set of Agent Clearance headers to an origin-controlled evaluator service binding;
- sends only the metrics contract to an origin-controlled metrics binding; and
- always returns the origin response.

Copy `wrangler.example.toml` to a private deployment configuration, replace every placeholder, create both service bindings, test the kill switch, and then deploy with Wrangler. Using Cloudflare is optional; the core handler depends only on Fetch-standard `Request` and `Response` objects.

The example's default HTTP status mapping is illustrative. A design partner must map its actual WAF and application outcomes rather than assume every `401`, `403`, or `429` has the same meaning.

## Metrics

The emitted object matches the field set in [`../../pilot/METRICS.md`](../../pilot/METRICS.md). It intentionally excludes:

- request or response bodies;
- full URLs and query strings;
- civil, account, pairwise-subject, presenter-key, mandate, nonce, signature, and artifact values;
- cookies and general authorization headers; and
- free-form errors.

The Cloudflare example forwards an `Authorization` header only when its scheme is exactly `AgentClearance`.

## What remains partner-specific

- Route-to-action classification.
- The origin-controlled evaluator implementation.
- Trust and policy configuration.
- Incumbent decision mapping.
- Outcome-label joins.
- Retention and deletion.
- Sampling thresholds and rollout approval.

Those are explicit configuration points because hiding them in a universal hosted service would undermine origin authority and provider exit.
