# Reviewing changes to existing code

Ground recommendations in behavior and dependencies that actually exist.

- Locate the current entry point, affected rules, consumers and existing tests. Trace the change impact before moving responsibilities.
- Identify which behavior must stay unchanged. Plan characterization tests for risky, untested behavior before refactoring; existing behavior is not automatically a requirement if the spec explicitly changes it.
- Find a seam at which dependencies can be substituted or behavior observed without launching the entire application. Prefer the smallest safe intervention over a speculative rewrite.
- Separate necessary enabling refactors from feature changes where practical; plan a migration/compatibility path for persisted data and public contracts.
- Choose tests based on likely regressions and side effects, not raw coverage percentages. Ensure integration checks cover boundaries the unit tests cannot.
- If the design depends on an unknown legacy behavior, identify a focused investigation and withhold approval until material uncertainty is resolved.

Example: if a route directly calls an external mail service and is untested, isolate the mail dependency and characterize current observable outcomes before changing the workflow. Preserve existing error semantics unless the specification requires a change.

## Reading

Michael Feathers, *Working Effectively with Legacy Code* (2004):
- Ch. 2 Working with Feedback; ch. 3 Sensing and Separation; ch. 4 The Seam Model.
- Ch. 8 How Do I Add a Feature?
- Ch. 11 I Need to Make a Change. What Methods Should I Test?
- Ch. 13 I Need to Make a Change but I Don't Know What Tests to Write.
- Ch. 23 How Do I Know That I'm Not Breaking Anything?

[Publisher table of contents](https://www.pearson.com/en-us/subject-catalog/p/Feathers-FEATHERS-WORK-EFFECT-LEG-CODE-p-1/P200000008984/9780131177055) · [O'Reilly listing](https://www.oreilly.com/library/view/working-effectively-with/0131177052/).
