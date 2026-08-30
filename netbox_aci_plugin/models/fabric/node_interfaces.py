# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Model for ACI node interfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.constants import NONCONNECTABLE_IFACE_TYPES
from netbox.models import NetBoxModel
from netbox.models.mixins import OwnerMixin

from ...choices import NodeRoleChoices
from ...constants import (
    ACI_DESC_MAX_LEN,
    NODE_INTERFACE_MODULE_MAX,
    NODE_INTERFACE_MODULE_MIN,
    NODE_INTERFACE_PORT_MAX,
    NODE_INTERFACE_PORT_MIN,
    NODE_INTERFACE_SUB_PORT_MAX,
    NODE_INTERFACE_SUB_PORT_NONE,
)
from ...validators import ACIPolicyDescriptionValidator

if TYPE_CHECKING:
    from core.models import ObjectChange

    from ..access_policies.leaf_interface_overrides import ACILeafInterfaceOverride
    from ..fabric.fabrics import ACIFabric
    from ..fabric.nodes import ACINode


class ACINodeInterface(OwnerMixin, NetBoxModel):
    """ACI Node Interface identity.

    Maps a physical Leaf switch interface by its APIC coordinates
    (module, port, sub port) and optionally links the NetBox interface
    it corresponds to. Access policy sources and access paths resolve
    against this identity.

    Notes:
        This is a NetBox normalization of the interface identity, not
        an APIC managed object. The coordinates are authoritative. A
        sub port of 0 means none, following the APIC interface
        configuration convention. FEX interfaces are out of scope.
    """

    aci_node = models.ForeignKey(
        to="netbox_aci_plugin.ACINode",
        on_delete=models.PROTECT,
        related_name="aci_node_interfaces",
        verbose_name=_("ACI Node"),
    )
    nb_interface = models.OneToOneField(
        to="dcim.Interface",
        on_delete=models.SET_NULL,
        related_name="aci_node_interface",
        verbose_name=_("NetBox interface"),
        blank=True,
        null=True,
        help_text=_(
            "NetBox interface backing this Node Interface. The device "
            "must match the ACI Node's assigned device."
        ),
    )
    module = models.PositiveSmallIntegerField(
        verbose_name=_("module"),
        default=1,
        validators=[
            MinValueValidator(NODE_INTERFACE_MODULE_MIN),
            MaxValueValidator(NODE_INTERFACE_MODULE_MAX),
        ],
        help_text=_("Module (slot) number of the interface. Default is 1."),
    )
    port = models.PositiveSmallIntegerField(
        verbose_name=_("port"),
        validators=[
            MinValueValidator(NODE_INTERFACE_PORT_MIN),
            MaxValueValidator(NODE_INTERFACE_PORT_MAX),
        ],
        help_text=_("Port number of the interface."),
    )
    sub_port = models.PositiveSmallIntegerField(
        verbose_name=_("sub port"),
        default=NODE_INTERFACE_SUB_PORT_NONE,
        validators=[MaxValueValidator(NODE_INTERFACE_SUB_PORT_MAX)],
        help_text=_("Breakout sub port number. 0 means none."),
    )
    description = models.CharField(
        verbose_name=_("description"),
        max_length=ACI_DESC_MAX_LEN,
        blank=True,
        validators=[ACIPolicyDescriptionValidator],
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="%(class)ss",
        verbose_name=_("NetBox tenant"),
        blank=True,
        null=True,
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "aci_node",
        "module",
        "port",
        "sub_port",
        "nb_tenant",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACINode",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_node", "module", "port", "sub_port"),
                name="%(app_label)s_%(class)s_uniq_coords",
                violation_error_message=_(
                    "A Node Interface with these coordinates already exists "
                    "on the ACI Node."
                ),
            ),
        ]
        default_related_name: str = "aci_node_interfaces"
        ordering: tuple = ("aci_node", "module", "port", "sub_port")
        verbose_name: str = _("ACI Node Interface")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.aci_node}:{self.interface_token}"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if self.aci_node_id and self.aci_node.role != NodeRoleChoices.ROLE_LEAF:
            errors.setdefault("aci_node", []).append(
                _("The ACI Node must have the Leaf role.")
            )

        if self.nb_interface_id:
            # The device match is only meaningful once a Node is selected.
            # Without one, the missing-Node error already says everything
            if self.aci_node_id:
                # The cached device relation avoids a generic FK lookup
                node_device = self.aci_node.assigned_device
                if node_device is None or self.nb_interface.device_id != node_device.pk:
                    errors.setdefault("nb_interface", []).append(
                        _(
                            "The NetBox interface's device must match the ACI "
                            "Node's assigned device."
                        )
                    )
            if self.nb_interface.type in NONCONNECTABLE_IFACE_TYPES:
                errors.setdefault("nb_interface", []).append(
                    _("This NetBox interface type cannot be connected.")
                )

        if errors:
            raise ValidationError(errors)

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_node
        return objectchange

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric instance of the related ACI Node."""
        return self.aci_node.aci_fabric

    @property
    def parent_object(self) -> ACINode:
        """Return the parent object of the instance."""
        return self.aci_node

    @property
    def interface_token(self) -> str:
        """Return the normalized APIC interface token."""
        token = f"eth{self.module}/{self.port}"
        if self.sub_port:
            return f"{token}/{self.sub_port}"
        return token

    @property
    def sub_port_display(self) -> int | None:
        """Return the sub port, or None for the APIC 0 (none) sentinel."""
        return self.sub_port or None

    @property
    def leaf_interface_override(self) -> ACILeafInterfaceOverride | None:
        """Return the Leaf Interface Override, or None if there is none.

        The reverse one-to-one descriptor raises rather than returning
        None, an exception the Django template engine silenced but plain
        attribute access does not. The descriptor reads its cache before
        querying, so a warm select_related costs no extra query here.
        """
        try:
            return self.aci_leaf_interface_override
        except ObjectDoesNotExist:
            return None
