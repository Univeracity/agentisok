export type IncumbentDecision =
  | "allow"
  | "challenge"
  | "block"
  | "rate_limit"
  | "error"
  | "unknown";

export type ShadowDecision =
  | "allow"
  | "allow_with_obligations"
  | "step_up"
  | "deny"
  | "indeterminate";

export type EvidenceResult = "valid" | "invalid" | "missing" | "indeterminate";

export interface ShadowClassification {
  readonly routeTemplate: string;
  readonly actionType: string;
  readonly riskTier: string;
}

export interface AgentClearanceResult {
  readonly decision: ShadowDecision;
  readonly reasonCodes: readonly string[];
  readonly criticalObligations: readonly string[];
  readonly obligationsEnforceable: boolean;
  readonly evidenceProfiles: readonly string[];
  readonly evidenceResult: EvidenceResult;
  readonly verifierVersion: string;
  readonly policyVersion: string;
}

export interface ShadowObservation {
  readonly schema_version: "0.1";
  readonly event_id: string;
  readonly occurred_at: string;
  readonly deployment_id: string;
  readonly route_template: string;
  readonly action_type: string;
  readonly risk_tier: string;
  readonly sample_probability: number;
  readonly incumbent_decision: IncumbentDecision;
  readonly agent_clearance_decision: ShadowDecision;
  readonly reason_codes: readonly string[];
  readonly critical_obligations: readonly string[];
  readonly obligations_enforceable: boolean;
  readonly verification_latency_ms: number;
  readonly evidence_profiles: readonly string[];
  readonly evidence_result: EvidenceResult;
  readonly outcome_label: "unknown";
  readonly label_source: "unknown";
  readonly verifier_version: string;
  readonly policy_version: string;
  readonly error_class: "none" | "timeout" | "evaluation_error" | "invalid_result";
}

export interface ShadowExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
}

export interface ShadowAdapterOptions<Input> {
  readonly deploymentId: string;
  readonly sampleProbability?: number;
  readonly evaluationTimeoutMs?: number;
  readonly metricsTimeoutMs?: number;
  readonly classify: (request: Request) => ShadowClassification | null;
  readonly buildEvaluationInput: (
    request: Request,
    classification: ShadowClassification,
  ) => Input | Promise<Input>;
  readonly evaluate: (input: Input, signal: AbortSignal) => Promise<AgentClearanceResult>;
  readonly fetchUpstream: (request: Request) => Promise<Response>;
  readonly incumbentDecision: (response: Response) => IncumbentDecision;
  readonly writeObservation: (observation: ShadowObservation) => Promise<void>;
  readonly now?: () => number;
  readonly random?: () => number;
  readonly eventId?: () => string;
}

export type ShadowHandler = (
  request: Request,
  context?: ShadowExecutionContext,
) => Promise<Response>;

interface SettledEvaluation {
  readonly result: AgentClearanceResult;
  readonly errorClass: ShadowObservation["error_class"];
  readonly latencyMs: number;
}

const DECISIONS = new Set<ShadowDecision>([
  "allow",
  "allow_with_obligations",
  "step_up",
  "deny",
  "indeterminate",
]);
const EVIDENCE_RESULTS = new Set<EvidenceResult>([
  "valid",
  "invalid",
  "missing",
  "indeterminate",
]);
const SAFE_IDENTIFIER = /^[a-z][a-z0-9_.:-]{0,255}$/;
const BOUNDED_TOKEN = /^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,127}$/;

