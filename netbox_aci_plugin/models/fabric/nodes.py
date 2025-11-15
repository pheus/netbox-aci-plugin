# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from dcim.models import Device
from django.apps import apps
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from utilities.templatetags.builtins.filters import bettertitle
from virtualization.models import VirtualMachine

from ...choices import NodeRoleChoices, NodeTypeChoices
from ...constants import NODE_ID_MAX, NODE_ID_MIN, NODE_OBJECT_TYPES
from ..base import ACIFabricBaseModel
from ..mixins import UniqueGenericForeignKeyMixin

if TYPE_CHECKING:
    from ..fabric.fabrics import ACIFabric


class ACINode(ACIFabricBaseModel, UniqueGenericForeignKeyMixin):
    """NetBox model for ACI Node."""

    aci_pod = models.ForeignKey(
        to="netbox_aci_plugin.ACIPod",
        on_delete=models.PROTECT,
        related_name="aci_nodes",
        verbose_name=_("ACI Pod"),
    )
    node_id = models.PositiveSmallIntegerField(
        verbose_name=_("Node ID"),
        validators=[
            MinValueValidator(NODE_ID_MIN),
            MaxValueValidator(NODE_ID_MAX),
        ],
    )
    node_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=NODE_OBJECT_TYPES,
        verbose_name=_("Node object type"),
        blank=True,
        null=True,
    )
    node_object_id = models.PositiveBigIntegerField(
        verbose_name=_("Node object ID"),
        blank=True,
        null=True,
    )
    node_object = GenericForeignKey(
        ct_field="node_object_type",
        fk_field="node_object_id",
    )
    role = models.CharField(
        verbose_name=_("Role"),
        max_length=6,
        default=NodeRoleChoices.ROLE_LEAF,
        choices=NodeRoleChoices,
        help_text=_(
            "The functional role of the node within the ACI fabric topology (e.g., Spine, Leaf, or APIC)."
        ),
    )
    node_type = models.CharField(
        verbose_name=_("Type"),
        max_length=16,
        default=NodeTypeChoices.TYPE_UNKNOWN,
        choices=NodeTypeChoices,
        help_text=_(
            "The specific deployment type of the node, such as a virtual leaf, a remote leaf over WAN, or a Tier-2 leaf."
        ),
    )
    tep_ip_address = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.SET_NULL,
        related_name="aci_nodes",
        verbose_name=_("TEP IP Address"),
        blank=True,
        null=True,
    )

    # Cached related objects by association name for faster access
    _device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="_aci_nodes",
        verbose_name=_("Device"),
        blank=True,
        null=True,
    )
    _virtual_machine = models.ForeignKey(
        to="virtualization.VirtualMachine",
        on_delete=models.CASCADE,
        related_name="_aci_nodes",
        verbose_name=_("Virtual Machine"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_pod",
        "role",
        "node_type",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIPod",)

    # Unique GenericForeignKey validation
    generic_fk_field = "node_object"
    generic_unique_fields = ("aci_pod",)

    class Meta:
        constraints: tuple[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_pod", "node_id"),
                name="%(app_label)s_%(class)s_unique_nodeid_per_pod",
            ),
            models.UniqueConstraint(
                fields=("aci_pod", "name"),
                name="%(app_label)s_%(class)s_unique_nodename_per_pod",
            ),
            models.UniqueConstraint(
                fields=("node_object_id", "node_object_type"),
                name="%(app_label)s_%(class)s_unique_node_object",
                violation_error_message=_("ACI Node must be unique per ACI Fabric."),
            ),
        ]
        ordering: tuple = ("aci_pod", "node_id")
        verbose_name: str = _("ACI Node")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        # Validate object assignment before validation of any other fields
        if self.node_object_type and not (self.node_object or self.node_object_id):
            model_class = self.node_object_type.model_class()
            raise ValidationError(
                {
                    "node_object": _(
                        "The {node_object} field is required, if an Object Type "
                        "is selected.".format(
                            node_object=model_class._meta.verbose_name
                        )
                    )
                }
            )

        super().clean()

        errors = {}

        # Validate Node ID ranges based on Role
        is_apic = self.role == NodeRoleChoices.ROLE_APIC
        if is_apic and self.node_id > 100:
            errors.setdefault("node_id", []).append(
                _("Node ID must be lower than 100 for APIC nodes.")
            )
        elif not is_apic and self.node_id <= 100:
            errors.setdefault("node_id", []).append(
                _(
                    "Node ID must be greater than or equal to 101 for Leaf or Spine nodes."
                )
            )

        # Validate Node Object location matches Pod scope
        if self.node_object and self.aci_pod.scope:
            pod_scope = self.aci_pod.scope
            obj = self.node_object

            # Build a set of all scopes associated with the node_object
            valid_scopes = set()

            if hasattr(obj, "site") and obj.site:
                valid_scopes.add(obj.site)
                if obj.site.region:
                    valid_scopes.update(
                        obj.site.region.get_ancestors(include_self=True)
                    )
                if obj.site.group:
                    valid_scopes.update(obj.site.group.get_ancestors(include_self=True))

            if getattr(obj, "location", None):
                valid_scopes.update(obj.location.get_ancestors(include_self=True))

            if pod_scope not in valid_scopes:
                # Generate a breadcrumb-style path for the pod scope
                path_components = []
                if hasattr(pod_scope, "get_ancestors"):
                    path_components = [
                        ancestor.name for ancestor in pod_scope.get_ancestors()
                    ]
                path_components.append(pod_scope.name)
                full_path = " / ".join(path_components)

                errors.setdefault("node_object", []).append(
                    _(
                        "The assigned {model} does not match the Pod's scope: {type} ({path})."
                    ).format(
                        model=obj._meta.verbose_name,
                        type=bettertitle(pod_scope._meta.verbose_name),
                        path=full_path,
                    )
                )
        # Validate TEP IP address is contained in the Pod's TEP pool
        # prefix (and match VRF, if applicable)
        if self.tep_ip_address:
            if not (self.aci_pod and self.aci_pod.tep_pool):
                errors.setdefault("tep_ip_address", []).append(
                    _(
                        "Cannot assign a TEP IP address when the Pod "
                        "has no TEP Pool configured."
                    )
                )
            else:
                tep_pool = self.aci_pod.tep_pool

                # VRF must match the Pod's TEP Pool VRF
                if self.tep_ip_address.vrf_id != tep_pool.vrf_id:
                    tep_pool_vrf = getattr(tep_pool.vrf, "name", "None")
                    errors.setdefault("tep_ip_address", []).append(
                        _(
                            "TEP IP VRF must match the Pod's TEP Pool VRF {vrf_name}."
                        ).format(vrf_name=tep_pool_vrf)
                    )
                # Host IP must fall inside the pool prefix
                if self.tep_ip_address.address.ip not in tep_pool.prefix:
                    errors.setdefault("tep_ip_address", []).append(
                        _(
                            "The assigned TEP IP address is not within "
                            "the Pod's TEP Pool prefix ({prefix})."
                        ).format(prefix=str(tep_pool.prefix))
                    )
                # Mask must match the pool mask (/len)
                if self.tep_ip_address.address.prefixlen != tep_pool.prefix.prefixlen:
                    errors.setdefault("tep_ip_address", []).append(
                        _(
                            "TEP IP mask length (/{ip_plen}) must "
                            "match the Pod's TEP Pool mask length "
                            "(/{pool_plen})."
                        ).format(
                            ip_plen=self.tep_ip_address.address.prefixlen,
                            pool_plen=tep_pool.prefix.prefixlen,
                        )
                    )

        if errors:
            raise ValidationError(errors)

        # Perform the mixin's unique constraint validation
        self._validate_generic_uniqueness()

    def save(self, *args, **kwargs) -> None:
        """Save the current instance to the database."""
        # Cache the related objects for faster access
        self.cache_related_objects()

        super().save(*args, **kwargs)

    def cache_related_objects(self) -> None:
        """Cache the related objects for faster access."""
        self._device = self._virtual_machine = None
        if self.node_object_type:
            node_object_type = self.node_object_type.model_class()
            if node_object_type == apps.get_model("dcim", "Device"):
                self._device = self.node_object
            elif node_object_type == apps.get_model("virtualization", "VirtualMachine"):
                self._virtual_machine = self.node_object

    cache_related_objects.alters_data = True

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric instance of related ACIPod."""
        return self.aci_pod.aci_fabric

    @property
    def parent_object(self) -> ACIFabricBaseModel:
        """Return the parent object of the instance."""
        return self.aci_pod

    def get_role_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return NodeRoleChoices.colors.get(self.role)

    def get_node_type_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return NodeTypeChoices.colors.get(self.node_type)


#
# Generic Relations: ACINode
#

GenericRelation(
    to=ACINode,
    content_type_field="node_object_type",
    object_id_field="node_object_id",
    related_query_name="device",
).contribute_to_class(Device, name="aci_nodes")

GenericRelation(
    to=ACINode,
    content_type_field="node_object_type",
    object_id_field="node_object_id",
    related_query_name="virtual_machine",
).contribute_to_class(VirtualMachine, name="aci_nodes")
