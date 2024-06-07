# NetBox ACI Plugin

The NetBox plugin for Cisco ACI allows NetBox to document ACI specific objects like Tenants (TN), Application Profiles (AP), Endpoint Groups (EPG), Bridge Domains (BD) and Contexts (CTX) / Virtual Routing and Forwarding (VRF).

Documentation: https://pheus.github.io/netbox-aci-plugin/

## Features

- Tenants
- Application Profiles
- Endpoint Groups
- Bridge Domains
- VRF

## Compatibility

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.0        |      0.0.4     |

## Installing

For adding to a NetBox Docker setup see
[the general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

While this is still in development and not yet on pypi you can install with pip:

```bash
pip install git+https://github.com/pheus/netbox-aci-plugin
```

or by adding to your `local_requirements.txt` or `plugin_requirements.txt` (netbox-docker):

```bash
git+https://github.com/pheus/netbox-aci-plugin
```

Enable the plugin in `/opt/netbox/netbox/netbox/configuration.py`,
 or if you use netbox-docker, your `/configuration/plugins.py` file :

```python
PLUGINS = [
    'netbox-aci-plugin'
]

PLUGINS_CONFIG = {
    "netbox-aci-plugin": {},
}
```

## Status

This project has just started. Database migrations will be added once the main models have been defined.

## Release notes

See the [changelog](https://github.com/pheus/netbox-aci-plugin/blob/main/CHANGELOG.md).

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

## Credits

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.
