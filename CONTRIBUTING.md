# Contributing to AgentIsOK

AgentIsOK welcomes implementation, protocol, security, privacy, accessibility, abuse-prevention, governance, research, and documentation contributions.

The project is pre-alpha. Early participation should challenge assumptions and produce interoperability evidence rather than rush unreviewed code into production.

## Before contributing

Read:

- [PRINCIPLES.md](PRINCIPLES.md);
- [SCOPE.md](SCOPE.md);
- [ARCHITECTURE.md](ARCHITECTURE.md);
- [THREAT-MODEL.md](THREAT-MODEL.md);
- [IPR-POLICY.md](IPR-POLICY.md); and
- [GOVERNANCE.md](GOVERNANCE.md).

Security vulnerabilities follow [SECURITY.md](SECURITY.md), not the public issue process.

## Ways to participate

- Describe a real origin workflow where desirable agents are blocked or challenged.
- Review challenge, evidence, privacy, decision, and obligation semantics.
- Add protocol examples or negative conformance vectors.
- Implement an independent origin verifier or agent responder.
- Design an adapter for an existing evidence profile.
- Test intermediary, replay, revocation, and concurrency behavior.
- Review accessibility and human step-up flows.
- Analyze gatekeeper concentration or governance failure modes.
- Improve explanations and translations.

## Proposing protocol changes

Open an issue before a large protocol change. Include:

1. The concrete problem and affected participants.
2. A real or plausible deployment example.
3. The proposed semantics, including failure behavior.
4. Security, privacy, accessibility, and competition effects.
5. Alternatives, especially composition with existing standards.
6. Backward-compatibility and versioning effects.
7. How at least two independent implementations could support the change.

Protocol pull requests should update the specification, schemas, examples, conformance vectors, threat model, and whitepaper where relevant.

## Pull requests

- Keep changes focused and explain their purpose.
- Use clear normative language only in specification documents.
- Add positive and negative tests for behavioral changes.
- Do not include real credentials, personal data, or sensitive origin logs.
- Cite primary standards and specifications for technical claims.
- Preserve provider-neutral terminology in protocol surfaces.
- Ensure public files do not contain private research or unpublished partner information.

## Commit sign-off

Every commit must be signed off with the Developer Certificate of Origin declaration by adding:

```text
Signed-off-by: Your Name <your-email@example.com>
```

Git can add this with `git commit -s`. The sign-off certifies the contribution under the [Developer Certificate of Origin 1.1](https://developercertificate.org/).

## License and patent terms

Unless a file says otherwise, contributions are accepted under the repository's [Apache License 2.0](LICENSE), including its patent provisions. Specification contributors also follow [IPR-POLICY.md](IPR-POLICY.md).

Do not submit material you lack the right to contribute. Identify third-party material and its license in the pull request.

## Review expectations

Review evaluates:

- consistency with project principles and scope;
- implementability by parties other than AgentIsOK;
- protocol clarity and deterministic failure behavior;
- security and privacy impact;
- origin and agent operational burden;
- accessibility and recourse;
- ecosystem concentration and provider-exit impact; and
- test and interoperability evidence.

Maintainers may request design discussion or an implementation experiment before accepting a normative feature.

## Conduct

Participate respectfully and focus criticism on ideas, behavior, evidence, and system effects. Harassment, discrimination, threats, deliberate exposure of private information, and sustained disruption are not acceptable.

Technical disagreement is expected. Good-faith objections—especially about safety, privacy, accessibility, market power, or implementation feasibility—must not be dismissed as disloyalty to the project.

## Public and private information

Repository discussions are public once the project launches. Do not post private correspondence, partner data, security details under embargo, personal information, or confidential research without authorization.
