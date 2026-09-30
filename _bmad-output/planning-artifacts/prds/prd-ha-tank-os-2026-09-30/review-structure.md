# Editorial Structure Review — ha-tank-os PRD

## Verdict

The document has a coherent chain-top PRD structure: vision, target user, glossary, functional requirements, exclusions, initial scope, metrics, guardrails, and open questions. The addendum is correctly separated because it contains research notes and candidate detail rather than a second requirements source.

## Findings

- **PRESERVE** The explicit Home Assistant ecosystem-first principle near the vision; it is a product thesis and should remain prominent.
- **PRESERVE** The separate addendum; moving its research detail into the PRD would reduce decision clarity.
- **CONDENSE** Repeated explanations of “no inference” only if the document grows substantially; current repetition reinforces a safety-critical boundary.
- **MOVE** Architecture-level open questions into the later architecture artifact when that artifact exists; retain a short pointer in the PRD.
