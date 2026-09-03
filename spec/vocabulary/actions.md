# Action types

Action types are origin-local structured identifiers. They are not a global capability ontology. Agents MUST treat unknown types as unknown, not as substrings of a broader permission.

The strings below are a starter list for the first availability-search workflow. Origins MAY use them, MAY namespace their own (`travel.example:availability.read`), and MUST NOT infer that sharing a string implies a shared policy.

| Type | Intended meaning in the first workflow | Typical decision |
|---|---|---|
| `availability.read` | Bounded inventory or availability search | `allow_with_obligations` |
| `inventory.read` | Bounded catalog or stock read | `allow_with_obligations` |
| `reservation.commit` | Create or confirm a reservation | `step_up` or separate authorization |
| `purchase.commit` | Commit funds or place an order | Out of scope for the first workflow |

Matching is exact. `availability.read` does not grant `reservation.commit`.

Constraints such as `maximum_results` belong on the action object. They are part of what the principal approved and what the enforcement point must apply.
