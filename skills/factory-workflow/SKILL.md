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
| 5 | Slice the story | Independently testable vertical slices |
| 6 | Build a slice | Scoped commit and passing tests |
| 7 | Review | Review findings and draft PR when authorised |

Stages 3 and 4 share the design-docs skill and .pipeline/system-design.md. Name them separately when explaining progress. Check which sections exist for the feature under discussion and which decisions the user approved.

When asked what comes next in the factory workflow, answer with the next stage, its output, and the evidence for the current stage. If the question names a stage, give its immediate successor. For status requests, distinguish product-wide specs from design or build work for a single feature. Resume existing artifacts. Consult project instructions for local build, tracker and review procedures when executing a stage.

Some upstream stage skills are referenced from other repositories or are private. Use installed stage skills when available, or follow the documented artifact contract and identify a manual stage when relevant.

## Build and review separation

At stage 6, dispatch a fresh build subagent with no inherited conversation. Give it the approved user story, product behaviour, software design and slice boundary. Prepare a standalone handoff if the source documents embed BDD examples. Withhold the BDD files, scenario text, exact acceptance fixtures and reviewer tests from the builder. Ask it to avoid reading them through links, searches or test output. The builder can design and run its own implementation tests.

At stage 7, dispatch a separate fresh reviewer with the original BDD, the build revision and normal product entry points. Have it exercise the behaviour independently and report observations against the criteria. If a correction is needed, send the builder the observed defect. Record any earlier exposure when reviewing existing work. In a shared workspace, report the actual context and file access boundaries.
