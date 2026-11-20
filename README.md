# My development process

A personal, invokable set of skills that takes a feature from **idea to reviewed code**. Each stage is one skill I call; each stage's output is the next stage's input. Most of the skills already exist and are only referenced here with credit — I build my own only for a real gap.

The autonomous / overnight path (`firstmate`, `gnhf`) is deliberately **not** in this repo. This is the toolkit I drive by hand; it can hand off to those, it doesn't become them.

- The per-stage picks, dispositions and outputs: [`MANIFEST.md`](MANIFEST.md)
- Attribution for everything referenced: [`CREDITS.md`](CREDITS.md)

## The spine

```
idea → spec → user story → system design → slice → build → review
```

Every serious design-first workflow I looked at (Matt Pocock, Harper Reed, GitHub Spec Kit, Amazon Kiro, the wsff flow) converges on this order. The one rule underneath it: **a written design is the primary artifact, and it comes before the code.**

## How I develop, stage by stage

| # | Stage | I run | Output (→ feeds next) |
|---|-------|-------|------------------------|
| 0 | **Standing rules** (set once) | lean on `PRODUCT.md` (impeccable) + a `CONTEXT.md` glossary (`domain-modeling`) | `CLAUDE.md` · `PRODUCT.md` · `CONTEXT.md` — read by every stage |
| 1 | **Shape the idea** | `grill-me` | a sharpened problem + go/no-go |
| 2 | **Write the spec** | `bdd-spec-writer` (+ `impeccable` for UI) | a `.feature` file → `specs/features/…` |
| 2a | **Write the user story** | `user-story-writer` | a user story (What / AC) — the PM deliverable |
| 3–4 | **Design the system + code** | `design-docs` *(the one skill I built)* | `.pipeline/system-design.md` — contracts, data model, signatures |
| 5 | **Slice into tasks** | `user-story-splitter` | a list of thin vertical slices |
| 6 | **Build** | `build` (= `story-to-mr`) | committed code + passing tests |
| 7 | **Review** | `no-mistakes` | a reviewed, draft PR |

The keystone is stage 3–4: **decide the shape on paper before writing code.** `design-docs` reads the spec and `PRODUCT.md`, then writes `system-design.md` and stops for my OK — the step my old `story-to-mr` pipeline skipped.

## What's mine vs referenced

- **Built here:** `design-docs` ([`skills/design-docs`](skills/design-docs/SKILL.md)) — the only genuinely new skill.
- **My own, referenced:** `story-to-mr` (→ `build`), `bdd-spec-writer`, `user-story-writer`, `user-story-splitter`. These are already installed; packaging/renaming them to verbs is a later pass.
- **Others, referenced with credit:** `grill-me` (Matt Pocock), `no-mistakes` (Kun Chen), the `domain-modeling` glossary (Pocock).

## Install

Skills install through the open skills CLI, which targets Claude Code and Codex alike and pins versions in a lockfile:

```bash
# referenced upstream skills
npx skills add mattpocock/skills --skill grill-me
npx skills add kunchenguid/no-mistakes

# the skill built in this repo
npx skills add febriy/factory --skill design-docs
```

My own Panopticon skills are installed locally today; wiring them into this collection as sources is part of the later global-skills curation.

## Not here, on purpose

The old autonomous "software factory" (a self-running controller, board, and quality harness) lived in this repo and has been cleared — it's recoverable in git history. Autonomy is `firstmate` / `gnhf`'s job, kept separate.
