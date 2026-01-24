###############################################################
# This NetBox configuration file serves as a base for testing #
# purposes only. It is not intended for production use.       #
###############################################################

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "NAME": "netbox",
        "USER": "netbox",
        "PASSWORD": "netbox",
        "HOST": "localhost",
        "PORT": "",
        "CONN_MAX_AGE": 300,
    }
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

SECRET_KEY = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

DEFAULT_PERMISSIONS = {}

API_TOKEN_PEPPERS = {
    1: "TEST-VALUE-DO-NOT-USE-TEST-VALUE-DO-NOT-USE-TEST-VALUE-DO-NOT-USE",
}

LOGGING = {"version": 1, "disable_existing_loggers": True}
