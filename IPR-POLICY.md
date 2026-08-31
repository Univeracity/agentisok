# AgentIsOK Contribution and IPR Policy

## Purpose

AgentIsOK is intended to be implementable by competing open and commercial implementations without permission from a mandatory gatekeeper. Clear copyright and patent terms are necessary to make that promise credible.

This policy describes the project's initial contribution expectations. It is not legal advice, and the project may seek independent legal review before formal standards submission or creation of a certification program.

## Repository license

Unless a file states otherwise, repository contents are licensed under the [Apache License 2.0](LICENSE). This includes source code, specification text, documentation, examples, schemas, and test material.

The Apache License includes copyright permissions and an express patent license from contributors for patent claims necessarily infringed by their contributions, subject to its terms.

## Contribution certification

Contributors must sign off commits under the [Developer Certificate of Origin 1.1](https://developercertificate.org/). The sign-off represents that the contributor has the right to submit the work under the project's license.

The project does not currently require a copyright assignment or contributor license agreement. Contributors retain their copyright while licensing contributions under Apache-2.0. The steward does not receive exclusive ownership and cannot withdraw the open rights already granted to recipients.

## Patent disclosure expectation

A contributor participating in protocol design must disclose any patent or pending patent application personally known to the contributor that the contributor reasonably believes contains claims essential to implementing the proposed contribution.

Disclosure should occur as early as practical and must not include confidential information the contributor is not authorized to reveal. Disclosure is not itself a legal conclusion about validity, infringement, or essentiality.

Contributors must not knowingly steer the protocol toward an undisclosed encumbered mechanism in order to obtain licensing leverage over implementations.

## Royalty-free objective

The project intends the protocol to be implementable on a royalty-free basis. Features known to require discriminatory, field-of-use, per-implementation, or per-transaction patent royalties are presumptively unsuitable for the core protocol.

If a potentially essential claim is disclosed, maintainers should:

1. Record the disclosure publicly when legally possible.
2. Seek an unencumbered technical alternative.
3. Request a clear royalty-free, worldwide, nonexclusive implementation commitment from the rights holder if the feature remains necessary.
4. Obtain legal and standards-process advice before adoption.

The repository license does not by itself replace the IPR policy of a future standards organization. Contributions taken into an external standards venue will also follow that venue's rules.

## Standards submissions

Material submitted from this project to an external standards organization should:

- preserve attribution and repository history;
- use a venue with public participation and a credible royalty-free or appropriately protective IPR framework;
- disclose known relevant claims as required by that venue;
- avoid making AgentIsOK trademarks, services, registries, or infrastructure normative; and
- retain independent implementability as an explicit requirement.

No maintainer may make a patent or licensing commitment on behalf of another contributor without authority.

## Third-party material

Third-party code, text, schemas, or test vectors must have a compatible license and clear provenance. Submissions must identify copied or adapted material. Links and factual citations are preferred over unnecessary reproduction.

Dependencies with restrictive, source-available-only, noncommercial, or field-of-use terms must not be required by the open protocol or its conformance suite.

## Trademarks

The Apache License does not grant trademark rights except as necessary for reasonable description of the origin of a work. AgentIsOK and `AI OK` names or marks may be governed separately.

Trademark policy must not prevent truthful statements that an implementation supports the protocol. Any official compatibility mark should be available under public, objective, nondiscriminatory criteria and must not become a required commercial gate.

## Conformance artifacts

Public schemas, examples, and conformance vectors are licensed to permit use by independent implementations. Test access must not depend on a commercial account. Private test cases may supplement abuse testing but cannot be the sole basis for ordinary protocol compatibility.

## Changes to this policy

Changes follow [GOVERNANCE.md](GOVERNANCE.md). A change that weakens royalty-free implementation, permits unilateral relicensing, or creates a mandatory proprietary dependency requires prominent notice, extended public review, and an explicit analysis of ecosystem-capture risk.
