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

Requires Node.js 24+. This is a private source package in the monorepo, not a published npm install. The package name in the example below assumes a local workspace/package link; inside this checkout, import from `src/index.ts` or the compiled `dist/src/index.js`.

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

The adapter validates result types and bounded identifiers and snapshots results before waiting for the upstream response. It rejects free-form profile/obligation values and query strings in those fields. This is shape validation, not a general personal-data scrubber: an account ID can look like a valid token. The origin must supply reviewed route templates, version labels, and profile identifiers.

When no `waitUntil` context is supplied, the handler waits for bounded evaluation and metrics completion before returning so observations are not silently lost. Edge deployments should supply the platform context to keep this work off the authoritative response path.

## Cloudflare Worker example

[`src/cloudflare-worker.ts`](src/cloudflare-worker.ts) shows one deployment. It:

- shadows only `/availability/search`;
- forwards the original request to `ORIGIN_BASE_URL`;
- sends an allowlisted set of Agent Clearance headers to an origin-controlled evaluator service binding;
- sends only the metrics contract to an origin-controlled metrics binding; and
- always returns the origin response.

Copy `wrangler.example.toml` to a private deployment configuration, replace every placeholder, create both service bindings, test the kill switch, and then deploy with Wrangler. Using Cloudflare is optional; the core handler depends only on Fetch-standard `Request` and `Response` objects.

This example is comparison plumbing, not a complete Agent Clearance verifier. It forwards header metadata from `/availability/search`; it does not collect a presentation POST body, issue a challenge, or redeem an artifact. Those headers alone cannot verify a body digest or mandate. Before a real pilot, provide an origin-controlled evaluator with the exact signed bytes, original target, stored challenge, and trust/policy state through an explicitly reviewed local path. If that evidence is unavailable, return missing evidence or `indeterminate`, never infer a valid mandate from the headers. Keep those bytes out of the metrics binding.

The example's default HTTP status mapping is illustrative. A design partner must map its actual WAF and application outcomes rather than assume every `401`, `403`, or `429` has the same meaning.

Timeouts bound how long the adapter waits. Evaluators must honor the abort signal to stop their own work; metrics sinks must implement their own network cancellation. Input preparation that finishes after the evaluation timeout does not start an evaluator call.

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
