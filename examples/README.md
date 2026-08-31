# Protocol examples

These examples are fictional and non-normative. Strings representing digests, keys, evidence, and signatures are placeholders and are not cryptographically valid.

The examples illustrate one bounded availability-search flow:

1. [`challenge.json`](challenge.json) requests request-integrity and delegation evidence.
2. [`presentation.json`](presentation.json) supplies evidence bound to the challenge and request.
3. [`decision.json`](decision.json) permits the read with rate and result-count obligations and requires step-up before reservation.

The examples must not be used as production credentials or copied as security test vectors.
