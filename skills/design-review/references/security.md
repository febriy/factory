# Security design review

Scale this review to the data sensitivity and trust boundaries. This is not a security certification.

- Identify actors, assets, data flows and trust boundaries; include external services and privileged operations.
- For each entry point, distinguish authentication (who is calling) from authorization (what they may do). Check object-level ownership and tenant isolation; do not rely on client-side controls.
- Validate untrusted input at appropriate boundaries. Do not expose private fields, secrets, internal errors or unnecessary personal information in responses or logs.
- Consider impersonation, data tampering, disclosure, service exhaustion, privilege escalation and workflow abuse. Check replay, duplicates and concurrent actions where relevant.
- For significant threats, document plausible failure, impact, mitigation, residual risk and a verification (such as a cross-tenant request rejection test). Avoid unsupported risk ratings.
- Ensure sensitive data retention, deletion and access policies match product requirements; escalate material unknowns or high-impact unresolved risks to a qualified human.

## Reading

- OWASP, [Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html).
- Google, [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html).

These links are references, not a claim that every control has been implemented or verified.
