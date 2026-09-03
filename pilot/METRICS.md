# Shadow-evaluation metrics contract

## Purpose

Measure whether AgentIsOK improves an origin's decision about desirable agent traffic without worsening abuse, privacy, reliability, or operational cost.

The metrics contract is origin-controlled. It does not require central AgentIsOK telemetry.

## Pre-register the hypotheses

Before live shadowing, the origin records:

- eligible route template and action type;
- incumbent decision definitions;
- sources and limitations of outcome labels;
- success metrics and minimum meaningful change;
- abuse and reliability guardrails;
- sample plan and analysis interval;
- retention and deletion schedule; and
- the person authorized to stop or expand the evaluation.

Thresholds are partner-specific. The protocol must not encode a universal acceptable abuse rate.

## Event schema

A shadow observation contains only:

The normative pilot shape is the [JSON Schema](schema/shadow-observation.schema.json); a non-normative [example observation](examples/shadow-observation.json) is provided for integration tests.

| Field | Meaning |
|---|---|
| `schema_version` | Metrics contract version |
| `event_id` | Random evaluation-local identifier |
| `occurred_at` | Coarsened UTC timestamp |
| `deployment_id` | Origin-local deployment label |
| `route_template` | Template such as `/availability/search`, never a full URL |
| `action_type` | Structured action such as `availability.read` |
| `risk_tier` | Origin-local coarse tier |
| `sample_probability` | Probability used to sample this event |
| `incumbent_decision` | `allow`, `challenge`, `block`, `rate_limit`, `error`, or `unknown` |
| `agent_clearance_decision` | Protocol decision value |
| `reason_codes` | Coarse public reason codes only |
| `critical_obligations` | Obligation type identifiers, without subject values |
| `obligations_enforceable` | Whether the deployment could enforce every critical obligation |
| `verification_latency_ms` | Local evaluation duration |
| `evidence_profiles` | Profile identifiers, not evidence values |
| `evidence_result` | `valid`, `invalid`, `missing`, or `indeterminate` |
| `outcome_label` | Partner-defined result or `unknown` |
| `label_source` | Coarse provenance such as `support_review`, `account_outcome`, or `unknown` |
| `verifier_version` | Reproducible implementation version |
| `policy_version` | Origin policy version |
| `error_class` | Coarse operational class with no stack trace or private claim |

## Prohibited fields

The metrics sink must reject or strip:

- natural-language tasks or prompts;
- request and response bodies;
- full URLs, query strings, or free-form referrers;
- civil identity, email, account, or payment identifiers;
- pairwise subject, presenter key, mandate, challenge, nonce, signature, or artifact values;
- IP addresses or raw user-agent strings;
- cookies, authorization headers, or credentials;
- issuer payloads and fraud-model features; and
- unbounded free-form error text.

Evidence needed for origin reconstruction remains in protected origin storage under its own retention policy. It does not enter the comparative metrics dataset.

## Core measures

### Decision matrix

Count weighted observations for every incumbent and AgentIsOK decision pair. Sampling weights use `1 / sample_probability` where appropriate.

The important disagreements are:

- incumbent challenges or blocks while AgentIsOK would allow with enforceable obligations;
- incumbent allows while AgentIsOK denies or is indeterminate;
- AgentIsOK requires step-up for an action the incumbent allows; and
- either system produces an operational error.

### Authorized-task recovery

Among requests labeled as desirable through an agreed origin process, estimate the portion currently challenged or blocked that AgentIsOK would admit with enforceable obligations.

Do not call this a false-positive reduction when the desirable label is unknown or inferred only from AgentIsOK evidence.

### Abuse non-inferiority

Among requests with usable abuse or invalid-action labels, compare the incumbent admission rate with the hypothetical AgentIsOK admission rate. Report uncertainty and label coverage.

An apparent conversion improvement does not justify expansion if the abuse guardrail is crossed.

### Friction

Measure challenge, step-up, abandonment, and completion rates for eligible flows. In pure shadow mode, AgentIsOK step-up is hypothetical and must be labeled as such.

### Reliability and latency

Report evaluation success, `indeterminate`, timeout, and error rates plus p50, p95, and p99 verification latency. Incumbent responses remain authoritative even when evaluation times out.

### Privacy and operational cost

Record prohibited-field incidents, retention compliance, decision-reconstruction success, integration hours, on-call events, and support burden.

## Label discipline

Outcome labels are often delayed and biased. Every report states:

- what the label actually observes;
- which traffic lacks labels;
- the delay between request and label;
- whether human review was blinded to the AgentIsOK decision;
- potential selection bias; and
- confidence intervals or an explicit reason they are unavailable.

Unknown labels remain unknown. They are not counted as desirable or abusive to improve the result.

## Default minimization

Suggested starting defaults, subject to origin policy:

- evaluate one action only;
- coarsen timestamps to at least one minute before export;
- keep event-level comparative metrics no longer than needed for the agreed analysis;
- retain aggregate results separately from evidence;
- disable centralized collection; and
- require explicit review before adding a field.

## Result report

The final report includes:

1. Workflow and consequence boundary.
2. Deployment and sampling design.
3. Label sources and limitations.
4. Decision matrix and core measures.
5. Abuse, privacy, and reliability guardrails.
6. Decision-reconstruction results.
7. Operational effort.
8. Deviations from the pre-registered plan.
9. Continue, reshape, or stop decision made by the origin.

Publish only with partner approval. A private result can still guide protocol design, but public claims must be limited to evidence the partner authorizes for release.
