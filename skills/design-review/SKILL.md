---
name: design-review
description: Automatically invoked by design-docs or factory-workflow at Stage 4a to independently critique the system and code design, resolve technical findings through the orchestrator, and prepare a concise concept-labelled human decision brief before approval and slicing.
---

# Design review

Review the proposed design, not its author's confidence. The goal is the simplest sufficient design and a human who understands the trade-offs. The orchestrator must dispatch a fresh reviewer subagent, without the designer's inherited conversation or hidden reasoning. If subagents are unavailable, use a separate fresh session. If neither is possible, report INVESTIGATE and stop; self-review is not an independent gate. The reviewer receives the original requirements, proposed design and affected code, not the designer's conversational rationale. Record the actual context and any prior exposure. Do not implement code, silently rewrite the design, or approve on the user's behalf.

## 1. Gather evidence

Read the feature spec / story, PRODUCT.md, CONTEXT.md when present, .pipeline/system-design.md, .pipeline/context.md when present, and the actual affected code, tests, schemas and deployment configuration. Identify missing evidence explicitly. If the design or requirements are missing, stop with INVESTIGATE.

Read the local [architecture](references/architecture.md) and [code design](references/code-design.md) guides. Also read [legacy code](references/legacy-code.md) when modifying existing behavior and [security](references/security.md) whenever trust boundaries, sensitive data or privileged actions are affected. These are original review prompts inspired by the linked sources; do not pretend to have read a book or section that is not available.

## 2. Critique the design

- Trace every required scenario to a contract, data rule or behavior and a proposed verification. Surface contradictions and unspecified behavior; do not invent requirements.
- Evaluate architecture and code design separately. Inspect the actual repo conventions rather than assuming greenfield architecture.
- For consequential decisions, compare the proposed option with at least one genuinely viable alternative (including retaining the existing design where applicable). Explain why the simpler option is or is not sufficient, implementation and operating costs, reversibility, and what evidence could change the choice. Avoid ceremony for trivial changes.
- Walk through relevant failure cases, concurrent requests, unauthorized access, migration and recovery. Mark inapplicable checks with a reason.
- Identify what can be established from the design/code, what is an assumption, and what needs a focused experiment or human expertise. Do not claim planned tests have passed.

## 3. Write .pipeline/design-review.md

Include the reviewed design revision (commit/hash if available, otherwise a clear version identifier), spec and code references, and scope limitations.

Use this structure:

1. Verdict: APPROVE (recommendation only), REVISE (material design defect), or INVESTIGATE (material uncertainty or missing evidence). If both apply, use REVISE and list investigations.
2. Coverage: scenario → design element → intended test/check → gap.
3. Architecture and code design: criterion → PASS / CONCERN / BLOCK / UNKNOWN / N/A, with evidence and consequence.
4. Findings in severity order: ID, severity, exact design section or file/symbol, concrete failure or maintenance cost, recommended action, alternative/trade-off, verification and relevant reference. Label optional improvements as such.
5. Significant decisions: options, chosen recommendation, rationale, assumptions, reversal cost and reconsideration trigger.
6. Disposition: for each finding, mark RESOLVED BY DESIGNER (after verification), ROUTINE FIX, HUMAN CHOICE, or BLOCKER. A human choice requires two or more genuinely viable options with a meaningful difference in product behavior, cost, operational burden, reversibility, risk tolerance or strategic constraints; do not escalate routine technical correctness or fabricate choices.
7. Human briefing: use the format below, linking only actual unresolved choices and blockers. Keep earlier review rounds and findings in the artifact; summarize rather than erase them.

No aggregate score; a serious security, correctness or data-integrity defect cannot be averaged away. Avoid unsupported findings or pattern mandates. Highlight strengths worth preserving.

## 4. Human-facing decision brief (after routine fixes)

Return the full report to the orchestrator; the default user-facing output is the brief, not the report. Start with the latest verdict, reviewed revision, and a one-line summary of substantive technical fixes already verified. Link the full design and review artifact. If there are no real decisions, explicitly say so and request approval of the reviewed revision. Never pad the brief to reach a quota.

For each genuine human choice (usually zero to three; include all material choices even if more):

- **Decision:** one concrete question, why it matters, and what happens if deferred.
- **Engineering concept:** use the actual term (e.g. information hiding, deep modules, coupling, cohesion, seams, architecture characteristics, trade-offs, defensive programming, data invariants, atomicity, trust boundaries). Define it in one plain-English sentence and explain how it applies here.
- **Options:** at least two viable alternatives, with concrete effects on the product, change effort, risk, cost and reversibility as relevant. Include the status quo if viable. Distinguish measured evidence from assumptions.
- **Recommendation:** select the simplest sufficient option and explain the reason and what would change the recommendation.
- **Learn more:** name the author/resource and relevant chapter, section or linked guide. Use the local reference guides; link the original source when available. Distinguish a verified source from a reading pointer. Do not invent quotes, page numbers, chapter titles or claim a source was consulted when it was not.
- **Your choice:** a clear response or acceptance needed; do not ask the user to judge routine technical correctness.

Use precise concept labels rather than generic jargon. For example: deep modules and information hiding (Ousterhout); cohesion, coupling and defensive programming (McConnell); seams and characterization tests (Feathers); architecture characteristics and trade-offs (Richards/Ford); ADRs (Fowler); threat modeling and trust boundaries (OWASP); design and complexity (Google Engineering Practices). Use only concepts relevant to the decision. For general database concepts, cite an appropriate source if known rather than attributing them to a book without evidence.

## 5. Automatic revision loop and gate

The reviewer returns the verdict and findings to the orchestrator, not directly to the user as an approval request. For REVISE, the orchestrator routes routine findings to design-docs and gets a fresh independent review of material revisions. For INVESTIGATE, resolve material unknowns with available read-only evidence or a separately authorized, narrowly scoped spike. If the issue cannot be resolved within scope, escalate the actual blocker, not a false choice. Default to two revision/re-review cycles per run, then report unresolved blockers and stop. The reviewer never edits the design itself or marks its own findings resolved without evidence from the revised design.

Present the decision brief only after routine issues are resolved or genuinely blocked. When a choice is required, obtain the user's decision and re-review any material changes before final approval. For APPROVE, request explicit human approval and record it in .pipeline/system-design.md with the reviewed revision, review path and accepted residual risks. Do not advance to slicing until approved. Material design changes invalidate the previous review and approval. Never offer approval of a design with unresolved material defects or uncertainties.

Stage 7 still reviews implemented code; this gate does not replace it.
