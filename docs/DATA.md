# Data and access

What the project stores about people, who may do what, and the rules that follow. Read it before
any change that collects data, touches accounts or changes permissions. It is the starting point
of the GDPR record of processing activities (article 30); it lays out what the GDPR expects but is
not legal advice — ask a data protection officer or a lawyer when in doubt.

## Context

- **Audience:** _public / internal_
- **Accounts:** _none / yes — how people sign in_
- **Hosting:** _provider and region (EU or not)_

## Roles and permissions

| Role | Can | Cannot |
|---|---|---|
| _Visitor_ | _…_ | _…_ |

Every permission is enforced on the server side and has a test for the forbidden case.

## Personal data

_None. Update this file before collecting any._

| Data | Purpose | Legal basis | Retention | Stored in | Shared with |
|---|---|---|---|---|---|

**Sensitive data** (health, biometrics, ethnic origin, religion, political opinions, sex life,
criminal records, children's data): _none / list_. If any, an impact assessment (DPIA, "AIPD" in
French) is likely required before release.

## Third-party services that receive data (processors)

| Service | What it receives | Location | Data processing agreement |
|---|---|---|---|

## People's rights

How a person gets a copy of their data, has it corrected or deleted, objects, or withdraws consent:
_the feature or the manual procedure for each_.

## Rules for code

- Collect only what is listed above; a new field means updating this file first.
- Never log personal data, tokens or secrets; mask identifiers in error reports.
- Delete or anonymize data when its retention period ends, with an automated, tested job.
- Security baseline: OWASP ASVS level 1 at least; level 2 (recommended for most applications) when
  there are accounts or personal data.
