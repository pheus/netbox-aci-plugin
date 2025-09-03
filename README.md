# NetBox ACI Plugin

The NetBox plugin for Cisco ACI allows NetBox to document ACI specific objects
like Tenants (TN), Application Profiles (AP), Endpoint Groups (EPG),
Endpoint Security Groups (ESG), Bridge Domains (BD) and
Contexts (CTX) / Virtual Routing and Forwarding (VRF).

[![PyPI version](https://img.shields.io/pypi/v/netbox-aci-plugin.svg)](https://pypi.org/project/netbox-aci-plugin/)

Documentation: https://pheus.github.io/netbox-aci-plugin/

## Features

- Tenants
- Application Profiles
- Endpoint Groups
- uSeg Endpoint Groups
- Endpoint Security Groups
- Bridge Domains
- VRF
- Contracts
- Contract Subjects
- Contract Filters

## Compatibility

The following table details the tested plugin versions for each NetBox version:

| NetBox Version | Plugin Version |
|:--------------:|:--------------:|
|      4.4       |     0.1.0      |
|      4.3       |     0.1.0      |



## Installing

### For Docker Setups

For instructions specific to NetBox Docker setups,
see the [netbox-docker plugin documentation](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

### Via PyPI

Activate your NetBox Python virtual environment and run:

```bash
source /opt/netbox/venv/bin/activate

pip install netbox-aci-plugin
```

**Important:** When using NetBox's upgrade.sh, the virtual environment is
deleted and recreated.
To ensure that the ACI plugin is reinstalled during an upgrade,
add it to your `local_requirements.txt` (for local installations) or
`plugin_requirements.txt` (for container-based installations).

```txt
netbox-aci-plugin
```

## Configuration

Enable the plugin by editing the NetBox configuration file.
For local installations, update `/opt/netbox/netbox/netbox/configuration.py`;
for Docker setups, modify `/configuration/plugins.py`:

```python
PLUGINS = [
    'netbox_aci_plugin'
]

PLUGINS_CONFIG = {
    "netbox_aci_plugin": {
        # create default ACI Tenants "common", "infra", "mgmt" during migration
        "create_default_aci_tenants": True,
        # create default ACI Filters "arp", "icmp", "ip" during migration
        "create_default_aci_contract_filters": True,
    },
}
```

After configuration, apply the changes by running the database migrations:

```bash
source /opt/netbox/venv/bin/activate
cd /opt/netbox
python3 netbox/manage.py migrate
```

## Status

This project is in alpha.
While core functionality is stable, bugs and missing features may still be
present.
Use in testing or non-critical environments, and proceed with caution
in production.

## Release notes

See the [changelog](https://github.com/pheus/netbox-aci-plugin/blob/main/CHANGELOG.md).

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

## Credits

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.
