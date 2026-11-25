# Architecture review (stage 3)

Use this as a reasoning aid, not a mandate to introduce architecture patterns.

| Lens | Questions and evidence |
|---|---|
| Correctness | Can each required scenario be traced through an endpoint or entry point, business rule and persisted outcome? Are error responses and ownership clear? |
| Simplicity | Can the existing deployment, database or module handle this? What concrete requirement warrants another service, queue or cache? |
| Data integrity | What is the source of truth? Which uniqueness, foreign-key, check and transaction boundaries enforce invariants? What happens to duplicate or concurrent writes? |
| Security | Where are trust boundaries, authorization checks, private fields and tenant boundaries? See security.md. |
| Reliability | What happens on timeout, retry, partial failure or dependency outage? Are retries safe and recovery observable? |
| Evolvability | Walk through one likely business change. Which components, data and contracts would change? Is migration/backward compatibility necessary? |
| Cost and operations | What is the expected traffic, data size, deployment burden, failure diagnosis and recurring spend? Separate estimates from measured facts. |

Example: for a small learning tracker, calculate progress from completed lessons unless measured read cost or historical snapshot requirements justify storage. Stored derived state needs a consistency and repair plan. Compare realistic options and identify a reconsideration trigger.

For a material architectural choice record context, options, decision, consequences, evidence, confidence and trigger for revisiting. An ADR is useful for persistent, significant decisions; routine feature choices can stay in the design document.

## Reading

- Steve McConnell, *Code Complete*, 2nd ed., §3.5 (Architecture Prerequisite), ch. 5 (Design in Construction). [Public chapter excerpt](https://www.microsoftpressstore.com/articles/article.aspx?p=2222451).
- Mark Richards and Neal Ford, *Fundamentals of Software Architecture*, 2nd ed. (2025). Start with architecture characteristics, coupling, components and trade-offs. [Publisher listing](https://www.oreilly.com/library/view/fundamentals-of-software/9781098175504/) · [Author's resources](https://www.developertoarchitect.com/books.html).
- Martin Fowler, [Architecture Decision Record](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html) — lightweight decision documentation.
- Microsoft, [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/) — browse patterns in response to an actual problem; Azure examples are not a requirement to use Azure.
- Google, [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html) — adapt design and complexity checks to pre-implementation review.
