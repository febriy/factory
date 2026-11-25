# Manifest

One row per stage: the skill, where it comes from, and the artifact it outputs. Each output is the next stage's input. Edit a row to change a choice.

| # | Stage | Skill | From | Output → next |
|---|-------|-------|------|----------------|
| 0 | Standing rules | `PRODUCT.md` + `domain-modeling` glossary | impeccable · Matt Pocock | `CLAUDE.md` · `PRODUCT.md` · `CONTEXT.md` |
| 1 | Shape the idea | `grill-me` | Matt Pocock | sharpened problem + go/no-go |
| 2 | Write the spec | `bdd-spec-writer` (+ `impeccable` UI) | me · impeccable | `.feature` → `specs/features/` |
| 2a | Write the user story | `user-story-writer` | me | user story (What / AC) |
| 3 | Design the system | `design-docs` | me | `system-design.md` — contracts + data model |
| 4 | Design the code | `design-docs` (same) | me | `system-design.md` — + signatures |
| 4a | Review the design | `design-review` | me | `.pipeline/design-review.md` + human-approved design |
| 5 | Slice into tasks | `user-story-splitter` | me | vertical slices |
| 6 | Build | `story-to-mr` | me | committed code + tests |
| 7 | Review | `no-mistakes` | Kun Chen | reviewed, draft PR |

Stages 3 and 4 share one output (`system-design.md`), so they're one skill. Stage 4a automatically uses a fresh independent subagent to review that artifact, then routes routine technical fixes and re-reviews before human approval and slicing. The user sees a concise decision brief with engineering terms and attributed reading pointers, not raw review findings. A materially changed design needs a fresh review.

The [factory-workflow skill](skills/factory-workflow/SKILL.md) coordinates the stages, including separate design reviewer, builder and implementation reviewer handoffs.

## Install

Everything installs through the `skills` CLI (vercel-labs), which targets Claude Code and Codex and pins versions in a lockfile:

```bash
npx skills add mattpocock/skills --skill grill-me
npx skills add kunchenguid/no-mistakes
npx skills add febriy/factory --skill design-docs
npx skills add febriy/factory --skill design-review
npx skills add febriy/factory --skill factory-workflow
```

My own Panopticon skills are installed locally; packaging them as sources is pending.

## Substrate

Runs under every stage; adopt as needed, not a per-feature skill.

| Concern | Tool |
|---------|------|
| Install & pin skills | `skills` CLI (vercel-labs) |
| Review artifacts | Claude artifacts / an HTML review tool |
| Isolated worktrees | git worktrees |

## Naming

Stages use plain verb names (Stage 4a runs automatically as part of design; it can also be invoked for a standalone review): `grill · spec · story · design · design-review · slice · build · review`. For my own skills this is a rename; for others, keep the upstream name or add a thin alias.
