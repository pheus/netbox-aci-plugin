# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from netbox.graphql.filters import NetBoxModelFilter

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter

    from ..fabric.fabrics import ACIFabricFilter


__all__ = (
    "ACIAAEPDomainBindingFilter",
    "ACIAttachableAccessEntityProfileFilter",
)


@strawberry_django.filter_type(models.ACIAttachableAccessEntityProfile, lookups=True)
class ACIAttachableAccessEntityProfileFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for ACIAttachableAccessEntityProfile."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()
    infra_vlan: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACIAAEPDomainBinding, lookups=True)
class ACIAAEPDomainBindingFilter(NetBoxModelFilter):
    """GraphQL filter definition for the ACIAAEPDomainBinding model."""

    aci_aaep: (
        Annotated[
            "ACIAttachableAccessEntityProfileFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_aaep_id: ID | None = strawberry_django.filter_field()
    aci_domain_object_type: (
        Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    aci_domain_object_id: ID | None = strawberry_django.filter_field()
