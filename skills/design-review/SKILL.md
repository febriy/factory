---
name: design-review
description: Independently critique the system and code design before human approval and task slicing. Use after design-docs and before user-story-splitter.
disable-model-invocation: true
---

# Design review

Review the proposed design, not its author's confidence. The goal is the simplest sufficient design and a human who understands the trade-offs. Run in a fresh agent context when available; otherwise disclose that the review is not independent. Do not implement code, silently rewrite the design, or approve on the user's behalf.

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
6. Human briefing: up to three important decisions in plain English, one worked example where useful, relevant reading sections, and any residual risks requiring explicit acceptance.

No aggregate score; a serious security, correctness or data-integrity defect cannot be averaged away. Avoid unsupported findings or pattern mandates. Highlight strengths worth preserving.

## 4. Stop at the gate

Present the report and stop. For REVISE, return to design-docs to address the findings. For INVESTIGATE, gather evidence or run a narrowly scoped, separately authorized spike; then review again. For APPROVE, ask for explicit human approval and record it in .pipeline/system-design.md with the reviewed revision, review path and accepted residual risks. Do not advance to slicing until approved. Material design changes invalidate the previous review and approval.

Stage 7 still reviews implemented code; this gate does not replace it.
