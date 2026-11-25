# Code design review (stage 4)

Assess proposed interfaces, responsibilities and dependency directions; implementation quality remains unverified until the code exists.

| Lens | Questions and evidence |
|---|---|
| Information hiding | What decisions or data representations are hidden behind each interface? Does a caller need to coordinate internal steps? |
| Module depth | Is the interface small relative to the behavior it owns? Avoid layers that merely forward calls without a benefit. |
| Cohesion | Are related invariants and business rules owned together? Can a change be made in one meaningful place? |
| Coupling | What must change if a dependency, representation or business rule changes? Do dependency cycles or duplicated knowledge exist? |
| Testability | Can rules be exercised with deterministic inputs without booting unrelated infrastructure? Are real database/HTTP integration checks also planned when needed? |
| Clarity | Do signatures express domain language, expected results, errors, side effects and relevant invariants? |
| Appropriate abstraction | What existing variation or complexity justifies each interface? Prefer concrete code over speculative extension points. |

Example: expose submit_assessment(user_id, assessment_id, answers) instead of requiring the route to call validate, score, save and update in the correct order. The service coordinates persistence and transaction boundaries; pure validation/scoring can still be tested separately. Do not confuse a small interface with one oversized implementation.

## Reading

- Steve McConnell, *Code Complete*, 2nd ed.: ch. 5 Design in Construction, ch. 6 Working Classes, ch. 7 High-Quality Routines, ch. 8 Defensive Programming. [Chapter 5 excerpt](https://www.microsoftpressstore.com/articles/article.aspx?p=2222451).
- John Ousterhout, *A Philosophy of Software Design*, 2nd ed.: complexity, deep modules, information hiding, and designing interfaces. [Author's book page](https://web.stanford.edu/~ouster/cgi-bin/book.php).
- Google, [Engineering Practices](https://google.github.io/eng-practices/) and [review criteria](https://google.github.io/eng-practices/review/reviewer/looking-for.html) — focus on fit, understandability, appropriate scope and meaningful tests.

Use the books as reading pointers rather than claiming a chapter was consulted without access. No fixed function length, SOLID checklist or pattern is a substitute for judgment.
