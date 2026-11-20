# Manifest

The control surface for my skill collection. One row per stage: the pick, how I use it, the source to credit, and the artifact it outputs. Changing my mind is a one-line edit here.

Dispositions: **Use** (reference an existing skill as-is) · **Adapt** (thin change over an existing one) · **Own** (I build it — a real gap) · **Ref** (reference with credit; I don't own it).

| # | Stage | Disposition | Skill | Output → next | Source / credit |
|---|-------|-------------|-------|----------------|------------------|
| 0 | Standing rules | Adapt | `PRODUCT.md` (impeccable) + `domain-modeling` glossary | `CLAUDE.md` · `PRODUCT.md` · `CONTEXT.md` | impeccable · Pocock · Spec Kit constitution |
| 1 | Shape the idea | Ref | `grill-me` | sharpened problem + go/no-go | Matt Pocock |
| 2 | Write the spec | Use | `bdd-spec-writer` (+ `impeccable` UI) | `.feature` + mockups → `specs/features/` | mine · impeccable |
| 2a | Write the user story | Use | `user-story-writer` | user story (What / AC) | mine |
| 3 | Design the system | Own | `design-docs` | `system-design.md` — contracts + data model | this repo (handbook · wsff · Kiro · Spec Kit) |
| 4 | Design the code | Own | `design-docs` (same) | `system-design.md` — + signatures | this repo (handbook · codebase-design) |
| 5 | Slice into tasks | Use | `user-story-splitter` | vertical slices (tickets) | mine · (or `to-tickets`, Pocock) |
| 6 | Build | Adapt | `build` (= `story-to-mr`) | committed code + tests | mine (uses `tdd`, Pocock) |
| 7 | Review | Ref | `no-mistakes` | reviewed, draft PR | Kun Chen |

Stages 3 and 4 share one output (`system-design.md`), so they are one skill.

## Substrate (under every stage — adopt as needed, not per-feature skills)

| Concern | Tool | Note |
|---------|------|------|
| Distribution & agility | `npx skills` (vercel-labs) | installs each row from its source; pins in a lockfile |
| Review surface | `lavish` (Kun) / Claude artifacts | review HTML / diagram artifacts |
| Worktrees | `treehouse` (Kun) / local `.worktrees/` | if running parallel sessions |
| Autonomy — out of this repo | `firstmate`, `gnhf` (Kun) | the overnight / crew path; hand off, don't absorb |

## Naming plan (apply during the later global-skills curation)

Invoke each stage as a plain verb. For skills I own, this is a rename; for skills I don't, keep the upstream name or add a thin alias.

`grill` → grill-me (Pocock, keep) · `spec` → bdd-spec-writer · `story` → user-story-writer · `design` → design-docs · `slice` → user-story-splitter · `build` → story-to-mr · `review` → no-mistakes (Kun, keep)

Nothing installed is renamed yet — this manifest only records the intent.
