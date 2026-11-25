---
name: design-docs
description: Before any code, write the system and program design for a feature — endpoint contracts, the data model, and key function signatures — into .pipeline/system-design.md, grounded in the spec and PRODUCT.md, for independent design review and a human OK gate. Use after the spec / user story and before the build.
disable-model-invocation: true
---

# Design docs

Decide the shape before you build. The cheapest place to fix a design mistake is this one file; the most expensive is merged code. Produce `.pipeline/system-design.md`, automatically hand it off to `design-review`, resolve routine engineering findings and get the user's OK on the reviewed design before any implementation starts. Invoking this skill includes Stage 4a; do not require a separate user invocation.

Input: the feature spec (a `.feature` in `specs/features/…` and/or the user story) and `PRODUCT.md`. If there is neither a spec nor a story, ask for it — do not invent the behaviour.

## 1. Ground it

- Read the spec / user story and `PRODUCT.md`. Note the nouns (tables, endpoints, emails) and the observable behaviour the scenarios require.
- Run `find-conventions` first, or read its `.pipeline/context.md` if it already ran, so the design copies existing patterns — where routers, services and schemas live, how settings and Helm wiring are done, how tests are written.
- Pull only the product facts this feature depends on. Do not restate `PRODUCT.md`.

## 2. Write `.pipeline/system-design.md`

Three load-bearing sections. Skip one only when the feature truly has no such surface, and say so.

1. **Endpoint contracts** — per endpoint: method + path, request body, the success response, and the named error responses (404 / 403 / 409 / 422 …), plus who is allowed to call it. Keep out of a response anything a caller must not see (e.g. an answer key). This section forces the real decisions, so it is never skipped for a feature with an API.
2. **Data model** — `CREATE TABLE` / `ALTER TABLE` for new or changed tables and columns, plus the one or two queries this feature runs most, so the indexes it needs are obvious. Store the facts you cannot recompute; derive the rest on read; store a derived value only for a reason — cost, or freezing a snapshot — and then own keeping it honest.
3. **Types & signatures** — the key new functions as signatures only, no bodies: what each takes and returns. Keep the real logic free of the database and HTTP (accept dependencies, return results) so it is testable in isolation. Say where each lives: the router is a thin coordinator; the service holds the deep module.

Optional, and only when the change crosses several services or edits a tangled existing flow: a short Mermaid **sequence diagram**, or a **call-stack tree** with `+` / `-` marks. Skip both for a straightforward feature.

## 3. Automatic review before the human gate

Mark the design as pending review. Without asking the user to approve the draft or invoke another skill, load the `design-review` skill and dispatch it to a fresh independent subagent (or separate fresh session if subagents are unavailable). If neither is possible, report the blocker and stop. The reviewer must receive the original requirements, current design and affected code, but not the designer's inherited conversation.

Follow the review's findings: correct routine technical defects and make low-risk, evidence-supported choices within the approved requirements. Do not change product behavior, commit to new spend or accept material risk without the user's decision. Send material revisions back to a fresh reviewer. Keep the full review history in `.pipeline/design-review.md`. Default to at most two revision/re-review cycles in a single run; if a material issue persists, present the blocker rather than silently approving or looping indefinitely.

Only then present the concise, concept-labelled decision brief specified by `design-review`. Do not present raw draft artifacts or the entire checklist as the default human-facing output. If a real choice is needed before approval, present the viable reviewed options and recommendation, obtain the decision, incorporate it and re-review any material changes. If no choice remains, say so and request one explicit approval of the reviewed design. Do not move to slicing or build until the final review recommends approval and the user explicitly approves that revision. Record approval as specified by `design-review`.

## Output

`.pipeline/system-design.md` — the input to `design-review` and, once reviewed and approved, to slicing and to `build` (`story-to-mr`), read alongside the spec. It is deliberately code-shaped but is not code: no file bodies, no implementation.

---

Credit: the artifacts and their order follow the Design Docs Handbook, drawn from the wsff ("Why Software Factories Fail") planning flow, with the deep-module framing from Matt Pocock's `codebase-design`.
