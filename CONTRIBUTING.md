# Contributing to NetBox ACI Plugin

First off—thanks for taking the time to contribute to
**NetBox ACI Plugin**!
Contributions of all kinds are welcome.
Please be kind, constructive, and respectful in issues, PRs, and
discussions.

> **Code of Conduct**
> This project follows our [Code of Conduct](https://github.com/pheus/netbox-aci-plugin/blob/main/CODE_OF_CONDUCT.md).
> By participating, you agree to uphold it.

---

## General Tips for Working on GitHub

- Register for a free [GitHub account](https://github.com/signup) if you
  haven't already.
- You can use [GitHub Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
  for formatting text and adding images.
- To help mitigate notification spam, please avoid "bumping" issues
  with no activity.
  To vote an issue up or down, use 👍 / 👎 reactions.
- Please avoid pinging members with `@` unless they've previously
  expressed interest or involvement with that particular issue.
- Familiarize yourself with this list of
  [discussion anti‑patterns](https://github.com/bradfitz/issue-tracker-behaviors)
  and make every effort to avoid them.

---

## How We Work: Issue‑First → Assignment → PR

To avoid wasted effort and keep the project coherent, we follow an
**issue‑first** workflow:

1. **Open an issue** (bug report or feature request) first.
2. A maintainer **triages** it.
   If it’s viable, we’ll mark it as **accepted** and
   (optionally) **needs owner**.
3. The issue’s author or another volunteer can **offer to own it** by
   commenting.
4. A maintainer **assigns** the issue to the owner.
5. The owner opens a **pull request** that resolves the issue.

**Please do not open PRs without an accepted, assigned issue.**
Unassigned PRs may be closed to keep the queue focused.
Draft PRs are welcome **after** an issue is accepted and assigned.

> For background, see the NetBox contributing guide:
> https://github.com/netbox-community/netbox/blob/main/CONTRIBUTING.md

---

## Types of Contributions

- **Report Bugs** → see [Reporting Bugs](#Reporting-Bugs).
- **Implement Features** → see [Requesting Features](#Requesting-Features).
  _Note:_ For issues tagged `help wanted`, **comment to volunteer**;
  a maintainer must **assign the issue** before work begins.
- **Fix Bugs** → look for issues tagged `bug` and `help wanted`
  (same assignment note as above).
- **Write Documentation** → improve the docs' site, README,
  in‑code docstrings, or tutorials.
- **Submit Feedback** → see [Requesting Features](#Requesting-Features)
  for structure.

---

## Reporting Bugs

Open an issue via **Issues → New Issue** and pick the bug template
(if available).
Please include:

- **NetBox version** and **plugin version**
- **Steps to reproduce** (clear, minimal)
- **Expected vs. actual behavior**
- Any **stack traces, logs, or screenshots**

Bug reports are for unintended behavior only; new functionality belongs
in a **feature request**.

---

## Requesting Features

When proposing features, please provide:

- **Problem / use case** (why this matters for ACI modeling in NetBox)
- **Proposed behavior** (what changes, at a high level)
- Any anticipated **models / UI / API** impacts
- **Alternatives** you considered

We may ask questions to refine the scope before acceptance.

---

## Development Environment

> This plugin targets the NetBox ecosystem (Django).
> You’ll need a working NetBox dev environment.

1. **Set up a NetBox dev environment** (Python, PostgreSQL, Redis).
2. **Clone** this repository and create/activate a virtual environment.
3. **Install the plugin in editable mode** from the repo root:
   ```bash
   pip install -e .
   ```
4. **(Recommended) Install and run pre-commit hooks**:
   ```bash
   pip install pre-commit ruff
   pre-commit install
   pre-commit run -a
   ```
5. **Run tests** before pushing:
   ```bash
   python3 netbox/manage.py test
   ```
   > Keep tests fast and focused.

6. **Run NetBox** and verify the plugin loads and behaves as expected.

### Database Migrations (Django)

- Include **one logical migration per PR** for model changes.
- Prefer **backward‑compatible** changes;
  avoid destructive operations in the same release (deprecate first
  when possible).
- Use `RunPython`/`RunSQL` for **data migrations**;
  keep them idempotent and fast.
- Avoid surprising nullability/index changes on large tables without
  discussion.

### API & UI Compatibility

- Avoid breaking API fields, choices, or slugs without prior deprecation.
- Keep UI patterns consistent with NetBox (tables, filtersets, views).

---

## Style, Linting & Versions

- **Python style**: PEP 8 where practical;
  readability over rigid line limits.
- **Linters/formatters**: We use **Ruff** (via **pre-commit**).
  Run `pre-commit run -a` locally before pushing.
- **Supported Python**: Keep changes compatible with the versions
  tested in CI.
- **Typing**: Prefer adding or improving type hints where it increases
  clarity.

---

## Pull Request Guidelines

A PR is reviewed only if:

- [ ] It **links to an accepted, assigned issue** (use `Fixes #NNN` / `Closes #NNN`).
- [ ] It **adds tests** (where applicable) that demonstrate the change.
- [ ] It **updates docs** for user‑facing changes (README, usage docs, and/or docstrings).
- [ ] **pre-commit** passes locally (**Ruff** checks, etc.).
- [ ] It **does not** bump versions or edit the changelog—maintainers handle release bookkeeping.
- [ ] **PR title & commits follow Conventional Commits.**

**Branching & commits**

- Use clear, focused branches like `fix-<short-description>` or
  `feat-<short-description>`.
- Conventional Commits are **mandatory**. Examples:
  - `feat(contracts): add EPG-to-contract binding model`
  - `fix(filters): correct L4 port range validation`
  - `docs: add quickstart for enabling the plugin`
  - `refactor: split utils into modules`
  - Include a body when necessary;
    use `BREAKING CHANGE:` footer if applicable.
- Keep PRs small and focused;
  large refactors should be discussed first in an issue.

**Target branch**

- Open PRs against the default branch unless a maintainer specifies
  otherwise.

---

## Documentation

- Update README or in‑repo docs when behavior changes.
- Include short examples or screenshots for UI‑adjacent changes.
- Keep docstrings current for public methods, models, and utilities.

---

## Security

Please do **not** open a public issue for security problems.
Follow our [SECURITY.md](https://github.com/pheus/netbox-aci-plugin/blob/main/SECURITY.md).
If in doubt, contact a maintainer privately, and we’ll coordinate a fix
and disclosure.

---

## Releasing (Maintainers)

We follow **SemVer** and maintain the changelog. Typical steps:
1. Ensure CI is green and docs are updated.
2. Bump version and changelog.
3. Publish to PyPI (trusted publishing) and create a GitHub release.

---

## Thanks!

Whether you’re filing a precise bug report, improving docs,
or implementing ACI models—thank you!
Your time and effort are appreciated.
🙌
