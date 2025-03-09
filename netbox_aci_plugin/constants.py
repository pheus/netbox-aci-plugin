# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import Q

#
# Contract Relation
#

# Contract relation to possible ACI object types
CONTRACT_RELATION_OBJECT_TYPES = Q(
    app_label="netbox_aci_plugin",
    model__in=(
        "aciendpointgroup",
        "acivrf",
    ),
)
