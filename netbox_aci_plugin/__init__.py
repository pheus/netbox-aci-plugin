"""Top-level package for NetBox ACI Plugin."""

__author__ = """Martin Hauser"""
__email__ = "git@pheus.dev"
__version__ = "0.1.0"


from netbox.plugins import PluginConfig


class ACIConfig(PluginConfig):
    """NetBox ACI Plugin specific configuration."""

    name = "netbox_aci_plugin"
    label = "netbox_aci_plugin"
    verbose_name = "NetBox ACI"
    description = "NetBox plugin for documenting Cisco ACI specific objects."
    version = __version__
    author = __author__
    author_email = __email__
    base_url = "aci"
    min_version = "4.3.0"
    max_version = "4.4.99"
    default_settings = {
        "create_default_aci_tenants": True,
        "create_default_aci_contract_filters": True,
    }


config = ACIConfig
