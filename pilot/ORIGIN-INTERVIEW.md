# Origin discovery interview

## Purpose

Find evidence of an origin problem worth solving and determine whether a bounded shadow evaluation is possible. This is a research conversation, not a request for endorsement of the protocol.

Ask for concrete recent behavior. Avoid asking whether the participant “likes the idea” until the workflow is understood.

## Participants

Prefer people responsible for one or more of:

- bot management or WAF policy;
- fraud and abuse;
- identity and authorization;
- developer or platform infrastructure;
- conversion or marketplace integrity; or
- support escalation caused by blocked automation.

## Consent and handling

At the beginning, state how notes will be used and whether the discussion is attributable, anonymized, or confidential. Do not request production credentials, personal data, raw customer traffic, or protected fraud rules.

## Interview guide

### 1. Last concrete event

- Tell us about the most recent legitimate automated request that was blocked, challenged, or mishandled.
- What was the agent trying to do?
- How did you determine later that the request was desirable?
- What happened to the user, origin, inventory, or support team?

### 2. Frequency and value

- How often does this class of request occur?
- Which action is the lowest-consequence useful starting point?
- What is the cost of a false block?
- What is the cost of admitting an abusive request?
- Is this material enough for an owner to prioritize?

### 3. Current path

- Which CDN, WAF, CAPTCHA, API, OAuth, account, and fraud controls are involved?
- Why was a first-party API or ordinary OAuth not sufficient?
- Where is the earliest point at which the origin itself can inspect the request?
- Can the origin retain enough input to reproduce an independent decision?

### 4. Evidence and policy

- What evidence would have changed the decision?
- Does the origin need agent identity, operator accountability, principal backing, delegation, recent presence, rate accountability, or some combination?
- What must remain origin-local?
- Which limits would have to accompany an allow decision?
- Which action requires step-up or separate authorization?

### 5. Privacy and accessibility

- Which identity or task facts may the origin not collect?
- Which facts may not reach the CDN or verifier provider?
- What retention and residency restrictions apply?
- How must a person approve, decline, revoke, or appeal?
- Which accessibility requirements apply to the human alternative and step-up path?

### 6. Evaluation readiness

- Can AgentIsOK run in shadow mode while current controls remain authoritative?
- Which outcome labels are available, and how reliable are they?
- Who approves integration, security review, privacy review, and expansion?
- What is the rollback path?
- What result would justify retaining the integration?

### 7. Alternatives and buying path

- Would a direct API, OAuth profile, Web Bot Auth, incumbent CDN feature, or bilateral integration solve this with less effort?
- Which existing spend or operational burden could this improve?
- Who would own the budget if it became production infrastructure?

## Evidence to record

- Workflow identifier and structured action.
- Consequence tier.
- Actual incident recency and estimated frequency.
- Incumbent decision point and owner.
- Evidence that could change the decision.
- Required obligations and step-up boundary.
- Prohibited disclosures.
- Available labels and known bias.
- Integration point and rollback owner.
- Named internal champion.
- Agreed next action and date.

Do not record raw tasks, customer identifiers, credentials, private keys, or unredacted traffic.

## Qualification rubric

Score each category from 0 to 2:

| Category | 0 | 1 | 2 |
|---|---|---|---|
| Real workflow | Hypothetical | Old or indirect | Recent concrete event |
| Materiality | Immaterial | Uncertain | Measurable cost or opportunity |
| Traffic | None | Emerging | Recurring eligible traffic |
| Origin owner | None | Interested observer | Named decision owner |
| Shadow feasibility | Cannot run | Requires discovery | Safe integration point exists |
| Outcome evidence | No label | Weak proxy | Useful label with known limits |

A promising design partner scores at least 8 of 12 and must have both a concrete workflow and a decision owner. The score is a triage aid, not evidence that a deployment is safe.

## Interview program

- Conduct 10–15 qualified origin-side conversations.
- Interview agent or harness teams separately; do not substitute their demand for origin demand.
- Synthesize patterns only after preserving contradictory evidence.
- Stop or reshape if qualified origins consistently prefer a simpler direct path.
