# Security Policy

## Current status

AgentIsOK is pre-alpha design and interoperability work. The protocol and examples are incomplete, have not received an independent security assessment, and must not be used to authorize production actions.

There are currently no supported production versions.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could create exploitation risk.

Once private vulnerability reporting is enabled, use the reporting flow from the repository's **Security** tab. If that option is unavailable, contact a repository maintainer privately through the Univeracity organization to establish a secure reporting channel before sending sensitive details.

Before changing the repository to public visibility, maintainers must enable private vulnerability reporting and verify that the reporting link works for a non-collaborator. GitHub does not expose that reporting feature while this repository remains private.

Include when possible:

- affected document, schema, implementation, or commit;
- threat and likely impact;
- reproduction steps or a proof of concept;
- assumptions and deployment conditions;
- suggested mitigations; and
- whether the issue is already public or under active exploitation.

Do not include real credentials, personal data, or third-party confidential information.

## Response process

Maintainers will attempt to:

1. Acknowledge receipt and establish a private coordination channel.
2. Assess whether the report affects the protocol, an implementation, or both.
3. Identify affected parties and safe mitigations.
4. Coordinate fixes and disclosure proportionate to exploitation risk.
5. Publish a security advisory and protocol clarification when appropriate.

Because the project is new and volunteer capacity may vary, this document does not promise a fixed response time. Reporters should state any disclosure deadline.

## Security design work

Non-embargoed design weaknesses belong in public issues and should update [THREAT-MODEL.md](THREAT-MODEL.md), the protocol specification, and conformance vectors together.

Particularly useful reviews include:

- signature coverage and canonicalization;
- nonce replay and concurrent redemption;
- delegation attenuation and confused-deputy behavior;
- issuer and metadata substitution;
- parser differentials;
- privacy and correlation;
- policy obligation enforcement;
- fail-open and downgrade paths; and
- centralization or registry-capture risks.

## Safe-harbor intent

The project supports good-faith security research that avoids privacy violations, service disruption, extortion, and unnecessary data access. A formal legal safe-harbor policy has not yet been adopted; researchers should obtain authorization before testing systems they do not own.
