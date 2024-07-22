###############################################################
# This NetBox configuration file serves as a base for testing #
# purposes only. It is not intended for production use.       #
###############################################################

ALLOWED_HOSTS = ["*"]

DATABASE = {
    "NAME": "netbox",
    "USER": "netbox",
    "PASSWORD": "netbox",
    "HOST": "localhost",
    "PORT": "",
    "CONN_MAX_AGE": 300,
}

PLUGINS = [
    "netbox_aci_plugin",
]

REDIS = {
    "tasks": {
        "HOST": "localhost",
        "PORT": 6379,
        "PASSWORD": "",
        "DATABASE": 0,
        "SSL": False,
    },
    "caching": {
        "HOST": "localhost",
        "PORT": 6379,
        "PASSWORD": "",
        "DATABASE": 1,
        "SSL": False,
    },
}

SECRET_KEY = "5i1(eGhHM_!*&E9-7rJ2y8wF8EA3iNvhRU#X&990-WJE&eT@@7"
