import assert from "node:assert/strict";
import test from "node:test";

import {
  createShadowHandler,
  type AgentClearanceResult,
  type ShadowObservation,
} from "../src/index.js";

const RESULT: AgentClearanceResult = {
  decision: "allow_with_obligations",
  reasonCodes: ["evidence.sufficient", "policy.bounded_read"],
  criticalObligations: ["urn:agent-clearance:obligation:rate-limit:0.1"],
  obligationsEnforceable: true,
  evidenceProfiles: ["urn:agent-clearance:profile:origin-scoped-mandate:0.1"],
  evidenceResult: "valid",
  verifierVersion: "test-verifier/0.1",
  policyVersion: "pilot-1",
};

function baseOptions(observations: ShadowObservation[]) {
  return {
    deploymentId: "travel-pilot",
    classify: () => ({
      routeTemplate: "/availability/search",
      actionType: "availability.read",
      riskTier: "bounded_read",
    }),
    buildEvaluationInput: (request: Request) => ({
      method: request.method,
      signature: request.headers.get("signature"),
    }),
    evaluate: async () => RESULT,
    fetchUpstream: async () => new Response("incumbent", { status: 403, headers: { "x-origin": "yes" } }),
    incumbentDecision: () => "block" as const,
    writeObservation: async (observation: ShadowObservation) => {
      observations.push(observation);
    },
    now: () => Date.parse("2026-09-03T17:23:45Z"),
    random: () => 0,
    eventId: () => "event-1",
  };
}

test("returns the authoritative response unchanged and records in background", async () => {
  const observations: ShadowObservation[] = [];
  const pending: Promise<unknown>[] = [];
  const expected = new Response("incumbent", { status: 403, headers: { "x-origin": "yes" } });
  const options = {
    ...baseOptions(observations),
    fetchUpstream: async () => expected,
  };
  const handler = createShadowHandler(options);
  const response = await handler(new Request("https://travel.example/availability/search?q=secret"), {
    waitUntil: (promise) => pending.push(promise),
  });

  assert.equal(response, expected);
  assert.equal(response.status, 403);
  assert.equal(await response.text(), "incumbent");
  await Promise.all(pending);
  assert.equal(observations.length, 1);
  const observation = observations[0]!;
  assert.equal(observation.incumbent_decision, "block");
  assert.equal(observation.agent_clearance_decision, "allow_with_obligations");
  assert.equal(observation.occurred_at, "2026-09-03T17:23:00.000Z");
  assert.equal(JSON.stringify(observation).includes("q=secret"), false);
});

test("evaluation failure is indeterminate and never changes an allow", async () => {
  const observations: ShadowObservation[] = [];
  const handler = createShadowHandler({
    ...baseOptions(observations),
    evaluate: async () => {
      throw new Error("contains private evaluator detail");
    },
    fetchUpstream: async () => new Response("ok", { status: 200 }),
    incumbentDecision: () => "allow",
  });

  const response = await handler(new Request("https://travel.example/availability/search"));
  assert.equal(response.status, 200);
  assert.equal(observations[0]!.agent_clearance_decision, "indeterminate");
  assert.equal(observations[0]!.error_class, "evaluation_error");
  assert.equal(JSON.stringify(observations[0]).includes("private evaluator detail"), false);
});

test("timeout aborts evaluation and records indeterminate", async () => {
  const observations: ShadowObservation[] = [];
  const handler = createShadowHandler({
    ...baseOptions(observations),
    evaluationTimeoutMs: 5,
    evaluate: async (_input: unknown, signal: AbortSignal) =>
      new Promise<AgentClearanceResult>((_resolve, reject) => {
        signal.addEventListener("abort", () => reject(new Error("aborted")), { once: true });
      }),
  });

  await handler(new Request("https://travel.example/availability/search"));
  assert.equal(observations[0]!.agent_clearance_decision, "indeterminate");
  assert.equal(observations[0]!.error_class, "timeout");
});

test("unsampled and unclassified requests do not evaluate", async () => {
  let evaluations = 0;
  const observations: ShadowObservation[] = [];
  const handler = createShadowHandler({
    ...baseOptions(observations),
    sampleProbability: 0,
    evaluate: async () => {
      evaluations += 1;
      return RESULT;
    },
  });

  const response = await handler(new Request("https://travel.example/availability/search"));
  assert.equal(response.status, 403);
  assert.equal(evaluations, 0);
  assert.equal(observations.length, 0);
});

test("metrics sink failure never changes the incumbent response", async () => {
  const observations: ShadowObservation[] = [];
  const handler = createShadowHandler({
    ...baseOptions(observations),
    fetchUpstream: async () => new Response("origin", { status: 202 }),
    incumbentDecision: () => "allow",
    writeObservation: async () => {
      throw new Error("sink unavailable");
    },
  });

  const response = await handler(new Request("https://travel.example/availability/search"));
  assert.equal(response.status, 202);
  assert.equal(await response.text(), "origin");
});

test("invalid partner classification is ignored without changing the response", async () => {
  const observations: ShadowObservation[] = [];
  const expected = new Response(null, { status: 204 });
  const handler = createShadowHandler({
    ...baseOptions(observations),
    classify: () => ({
      routeTemplate: "/availability/search?secret=yes",
      actionType: "availability.read",
      riskTier: "bounded_read",
    }),
    fetchUpstream: async () => expected,
  });

  const response = await handler(new Request("https://travel.example/availability/search"));
  assert.equal(response, expected);
  assert.equal(observations.length, 0);
});

test("invalid evaluator output is recorded as indeterminate", async () => {
  const observations: ShadowObservation[] = [];
  const handler = createShadowHandler({
    ...baseOptions(observations),
    evaluate: async () => ({ ...RESULT, reasonCodes: ["private free-form result!"] }),
  });

  await handler(new Request("https://travel.example/availability/search"));
  assert.equal(observations[0]!.agent_clearance_decision, "indeterminate");
  assert.equal(observations[0]!.error_class, "invalid_result");
});

test("partner response-mapping failure cannot change the response", async () => {
  const observations: ShadowObservation[] = [];
  const expected = new Response("origin", { status: 200 });
  const handler = createShadowHandler({
    ...baseOptions(observations),
    fetchUpstream: async () => expected,
    incumbentDecision: () => {
      throw new Error("bad origin mapping");
    },
  });

  const response = await handler(new Request("https://travel.example/availability/search"));
  assert.equal(response, expected);
});

test("a hanging metrics sink is bounded", async () => {
  const observations: ShadowObservation[] = [];
  const handler = createShadowHandler({
    ...baseOptions(observations),
    metricsTimeoutMs: 5,
    writeObservation: async () => new Promise<void>(() => undefined),
  });

  const started = performance.now();
  const response = await handler(new Request("https://travel.example/availability/search"));
  assert.equal(response.status, 403);
  assert.ok(performance.now() - started < 1_000);
});
