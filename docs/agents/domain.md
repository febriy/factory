# Domain documentation

Honor the target repository's established glossary convention. The existing personal `grill-with-docs` skill uses `CONTEXT.md`; the newly installed collection uses `GLOSSARY.md`.

Read the existing glossary and relevant ADRs before changing domain terminology. If only one convention exists, keep it authoritative; do not create a second glossary under the other name. For a new repository with no convention, use `GLOSSARY.md` and create entries when a real term is resolved. Create ADRs under `docs/adr/` when a consequential trade-off earns a durable decision record.

In a monorepo, follow its existing `GLOSSARY-MAP.md` or `CONTEXT-MAP.md` and scoped ADRs. A glossary contains domain terms and relationships. Factory implementation notes belong in design documents or ADRs, not in the glossary.
