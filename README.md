# My development process

An invokable set of skills that takes a feature from **idea to reviewed code**. Each stage is one skill I call; each stage's output is the next stage's input. Some skills are mine; some are other people's, referenced with credit.

```
idea → spec → user story → system design → slice → build → review
```

## The stages

| # | Stage | Skill | From | Output → next |
|---|-------|-------|------|----------------|
| 0 | Standing rules | `PRODUCT.md` + a `CONTEXT.md` glossary (`domain-modeling`) | impeccable · Matt Pocock | `CLAUDE.md` · `PRODUCT.md` · `CONTEXT.md` |
| 1 | Shape the idea | `grill-me` | Matt Pocock | a sharpened problem + go/no-go |
| 2 | Write the spec | `bdd-spec-writer` (+ `impeccable` for UI) | me · impeccable | a `.feature` file → `specs/features/…` |
| 2a | Write the user story | `user-story-writer` | me | a user story (What / AC) |
| 3–4 | Design the system + code | `design-docs` | me | `.pipeline/system-design.md` — contracts, data model, signatures |
| 5 | Slice into tasks | `user-story-splitter` | me | thin vertical slices |
| 6 | Build | `story-to-mr` | me | committed code + passing tests |
| 7 | Review | `no-mistakes` | Kun Chen | a reviewed, draft PR |

Stages 3 and 4 share one output (`system-design.md`), so they're one skill: decide the shape — contracts, data model, function signatures — before writing code.

## Mine

- `design-docs` — in this repo ([`skills/design-docs`](skills/design-docs/SKILL.md)): writes `system-design.md` before any code.
- `story-to-mr`, `bdd-spec-writer`, `user-story-writer`, `user-story-splitter` — authored for the Panopticon / Lumino codebase, referenced from where they live.

## From other people

- **Matt Pocock** — `grill-me`, `domain-modeling`.
- **Kun Chen** — `no-mistakes`.
- **impeccable** — `PRODUCT.md`, UI work.
- **vercel-labs** — the `skills` CLI that installs everything.

See [`CREDITS.md`](CREDITS.md) for attribution and [`MANIFEST.md`](MANIFEST.md) for the per-stage detail.

## Install

Skills install through the open skills CLI, which targets Claude Code and Codex and pins versions in a lockfile:

```bash
npx skills add mattpocock/skills --skill grill-me
npx skills add kunchenguid/no-mistakes
npx skills add febriy/factory --skill design-docs
```

## Software factory

This set is hands-on — I drive each stage myself. For a fully autonomous software factory, I use a separate tool.
