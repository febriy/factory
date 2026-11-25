---
name: factory-workflow
description: Navigate the febriy/factory stages and coordinate a blind build and independent BDD review when the user invokes the factory workflow.
---

Use the [upstream manifest](https://github.com/febriy/factory/blob/main/MANIFEST.md) for stage order.

| Stage | Activity | Output |
| --- | --- | --- |
| 0 | Establish product context and domain language | Product brief and glossary |
| 1 | Shape the idea | Agreed problem and direction |
| 2 | Specify behaviour | BDD scenarios |
| 2a | Write the user story | User outcome and acceptance criteria |
| 3 | Design the system | Endpoint contracts and data model |
| 4 | Design the code (software or program design) | Module responsibilities, types and function signatures |
| 4a | Independently review the design | .pipeline/design-review.md and human-approved design |
| 5 | Slice the story | Independently testable vertical slices |
| 6 | Build a slice | Scoped commit and passing tests |
| 7 | Review | Review findings and draft PR when authorised |

Stages 3 and 4 share the design-docs skill and .pipeline/system-design.md. Name them separately when explaining progress. Check which sections exist for the feature under discussion and which decisions the user approved.

When asked what comes next in the factory workflow, answer with the next stage, its output, and the evidence for the current stage. If the question names a stage, give its immediate successor. For status requests, distinguish product-wide specs from design or build work for a single feature. Resume existing artifacts. Consult project instructions for local build, tracker and review procedures when executing a stage.

Some upstream stage skills are referenced from other repositories or are private. Use installed stage skills when available, or follow the documented artifact contract and identify a manual stage when relevant.

## Independent design review

At stage 4a, dispatch a fresh design-review subagent with no inherited designer conversation. Give it the original spec / BDD, user story, product and domain context, proposed system-design.md, and read access to the affected code, tests and reference guides. Unlike the blind builder, this reviewer needs the BDD. Do not include the designer's conversational reasoning or ask the reviewer to defend the proposal. Require evidence, alternative options, a verdict and a human briefing. The parent agent presents findings; it must not substitute its own approval. If subagents are unavailable, hand off to a separate fresh session. If neither is available, report INVESTIGATE and stop rather than claim independence. Resolve findings, repeat review on material changes, and record explicit human approval of the reviewed revision before stage 5.

## Build and review separation

At stage 6, verify that the Stage 4a approval applies to the design being built. Then dispatch a fresh build subagent with no inherited conversation. Give it the approved user story, product behaviour, software design and slice boundary. Prepare a standalone handoff if the source documents embed BDD examples. Withhold the BDD files, scenario text, exact acceptance fixtures and reviewer tests from the builder. Ask it to avoid reading them through links, searches or test output. The builder can design and run its own implementation tests.

At stage 7, dispatch a separate fresh reviewer with the original BDD, the build revision and normal product entry points. Have it exercise the behaviour independently and report observations against the criteria. If a correction is needed, send the builder the observed defect. Record any earlier exposure when reviewing existing work. In a shared workspace, report the actual context and file access boundaries.