export function createShadowHandler<Input>(options: ShadowAdapterOptions<Input>): ShadowHandler {
  const sampleProbability = options.sampleProbability ?? 1;
  const timeoutMs = options.evaluationTimeoutMs ?? 250;
  const metricsTimeoutMs = options.metricsTimeoutMs ?? 250;
  if (!SAFE_IDENTIFIER.test(options.deploymentId) || options.deploymentId.length > 128) {
    throw new TypeError("deploymentId must be a bounded structured identifier");
  }
  if (!(sampleProbability >= 0 && sampleProbability <= 1)) {
    throw new TypeError("sampleProbability must be between 0 and 1");
  }
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0 || timeoutMs > 30_000) {
    throw new TypeError("evaluationTimeoutMs must be between 1 and 30000");
  }
  if (!Number.isFinite(metricsTimeoutMs) || metricsTimeoutMs <= 0 || metricsTimeoutMs > 30_000) {
    throw new TypeError("metricsTimeoutMs must be between 1 and 30000");
  }

  const clock = options.now ?? Date.now;
  const random = options.random ?? Math.random;
  const eventId = options.eventId ?? (() => crypto.randomUUID());

  return async (request: Request, context?: ShadowExecutionContext): Promise<Response> => {
    let shadowRequest: Request | null = null;
    try {
      shadowRequest = request.clone();
    } catch {
      // A consumed request cannot be evaluated safely, but the incumbent still decides.
    }
    const upstreamPromise = options.fetchUpstream(request);
    let classification: ShadowClassification | null = null;
    try {
      classification = options.classify(request);
      if (classification !== null) {
        validateClassification(classification);
      }
    } catch {
      return upstreamPromise;
    }

    if (classification === null || shadowRequest === null) {
      return upstreamPromise;
    }
    try {
      const draw = random();
      if (!Number.isFinite(draw) || draw < 0 || draw >= 1 || draw >= sampleProbability) {
        return upstreamPromise;
      }
    } catch {
      return upstreamPromise;
    }

    const selected = classification;
    const selectedRequest = shadowRequest;
    const evaluationStarted = clock();
    const evaluationPromise = evaluateWithTimeout(
      async (signal) => {
        const input = await options.buildEvaluationInput(selectedRequest, selected);
        return options.evaluate(input, signal);
      },
      timeoutMs,
      clock,
      evaluationStarted,
    );

    const upstreamResponse = await upstreamPromise;
    const background = recordObservation(
      options,
      selected,
      upstreamResponse,
      evaluationPromise,
      sampleProbability,
      eventId,
      clock,
      metricsTimeoutMs,
    ).catch(() => undefined);

    if (context) {
      try {
        context.waitUntil(background);
      } catch {
        // A platform scheduling failure cannot change the incumbent response.
      }
    } else {
      await background;
    }

    return upstreamResponse;
  };
}

async function evaluateWithTimeout(
  work: (signal: AbortSignal) => Promise<AgentClearanceResult>,
  timeoutMs: number,
  clock: () => number,
  started: number,
): Promise<SettledEvaluation> {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<SettledEvaluation>((resolve) => {
    timer = setTimeout(() => {
      controller.abort("shadow evaluation timeout");
      resolve(indeterminate("timeout", clock() - started));
    }, timeoutMs);
  });
  const evaluation = Promise.resolve()
    .then(() => work(controller.signal))
    .then((result) => {
      try {
        validateResult(result);
      } catch {
        return indeterminate("invalid_result", clock() - started);
      }
      return { result, errorClass: "none" as const, latencyMs: elapsed(clock, started) };
    }, () => indeterminate("evaluation_error", clock() - started));

  const settled = await Promise.race([evaluation, timeout]);
  if (timer !== undefined) {
    clearTimeout(timer);
  }
  return settled;
}

async function recordObservation<Input>(
  options: ShadowAdapterOptions<Input>,
  classification: ShadowClassification,
  upstreamResponse: Response,
  evaluationPromise: Promise<SettledEvaluation>,
  sampleProbability: number,
  eventId: () => string,
  clock: () => number,
  metricsTimeoutMs: number,
): Promise<void> {
  const evaluation = await evaluationPromise;
  const result = evaluation.result;
  const generatedEventId = eventId();
  if (typeof generatedEventId !== "string" || !BOUNDED_TOKEN.test(generatedEventId)) {
    return;
  }
  const observation: ShadowObservation = Object.freeze({
    schema_version: "0.1",
    event_id: generatedEventId,
    occurred_at: coarsenedUtcMinute(clock()),
    deployment_id: options.deploymentId,
    route_template: classification.routeTemplate,
    action_type: classification.actionType,
    risk_tier: classification.riskTier,
    sample_probability: sampleProbability,
    incumbent_decision: safeIncumbentDecision(options.incumbentDecision(upstreamResponse)),
    agent_clearance_decision: result.decision,
    reason_codes: [...result.reasonCodes],
    critical_obligations: [...result.criticalObligations],
    obligations_enforceable: result.obligationsEnforceable,
    verification_latency_ms: evaluation.latencyMs,
    evidence_profiles: [...result.evidenceProfiles],
    evidence_result: result.evidenceResult,
    outcome_label: "unknown",
    label_source: "unknown",
    verifier_version: result.verifierVersion,
    policy_version: result.policyVersion,
    error_class: evaluation.errorClass,
  });
  try {
    await withTimeout(options.writeObservation(observation), metricsTimeoutMs);
  } catch {
    // Metrics failure must never change the authoritative response.
  }
}

