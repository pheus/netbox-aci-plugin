# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""ACI extensions to NetBox's DCIM GraphQL types."""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from django.core.exceptions import ObjectDoesNotExist

from utilities.querysets import RestrictedPrefetch

from ..models.fabric.node_interfaces import ACINodeInterface

if TYPE_CHECKING:
    from ..graphql.types import ACINodeInterfaceType

__all__ = ("InterfaceTypeExtension",)


@strawberry.type
class InterfaceTypeExtension:
    """ACI additions to NetBox's Interface type."""

    models = ["dcim.interface"]

    @strawberry_django.field(
        prefetch_related=lambda info: RestrictedPrefetch(
            "aci_node_interface",
            info.context.request.user,
            "view",
            queryset=ACINodeInterface.objects.all(),
        ),
    )
    def aci_node_interface(
        self,
    ) -> (
        Annotated[
            "ACINodeInterfaceType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
        | None
    ):
        """Return the ACI Node Interface backed by this interface."""
        # A reverse one-to-one raises rather than returning None, whether
        # unset or filtered out by the restricted prefetch.
        try:
            return self.aci_node_interface
        except ObjectDoesNotExist:
            return None
