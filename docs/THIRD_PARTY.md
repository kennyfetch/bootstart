# Third-party code and assets

Licenses of everything the project did not write itself. This is guidance, not legal advice: when a
license is unclear or the stakes are high, ask a lawyer.

## Policy

- **Commercial use:** _yes / no_
- **Distribution:** _internal tool / online service / distributed app or package / open source_
- **Project license:** _see `LICENSE`, or proprietary_

| Licenses | Status |
|---|---|
| MIT, MIT-0, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, Zlib, Unlicense, CC0-1.0, BlueOak-1.0.0, Python-2.0, PSF-2.0 | Allowed |
| MPL-2.0 (changes to its files stay MPL), CC-BY-4.0 (credit the author) | Allowed, with their conditions |
| LGPL, GPL, AGPL, EPL and other copyleft licenses | Ask first: allowed only if compatible with the project's license and distribution; record the decision in an ADR |
| Non-commercial or source-available: CC-BY-NC-\*, BUSL-1.1, SSPL-1.0, Elastic-2.0, PolyForm Noncommercial, Commons Clause | Refused when commercial use is planned |
| No license | Refused: without a license there is no right to use it |

A copyleft project (GPL, AGPL) may move the matching copyleft licenses to "Allowed".

## Packages

Checked automatically: on every pull request, the `dependency-review` job
(`.github/workflows/dependency-review.yml`) fails when a new dependency has a license outside the
allowed rows above, or a known vulnerability. Keep its `allow-licenses` list in sync with this table.
An exception for a single package goes in `allow-dependencies-licenses`, with an ADR.

- Licenses the check cannot detect are reported in the job log, not blocked: read it.
- The check needs a public repository (or GitHub Advanced Security); elsewhere the job is skipped.
  Check new dependencies by hand instead: `pnpm licenses list --prod`,
  `uv run --with pip-licenses pip-licenses`.

## Other assets

Fonts, images, icons, sounds, datasets, AI models, copied code snippets: anything no package
manager tracks. Add a row before using one.

| Asset | Source (URL) | License | Commercial use | Credit required | Added |
|---|---|---|---|---|---|