function validateClassification(value: ShadowClassification): void {
  if (
    value.routeTemplate.length > 512 ||
    !value.routeTemplate.startsWith("/") ||
    value.routeTemplate.includes("?") ||
    value.routeTemplate.includes("#")
  ) {
    throw new TypeError("routeTemplate must be a path template without a query");
  }
  if (!SAFE_IDENTIFIER.test(value.actionType) || !SAFE_IDENTIFIER.test(value.riskTier)) {
    throw new TypeError("actionType and riskTier must be bounded structured identifiers");
  }
}

function validateResult(value: AgentClearanceResult): void {
  if (!DECISIONS.has(value.decision) || !EVIDENCE_RESULTS.has(value.evidenceResult)) {
    throw new TypeError("evaluator returned an invalid decision or evidence result");
  }
  if (
    !Array.isArray(value.reasonCodes) ||
    !Array.isArray(value.criticalObligations) ||
    !Array.isArray(value.evidenceProfiles) ||
    typeof value.obligationsEnforceable !== "boolean"
  ) {
    throw new TypeError("evaluator returned an invalid result shape");
  }
  if (value.reasonCodes.length > 32 || value.criticalObligations.length > 32 || value.evidenceProfiles.length > 16) {
    throw new TypeError("evaluator returned too many result identifiers");
  }
  if (
    new Set(value.reasonCodes).size !== value.reasonCodes.length ||
    new Set(value.criticalObligations).size !== value.criticalObligations.length ||
    new Set(value.evidenceProfiles).size !== value.evidenceProfiles.length
  ) {
    throw new TypeError("evaluator returned duplicate result identifiers");
  }
  for (const code of value.reasonCodes) {
    if (!SAFE_IDENTIFIER.test(code)) {
      throw new TypeError("evaluator returned an unsafe reason code");
    }
  }
  for (const item of [...value.criticalObligations, ...value.evidenceProfiles]) {
    if (typeof item !== "string" || item.length === 0 || item.length > 512) {
      throw new TypeError("evaluator returned an invalid identifier");
    }
  }
  if (!BOUNDED_TOKEN.test(value.verifierVersion) || !BOUNDED_TOKEN.test(value.policyVersion)) {
    throw new TypeError("evaluator versions must be bounded structured identifiers");
  }
}

function safeIncumbentDecision(value: IncumbentDecision): IncumbentDecision {
  switch (value) {
    case "allow":
    case "challenge":
    case "block":
    case "rate_limit":
    case "error":
    case "unknown":
      return value;
    default:
      return "unknown";
  }
}

function indeterminate(
  errorClass: Exclude<ShadowObservation["error_class"], "none">,
  latencyMs: number,
): SettledEvaluation {
  return {
    result: {
      decision: "indeterminate",
      reasonCodes: ["evaluation.indeterminate"],
      criticalObligations: [],
      obligationsEnforceable: false,
      evidenceProfiles: [],
      evidenceResult: "indeterminate",
      verifierVersion: "unavailable",
      policyVersion: "unavailable",
    },
    errorClass,
    latencyMs: Math.max(0, Math.round(latencyMs)),
  };
}

function elapsed(clock: () => number, started: number): number {
  return Math.max(0, Math.round(clock() - started));
}

function coarsenedUtcMinute(timestampMs: number): string {
  return new Date(Math.floor(timestampMs / 60_000) * 60_000).toISOString();
}

async function withTimeout(promise: Promise<void>, timeoutMs: number): Promise<void> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<void>((resolve) => {
    timer = setTimeout(resolve, timeoutMs);
  });
  await Promise.race([promise.catch(() => undefined), timeout]);
  if (timer !== undefined) {
    clearTimeout(timer);
  }
}
