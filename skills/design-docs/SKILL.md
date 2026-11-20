---
name: design-docs
description: Before any code, write the system and program design for a feature — endpoint contracts, the data model, and key function signatures — into .pipeline/system-design.md, grounded in the spec and PRODUCT.md, with a human OK gate. Use after the spec / user story and before the build.
disable-model-invocation: true
---

# Design docs

Decide the shape before you build. The cheapest place to fix a design mistake is this one file; the most expensive is merged code. Produce `.pipeline/system-design.md` and get the user's OK before any implementation starts.

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

## 3. The decision gate

For each section, name the one decision it forced (one attempt or many? who may read this? store or derive?). Present `system-design.md` and those decisions to the user and stop. Do not move to slicing or the build until the user approves. Record the approval in the file.

## Output

`.pipeline/system-design.md` — the input to slicing and to `build` (`story-to-mr`), read alongside the spec. It is deliberately code-shaped but is not code: no file bodies, no implementation.

---

Credit: the artifacts and their order follow the Design Docs Handbook, drawn from the wsff ("Why Software Factories Fail") planning flow, with the deep-module framing from Matt Pocock's `codebase-design`.
