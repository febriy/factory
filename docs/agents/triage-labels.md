# Triage and factory workflow

Proposed triage vocabulary follows the installed collection. These labels have not been created on any remote repository.

| Upstream role | Target label | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Request needs evaluation. |
| `needs-info` | `needs-info` | Required facts or a human decision are missing. |
| `ready-for-agent` | `ready-for-agent` | Request is specified sufficiently for agent implementation. |
| `ready-for-human` | `ready-for-human` | Work requires human implementation or judgment. |
| `wontfix` | `wontfix` | Request has been deliberately declined. |

Category roles are `bug` and `enhancement`. Retain an existing target repository's mappings when they are already configured.

Factory execution is a separate dimension, proposed as one `factory:*` status label per managed issue: `factory:triage`, `factory:planned`, `factory:ready`, `factory:running`, `factory:review`, `factory:done`, `factory:blocked`, or `factory:cancelled`.

Ready requires an approved scope and test interfaces, completed prerequisites, available access, and no active claim. `ready-for-agent` by itself does not satisfy these conditions.

Done requires acceptance evidence for the accepted revision and the required integrated/merged code and checks. Cancelled does not satisfy a prerequisite. A manually closed issue with missing acceptance evidence is a discrepancy to resolve, not automatic completion.

The future adapter must validate transitions and reconcile labels with PR/check state. This document defines the mapping; it does not implement that adapter.
