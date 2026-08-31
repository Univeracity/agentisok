# AgentIsOK Governance

## Purpose

AgentIsOK exists to develop an open agent-clearance protocol and interoperable implementations. Governance must preserve origin authority, implementation competition, privacy, and the ability to operate without a mandatory central gatekeeper.

This is the initial governance model. It is intentionally lightweight while participation is small and is expected to become more distributed as independent implementers join.

## Governance principles

- Technical decisions are made in public except for embargoed security matters.
- The protocol specification, not one implementation's behavior, is normative.
- Implementations compete on quality while sharing interoperability requirements.
- Commercial participation is welcome, but payment cannot buy protocol privileges or qualification.
- Decisions consider origins, agents, represented principals, issuers, implementers, and people affected by automated access.
- Privacy, accessibility, abuse resistance, provider exit, and ecosystem concentration are design concerns.
- No permanent protocol role is reserved for Univeracity or an AgentIsOK-operated service.

## Participation roles

### Contributors

Anyone participating through issues, reviews, design discussion, documentation, tests, research, or code.

### Maintainers

Contributors trusted to review and merge changes within documented areas. Maintainers are expected to disclose material conflicts, apply the contribution and IPR policies consistently, and prioritize protocol interoperability over implementation advantage.

### Stewards

Maintainers responsible for releases, repository administration, security coordination, and governance continuity. Initial stewardship rests with Univeracity contributors because the project is new. Stewardship does not grant unilateral ownership of the open protocol.

### Future technical steering committee

Once the project has at least six sustained maintainers representing at least three independent organizations or unaffiliated constituencies, the project should establish a technical steering committee through a public proposal.

The committee design should ensure:

- no organization controls more than one third of voting seats;
- at least one seat represents independent or user-interest expertise;
- terms and selection processes are published;
- conflicts and recusals are recorded; and
- protocol, registry, trademark, and commercial-service decisions remain distinguishable.

## Decision process

### Routine changes

Maintainers merge routine corrections and implementation changes after review under normal repository practice.

### Protocol and governance changes

Substantive changes require:

1. A public issue describing the problem, alternatives, compatibility effects, privacy and security effects, and implementation evidence.
2. A pull request containing the proposed normative change and tests or examples where applicable.
3. A review period ordinarily no shorter than 14 days.
4. Documented resolution of material objections or an explicit record of unresolved tradeoffs.
5. Approval from at least two maintainers when the project has enough active maintainers.

The preferred decision model is reasoned consensus. Consensus does not require unanimity, but objections involving security, privacy, competition, or implementability must receive a written response.

### Security exceptions

Embargoed fixes may be developed privately when public discussion would materially increase exploitation risk. After coordinated release, the project should publish the change, impact, and decision record to the extent safe.

## Normative authority

Normative protocol behavior comes from versioned specifications and adopted registries. Reference software is evidence of implementability, not the source of unwritten requirements.

An implementation must not be considered nonconforming merely because it differs internally from the AgentIsOK reference implementation.

## Registries and qualification

Any shared registry needed for protocol interoperability must publish:

- the purpose and exact semantics of each entry;
- objective inclusion, update, suspension, and removal criteria;
- review time expectations;
- decision makers and conflicts;
- decision records;
- an appeal path;
- machine-readable export; and
- a path for independent mirrors where technically possible.

Protocol identifier registration must not be confused with endorsement. Evidence-issuer qualification, if offered, must remain optional and origin-overridable.

No registry may require purchase of hosting, verification, certification, or unrelated commercial services as a condition of technically valid registration.

## Conformance and marks

The conformance suite and its expected results are public. Any formal compatibility mark must correspond to a published version and observable test criteria.

Trademark rules may prevent misleading use of an official mark, but they must not prohibit truthful statements that software independently implements the protocol. A formal mark cannot be the only way to interoperate.

## Conflicts of interest

Maintainers and decision makers disclose material employment, investment, customer, issuer, verifier, or platform interests when they could reasonably affect a decision. Disclosure does not automatically require recusal; the remaining maintainers decide and record whether recusal is appropriate.

## Appeals

A contributor may request reconsideration when a process was not followed, relevant evidence was ignored, or a registry or conformance decision was applied inconsistently. Appeals are public unless they contain embargoed security or protected personal information.

Before a steering committee exists, uninvolved maintainers review appeals. The future governance model should provide an independent escalation path.

## Forks and provider exit

The Apache-2.0 license permits independent implementation and forking. Project infrastructure should use exportable formats and public history so governance failure does not make the protocol or implementation unusable.

Forkability is a final safeguard, not a substitute for responsive governance.

## Changing this document

Changes follow the substantive decision process above. Proposals that reduce independent implementability, require a central service, or concentrate registry control must explicitly explain why less centralized alternatives are insufficient and how capture risk is mitigated.
