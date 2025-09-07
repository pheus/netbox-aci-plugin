# Security Policy

## No Warranty
Per the terms of the **GNU General Public License v3.0** (GPL‑3.0),
the NetBox ACI Plugin is provided “as is,” without a warranty of
any kind.
While maintainers make reasonable efforts to avoid security defects,
you are responsible for evaluating each release for fitness and risk in
your own environment.

## Supported Versions
We provide security fixes for the latest patch release of
each supported minor series.

| Plugin Version | Supported                 |
|----------------|---------------------------|
| 0.1.x          | ✅ Security fixes accepted |
| < 0.1.0        | ❌ End of support          |

> See the [changelog](https://github.com/pheus/netbox-aci-plugin/blob/main/CHANGELOG.md) for compatibility details.

## Reporting a Vulnerability

**Do not open public GitHub issues for security reports.**

**Preferred:** Use GitHub’s **Security → “Report a vulnerability”** to
contact the maintainers via a private Security Advisory.

Please include:
- Affected **plugin version** and **NetBox version**
- Environment details (local/Docker/OS/Python)
- Impact and minimal steps to reproduce (PoC if possible)
- Relevant logs (scrub sensitive data)

## Scope

This policy covers vulnerabilities in the **NetBox ACI Plugin**
codebase and its documentation site.
Issues in **NetBox core** or other dependencies should be reported
upstream to their respective maintainers.

### Out of Scope (examples)

- Denial‑of‑service (resource exhaustion, load tests) or spam
- Vulnerabilities require privileged access, physical access,
  or a compromised environment
- Clickjacking or missing security headers on non‑sensitive pages
- Best‑practice suggestions without a demonstrable security impact
- Third‑party or platform issues outside this repository’s control

### Testing Guidelines

- Use only your own systems and data; do **not** test against systems
  you do not own or have permission to test.
- Avoid privacy violations and service degradation.
- Do not run automated scanners against third‑party deployments.

## Our Process & Timelines

- **Acknowledgment:** within **3 business days**
- **Triage & Reproduction:** within **7 business days**
- **Fix & Release:** target **≤30 days** for high/critical issues and
  **≤90 days** otherwise (coordinated disclosure if needed)
- **Credit:** We’re happy to credit reporters unless you prefer anonymity.

## Coordinated Disclosure

After a fix is available, we will publish a GitHub Security Advisory
and update the changelog with upgrade guidance.
If a CVE is appropriate, we’ll request one through GitHub.

## Safe Harbor

We will not pursue or support legal action against researchers who:
- Act in good faith and within this policy’s Scope and Testing Guidelines
- Avoid privacy violations and service disruption
- Give us reasonable time to remediate before public disclosure

This policy does not authorize testing against systems you do not own
or have permission to test,
nor accessing data that does not belong to you.

## Bug Bounties

We do not operate a bug bounty program at this time.
