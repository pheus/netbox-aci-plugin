# NetBox ACI Plugin

The NetBox plugin for Cisco ACI allows NetBox to document
**ACI‑specific** objects like Tenants (TN), Application Profiles (AP),
Endpoint Groups (EPG), Endpoint Security Groups (ESG),
Bridge Domains (BD), and VRFs (Contexts).

[![PyPI](https://img.shields.io/pypi/v/netbox-aci-plugin.svg)](https://pypi.org/project/netbox-aci-plugin/)
[![Python versions](https://img.shields.io/pypi/pyversions/netbox-aci-plugin.svg)](https://pypi.org/project/netbox-aci-plugin/)
[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://pheus.github.io/netbox-aci-plugin/)
[![License](https://img.shields.io/badge/license-See%20LICENSE-lightgrey.svg)](https://www.gnu.org/licenses/gpl-3.0.txt)

> **Status:** Alpha – Interfaces and data models may change.

**Documentation:** https://pheus.github.io/netbox-aci-plugin/

## Table of Contents
- [Features](#Features)
- [Compatibility](#Compatibility)
- [Installation](#Installation)
    - [Via PyPI](#Via-PyPI)
    - [Docker](#Docker)
- [Quickstart](#Quickstart)
- [Configuration](#Configuration)
- [Status](#Status)
- [Release notes](#Release-notes)
- [Licensing](#Licensing)
- [Credits](#Credits)
- [Contributing](#Contributing)
- [Security](#Security)

## Features

- Represent core ACI constructs in NetBox:
    - Tenants
    - Application Profiles
    - Endpoint Groups (including **uSeg EPGs**)
    - Endpoint Security Groups
    - Bridge Domains
    - VRFs (Contexts)
    - Contracts, Contract Subjects, and Contract Filters
- Consistent UI patterns with NetBox core (tables, filtersets,
  detail views)
- Ready for automation via NetBox’s REST API
- Designed to coexist with your existing NetBox data model

## Compatibility

The following table details the tested plugin versions for each NetBox version:

| NetBox Version | Plugin Version |
|:--------------:|:--------------:|
|      4.4       |     0.1.0      |
|      4.3       |     0.1.0      |

## Installation

### Via PyPI

Activate your NetBox virtual environment and install:

```bash
source /opt/netbox/venv/bin/activate
pip install netbox-aci-plugin
```

**Important:** When using NetBox’s `upgrade.sh`, the virtual environment
is deleted and recreated.
To ensure that the ACI plugin is reinstalled during an upgrade,
add it to your `local_requirements.txt` (for local installations) or
`plugin_requirements.txt` (for container-based installations).

```txt
netbox-aci-plugin
```

### Docker

If you deploy NetBox with Docker and use `plugin_requirements.txt`, add:

```
netbox-aci-plugin
```

Rebuild/restart your NetBox container(s) so the plugin is installed and
discovered. For more on Docker usage, see the
[netbox-docker plugin documentation](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

## Quickstart

1. Install the plugin (see [Installation](#Installation)).
2. Start NetBox and verify **Plugins → NetBox ACI** appears in the UI.
3. Create a **Tenant**, then an **Application Profile** and **EPGs**.
4. Add **Contracts**, **Subjects**, and **Filters**; associate them with
   EPGs.
5. Define **Bridge Domains** and **VRFs** to complete the model.

> Tip: Use NetBox’s API to populate objects at scale once your model is set.

## Configuration

Enable the plugin by editing the NetBox configuration file.
For local installations, update `/opt/netbox/netbox/netbox/configuration.py`;
for Docker setups, modify `/configuration/plugins.py`:

```python
PLUGINS = [
    "netbox_aci_plugin",
]

PLUGINS_CONFIG = {
    "netbox_aci_plugin": {
        # Create default ACI Tenants "common", "infra", "mgmt" during migration
        "create_default_aci_tenants": True,
        # Create default ACI Filters "arp", "icmp", "ip" during migration
        "create_default_aci_contract_filters": True,
    },
}
```

Apply database migrations and restart NetBox:

```bash
source /opt/netbox/venv/bin/activate
cd /opt/netbox
python3 netbox/manage.py migrate
# restart your NetBox services (e.g., systemd or container restart)
```

## Status

This project is in **alpha**.
While core functionality is usable, bugs and missing features may remain.
Use in testing or non‑critical environments; exercise caution in production.

## Release notes

See the [changelog](https://github.com/pheus/netbox-aci-plugin/blob/main/CHANGELOG.md).

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) for the full text.

## Credits

- Built for the NetBox ecosystem – thanks to the NetBox community.
- Not affiliated with or endorsed by Cisco Systems, Inc.
- Based on the NetBox plugin tutorial:
    - [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
    - [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) template.

## Contributing

We follow an **issue‑first workflow**:

1. Open an issue (bug or feature request).
2. A maintainer triages and accepts it; a contributor is assigned.
3. Open a PR that **links the accepted, assigned issue**.

See [CONTRIBUTING.md](https://github.com/pheus/netbox-aci-plugin/blob/main/CONTRIBUTING.md) and our PR/issue templates for details.

## Security

Please **do not** file public issues for vulnerabilities.
See [SECURITY.md](https://github.com/pheus/netbox-aci-plugin/blob/main/SECURITY.md).
