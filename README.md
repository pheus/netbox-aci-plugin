# NetBox ACI Plugin

A NetBox plugin for documenting Cisco ACI policy as structured, related data.

It adds ACI-specific models for fabric inventory, fabric access policy,
tenant and application policy, endpoint policy, networking, contracts, and
external connectivity, so these parts of the ACI policy model can be
documented alongside the rest of your NetBox data.

The project focuses on documenting intended policy and supporting
source-of-truth workflows.

[![PyPI](https://img.shields.io/pypi/v/netbox-aci-plugin.svg)](https://pypi.org/project/netbox-aci-plugin/)
[![Python versions](https://img.shields.io/pypi/pyversions/netbox-aci-plugin.svg)](https://pypi.org/project/netbox-aci-plugin/)
[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://pheus.github.io/netbox-aci-plugin/)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-green.svg)](https://github.com/pheus/netbox-aci-plugin/blob/main/LICENSE)

> **Status:** Alpha - interfaces and data models may change.

**Documentation:** https://pheus.github.io/netbox-aci-plugin/

## Table of Contents

- [What this plugin adds](#what-this-plugin-adds)
- [Current model coverage](#current-model-coverage)
- [API access](#api-access)
- [APIC synchronization](#apic-synchronization)
- [Compatibility](#compatibility)
- [Installation](#installation)
    - [Production installation](#production-installation)
    - [Manual installation](#manual-installation)
    - [Docker](#docker)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [Status](#status)
- [Release notes](#release-notes)
- [Contributing](#contributing)
- [Security](#security)
- [Licensing](#licensing)
- [Affiliation](#affiliation)
- [Credits](#credits)

## What this plugin adds

NetBox does not model Cisco ACI policy constructs by default. This plugin
represents those constructs as NetBox objects and relates them to existing
NetBox data where appropriate.

The documented policy can be reviewed through the NetBox UI and consumed by
automation through REST and GraphQL.

## Current model coverage

| ACI area | Currently modeled |
|----------|-------------------|
| Fabric inventory | Fabrics, Pods, Nodes |
| Fabric access policy | VLAN Pools, VLAN Pool Ranges, Physical Domains, Routed Domains, Attachable Access Entity Profiles (AAEPs), AAEP Domain Bindings |
| Tenant and application policy | Tenants, Application Profiles |
| Networking | VRFs, Bridge Domains, Bridge Domain Subnets, Bridge Domain–L3Out Bindings |
| Endpoint policy | Endpoint Groups, uSeg Endpoint Groups, uSeg Network Attributes, Endpoint Security Groups, ESG Endpoint Group Selectors, ESG Endpoint Selectors |
| Endpoint bindings | Endpoint Group Domain Bindings, Endpoint Group AAEP Bindings |
| Contracts | Contracts, Contract Subjects, Contract Filters, Contract Filter Entries, Contract Subject Filters, Contract Relations |
| External connectivity | L3Outs, External Endpoint Groups, External Subnets |

For field-level details, relationships, and validation rules, see the
[feature documentation](https://pheus.github.io/netbox-aci-plugin/).

## API access

All currently modeled ACI objects are available through the plugin's REST API.

They are also available for read access through NetBox's GraphQL API,
including filterable, paginated list queries.

## APIC synchronization

This plugin is not an APIC synchronization engine.

It does not discover objects from APIC, synchronize operational state, detect
configuration drift, or push policy changes to APIC. Its focus is representing
the intended ACI policy as NetBox data.

No APIC connection or APIC credentials are required.

## Compatibility

The following table lists the latest plugin release tested with each NetBox
version:

| NetBox Version | Plugin Version |
|:--------------:|:--------------:|
|      4.6       |     0.4.0      |
|      4.5       |     0.4.0      |
|      4.4       |     0.1.0      |
|      4.3       |     0.1.0      |

Historical compatibility does not imply ongoing support. See the
[security policy](https://github.com/pheus/netbox-aci-plugin/blob/main/SECURITY.md)
for the currently supported release series.

## Installation

### Production installation

For production installations, add the plugin to NetBox's
`local_requirements.txt` so it is reinstalled whenever the virtual
environment is rebuilt:

```bash
sudo sh -c 'echo netbox-aci-plugin >> /opt/netbox/local_requirements.txt'
```

Enable the plugin in `configuration.py` as described in
[Configuration](#configuration), then run the NetBox upgrade script and
restart the services:

```bash
sudo /opt/netbox/upgrade.sh
sudo systemctl restart netbox netbox-rq
```

Because the plugin is enabled before `upgrade.sh` runs, the script also applies
its database migrations and collects static files.

### Manual installation

For a one-off manual installation, install the package directly into NetBox's
virtual environment:

```bash
sudo /opt/netbox/venv/bin/python3 -m pip install netbox-aci-plugin
```

Then enable and initialize the plugin as described in
[Configuration](#configuration).

For a development installation from source, see
[CONTRIBUTING.md](https://github.com/pheus/netbox-aci-plugin/blob/main/CONTRIBUTING.md).

### Docker

If you deploy NetBox using a custom netbox-docker image, add the package to
`plugin_requirements.txt`:

```text
netbox-aci-plugin
```

Enable the plugin in `configuration/plugins.py` as described in
[Configuration](#configuration), then rebuild and redeploy the custom image.
Restarting an existing image alone does not install new Python packages.

For Docker deployments, redeploy the containers according to your
netbox-docker workflow. Rebuild the image whenever package requirements
change.

For additional guidance, see the
[netbox-docker plugin documentation](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

## Quickstart

1. Install and enable the plugin.
2. Start NetBox and verify that the **ACI** menu appears in the UI.
3. Create or select a **Fabric** to contain the ACI policy model.
4. Add or select a **Tenant**.
5. Define a **VRF** and **Bridge Domain**.
6. Add an **Application Profile** and one or more **Endpoint Groups**.
7. Optionally define **VLAN Pools**, **Physical Domains**, and **AAEPs**;
   associate the access-policy objects, then bind the relevant Physical Domain
   and AAEP to each Endpoint Group.
8. Configure **Contracts**, **Contract Subjects**, and **Contract Filters**, then
   associate the Contracts with the appropriate Endpoint Groups.

> **Tip:** Use the REST API to populate objects at scale after establishing
> your desired policy model.

## Configuration

Enable the plugin in the NetBox configuration. For a standard installation,
edit `/opt/netbox/netbox/netbox/configuration.py`. For netbox-docker, edit
`configuration/plugins.py` in your deployment repository.

No plugin-specific settings are required. The following optional settings
default to `True` and control whether initial ACI objects are created during
database migrations:

```python
PLUGINS = [
    "netbox_aci_plugin",
]

PLUGINS_CONFIG = {
    "netbox_aci_plugin": {
        # Create the default ACI Fabric "Fabric1" during migration
        "create_default_aci_fabric": True,
        # Create the default ACI Tenants "common", "infra", and "mgmt"
        "create_default_aci_tenants": True,
        # Create the default ACI Filters "default", "arp", "est", and "icmp"
        "create_default_aci_contract_filters": True,
    },
}
```

These settings are evaluated when the corresponding database migrations run.
Changing them afterward does not remove or recreate existing objects.

Because the default ACI Tenants must belong to a Fabric, enabling
`create_default_aci_tenants` can also cause the default Fabric `Fabric1` to be
created.

For a manual installation that did not use `upgrade.sh` after enabling the
plugin, apply database migrations, collect static files and restart NetBox:

```bash
source /opt/netbox/venv/bin/activate
cd /opt/netbox
python3 netbox/manage.py migrate
python3 netbox/manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

For Docker deployments, rebuild and redeploy after changing
`plugin_requirements.txt`. A restart is enough only for configuration-only
changes.

## Status

This project is in **alpha**. Core functionality is usable, but model fields,
relationships, and API representations may change before version 1.0.

Review the release notes and back up your NetBox database before upgrading.

## Release notes

See the [changelog](https://github.com/pheus/netbox-aci-plugin/blob/main/CHANGELOG.md).

## Contributing

We follow an **issue-first workflow**:

1. Open an issue (bug or feature request).
2. A maintainer triages and accepts it; a contributor is assigned.
3. Open a PR that **links the accepted, assigned issue**.

See [CONTRIBUTING.md](https://github.com/pheus/netbox-aci-plugin/blob/main/CONTRIBUTING.md) and our PR/issue templates for details.

## Security

Report security vulnerabilities privately through GitHub Security Advisories.
Do not open a public issue for a suspected vulnerability.

See [SECURITY.md](https://github.com/pheus/netbox-aci-plugin/blob/main/SECURITY.md)
for details.

## Licensing

This project is licensed under the GNU General Public License v3.0 or later
(`GPL-3.0-or-later`).

See the repository [LICENSE](https://github.com/pheus/netbox-aci-plugin/blob/main/LICENSE)
for the full text.

## Affiliation

This is a community-maintained NetBox plugin.

It is not affiliated with, endorsed by, or sponsored by Cisco Systems, Inc.,
NetBox Labs, or the NetBox project maintainers.

## Credits

- Built for the NetBox ecosystem - thanks to the NetBox community.
- Based on the NetBox plugin tutorial:
    - [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
    - [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with
[Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the
[`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin)
template.
