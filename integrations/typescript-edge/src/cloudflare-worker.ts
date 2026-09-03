import {
  createShadowHandler,
  type AgentClearanceResult,
  type IncumbentDecision,
  type ShadowObservation,
} from "./shadow.js";

interface ServiceBinding {
  fetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response>;
}
interface Env {
  ORIGIN_BASE_URL: string;
  DEPLOYMENT_ID: string;
  SAMPLE_PROBABILITY?: string;
  EVALUATION_TIMEOUT_MS?: string;
  SHADOW_EVALUATOR: ServiceBinding;
  SHADOW_METRICS: ServiceBinding;
}

interface ExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
}

interface EvaluationInput {
  method: string;
  origin: string;
  route_template: string;
  action_type: string;
  risk_tier: string;
  agent_clearance_headers: Record<string, string>;
}

export default {
  async fetch(request: Request, env: Env, context: ExecutionContext): Promise<Response> {
    const handler = createShadowHandler<EvaluationInput>({
      deploymentId: env.DEPLOYMENT_ID,
      sampleProbability: parseNumber(env.SAMPLE_PROBABILITY, 1),
      evaluationTimeoutMs: parseNumber(env.EVALUATION_TIMEOUT_MS, 250),
      classify: (candidate) => {
        const url = new URL(candidate.url);
        if (url.pathname !== "/availability/search") {
          return null;
        }
        return {
          routeTemplate: "/availability/search",
          actionType: "availability.read",
          riskTier: "bounded_read",
        };
      },
      buildEvaluationInput: (candidate, classification) => ({
        method: candidate.method,
        origin: new URL(candidate.url).origin,
        route_template: classification.routeTemplate,
        action_type: classification.actionType,
        risk_tier: classification.riskTier,
        agent_clearance_headers: clearanceHeaders(candidate.headers),
      }),
      evaluate: async (input, signal) => {
        const response = await env.SHADOW_EVALUATOR.fetch("https://shadow-evaluator.internal/evaluate", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify(input),
          signal,
        });
        if (!response.ok) {
          throw new Error(`shadow evaluator returned ${response.status}`);
        }
        return (await response.json()) as AgentClearanceResult;
      },
      fetchUpstream: (candidate) => fetch(rewriteOrigin(candidate, env.ORIGIN_BASE_URL)),
      incumbentDecision: defaultIncumbentDecision,
      writeObservation: async (observation: ShadowObservation) => {
        const response = await env.SHADOW_METRICS.fetch("https://shadow-metrics.internal/events", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify(observation),
        });
        if (!response.ok) {
          throw new Error(`shadow metrics returned ${response.status}`);
        }
      },
    });
    return handler(request, context);
  },
};

function clearanceHeaders(headers: Headers): Record<string, string> {
  const allowed = ["signature", "signature-input", "content-digest", "agent-clearance"];
  const output: Record<string, string> = {};
  for (const name of allowed) {
    const value = headers.get(name);
    if (value !== null) {
      output[name] = value;
    }
  }
  const authorization = headers.get("authorization");
  if (authorization?.startsWith("AgentClearance ")) {
    output.authorization = authorization;
  }
  return output;
}

function rewriteOrigin(request: Request, origin: string): Request {
  const source = new URL(request.url);
  const destination = new URL(origin);
  destination.pathname = source.pathname;
  destination.search = source.search;
  return new Request(destination, request);
}

function defaultIncumbentDecision(response: Response): IncumbentDecision {
  if (response.status === 401) return "challenge";
  if (response.status === 403) return "block";
  if (response.status === 429) return "rate_limit";
  if (response.status >= 200 && response.status < 400) return "allow";
  if (response.status >= 500) return "error";
  return "unknown";
}

function parseNumber(value: string | undefined, fallback: number): number {
  if (value === undefined) return fallback;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new TypeError(`invalid numeric configuration: ${value}`);
  return parsed;
}
