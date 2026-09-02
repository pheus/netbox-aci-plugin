# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Model for ACI fabric nodes (leaf, spine, and APIC)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from utilities.templatetags.builtins.filters import bettertitle
from virtualization.models import VirtualMachine

from ...choices import NodeRoleChoices, NodeTypeChoices
from ...constants import NODE_ID_MAX, NODE_ID_MIN, NODE_OBJECT_TYPES
from ..base import ACIFabricBaseModel
from ..mixins import UniqueGenericForeignKeyMixin

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from ..access_policies.leaf_switch_profiles import ACILeafSwitchProfile
    from ..fabric.fabrics import ACIFabric
    from .vpc_protection_groups import ACIVPCProtectionGroup


class ACINode(ACIFabricBaseModel, UniqueGenericForeignKeyMixin):
    """Fabric switch or controller (leaf, spine, or APIC).

    Parented by an ACIPod and optionally linked to a NetBox device
    or virtual machine through a generic foreign key. May carry a
    TEP IP address drawn from the pod's TEP pool.

    Notes:
        APIC node IDs are below 100; leaf and spine node IDs start
        at 101. Node IDs are unique per ACI Fabric, not per ACI Pod.
        A TEP IP must sit within the pod's TEP pool prefix and share
        its VRF and mask length. A given device or virtual machine
        can back only one node. A Node that belongs to a VPC
        Protection Group must keep its ACI Pod and stay a Leaf.
    """

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
            "The functional role of the node within the ACI fabric topology "
            "(e.g., Spine, Leaf, or APIC)."
        ),
    )
    node_type = models.CharField(
        verbose_name=_("Type"),
        max_length=16,
        default=NodeTypeChoices.TYPE_UNKNOWN,
        choices=NodeTypeChoices,
        help_text=_(
            "The specific deployment type of the node, such as a virtual leaf, "
            "a remote leaf over WAN, or a Tier-2 leaf."
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

    # Cached ACIFabric of the related ACIPod, for per-fabric node ID
    # uniqueness and fast scope access
    _aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("ACI Fabric (cached)"),
        blank=True,
        editable=False,
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

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("_aci_fabric", "node_id"),
                name="%(app_label)s_%(class)s_uniq_nodeid_per_fabric",
                violation_error_message=_(
                    "ACI Node IDs must be unique per ACI Fabric."
                ),
            ),
            models.UniqueConstraint(
                fields=("aci_pod", "name"),
                name="%(app_label)s_%(class)s_unique_nodename_per_pod",
            ),
            models.UniqueConstraint(
                fields=("node_object_type", "node_object_id"),
                condition=models.Q(
                    node_object_type__isnull=False,
                    node_object_id__isnull=False,
                ),
                name="%(app_label)s_%(class)s_unique_assigned_node_object",
                violation_error_message=_(
                    "The selected object is already assigned to another ACI Node."
                ),
            ),
        ]
        default_related_name: str = "aci_nodes"
        ordering: tuple = ("aci_pod", "node_id")
        verbose_name: str = _("ACI Node")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        # Populate the fabric-scope and node-object caches before any
        # validation below reads them
        self.cache_related_objects()

        # Validate object assignment before validation of any other fields
        if self.node_object_type and not (self.node_object or self.node_object_id):
            model_class = self.node_object_type.model_class()
            raise ValidationError(
                {
                    "node_object": _(
                        "The {node_object} field is required, if an Object Type "
                        "is selected."
                    ).format(node_object=model_class._meta.verbose_name)
                }
            )

        super().clean()

        errors = {}

        # Validate Node ID ranges based on Role
        is_apic = self.role == NodeRoleChoices.ROLE_APIC
        if self.node_id is not None:
            if is_apic and self.node_id > 100:
                errors.setdefault("node_id", []).append(
                    _("Node ID must be lower than 100 for APIC nodes.")
                )
            elif not is_apic and self.node_id <= 100:
                errors.setdefault("node_id", []).append(
                    _(
                        "Node ID must be greater than or equal to 101 for Leaf "
                        "or Spine nodes."
                    )
                )

        # The ModelForm path adds _aci_fabric to the validation
        # exclusions because it is editable=False, so the constraint is
        # never checked there and this guard carries the enforcement
        if self._aci_fabric_id and self.node_id is not None:
            duplicate_nodes = ACINode.objects.filter(
                _aci_fabric_id=self._aci_fabric_id, node_id=self.node_id
            )
            if self.pk:
                duplicate_nodes = duplicate_nodes.exclude(pk=self.pk)
            if duplicate_nodes.exists():
                errors.setdefault("node_id", []).append(
                    _("An ACI Node with this Node ID already exists in the ACI Fabric.")
                )

        # Validate Node Object location matches Pod scope
        if self.node_object and self.aci_pod_id and self.aci_pod.scope:
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
                        "The assigned {model} does not match the Pod's scope: "
                        "{type} ({path})."
                    ).format(
                        model=obj._meta.verbose_name,
                        type=bettertitle(pod_scope._meta.verbose_name),
                        path=full_path,
                    )
                )
        # Validate TEP IP address is contained in the Pod's TEP pool
        # prefix (and match VRF, if applicable)
        if self.tep_ip_address:
            if not (self.aci_pod_id and self.aci_pod.tep_pool):
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

        if self.pk:
            # A node in a VPC protection group keeps its ACI Pod and Leaf role
            for field, message in self._get_paired_node_transition_issues().items():
                errors.setdefault(field, []).append(message)

            # A role or Node Object change must not strand the ACI Node
            # Interfaces already recorded on this ACI Node
            if (
                self.role != NodeRoleChoices.ROLE_LEAF
                and self.aci_node_interfaces.exists()
            ):
                errors.setdefault("role", []).append(
                    _(
                        "An ACI Node with assigned ACI Node Interfaces must "
                        "retain the Leaf role. Remove the ACI Node Interfaces "
                        "first."
                    )
                )

            # A cleared Node Object strands every linked row, so the
            # device comparison only applies once one is assigned
            stranded = self.aci_node_interfaces.filter(nb_interface__isnull=False)
            if self.assigned_device is not None:
                stranded = stranded.exclude(nb_interface__device=self.assigned_device)
            if stranded.exists():
                errors.setdefault("node_object", []).append(
                    _(
                        "The assigned device differs from the device of the "
                        "NetBox interfaces assigned to existing ACI Node "
                        "Interfaces."
                    )
                )

            # The Override cannot see an ACI Pod move made on this object
            if (
                self._aci_fabric_id
                and self.aci_node_interfaces.filter(
                    aci_leaf_interface_override__isnull=False
                )
                .exclude(
                    aci_leaf_interface_override__aci_leaf_interface_policy_group__aci_fabric=self._aci_fabric_id
                )
                .exists()
            ):
                errors.setdefault("aci_pod", []).append(
                    _(
                        "The assigned ACI Pod belongs to a different ACI "
                        "Fabric than the ACI Leaf Interface Policy Groups of "
                        "existing ACI Leaf Interface Overrides."
                    )
                )

        if errors:
            raise ValidationError(errors)

        # Only validate uniqueness when the GFK is fully populated, since
        # the constraint's condition exempts the null case
        if self.node_object_type_id and self.node_object_id:
            self._validate_generic_uniqueness()

    def save(self, *args, **kwargs) -> None:
        """Save the current instance to the database."""
        # Cache the related objects for faster access
        self.cache_related_objects()

        # Persist the whole node object relation and its derived caches
        # whenever any part of that relation is being saved
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            if {"aci_pod", "aci_pod_id"} & update_fields:
                update_fields.add("_aci_fabric")
            if {
                "node_object_type",
                "node_object_type_id",
                "node_object_id",
            } & update_fields:
                update_fields.update(
                    {
                        "node_object_type",
                        "node_object_id",
                        "_device",
                        "_virtual_machine",
                    }
                )
            kwargs["update_fields"] = update_fields

        # Re-check the paired-node transition here, limited to the
        # fields this save actually persists
        check_pod = update_fields is None or bool(
            {"aci_pod", "aci_pod_id"} & update_fields
        )
        check_role = update_fields is None or "role" in update_fields
        if self.pk and (check_pod or check_role):
            issues = self._get_paired_node_transition_issues(
                check_pod=check_pod, check_role=check_role
            )
            if issues:
                raise ValidationError(list(issues.values()))

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

        if not self.aci_pod_id:
            self._aci_fabric_id = None
            return

        # Read the stored ACI Pod, not the in-memory relation: this cache
        # backs a uniqueness constraint and must not follow an unsaved parent
        self._aci_fabric_id = (
            apps.get_model("netbox_aci_plugin", "ACIPod")
            .objects.filter(pk=self.aci_pod_id)
            .values_list("aci_fabric_id", flat=True)
            .first()
        )

    cache_related_objects.alters_data = True

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric instance of related ACIPod."""
        return self.aci_pod.aci_fabric

    @property
    def parent_object(self) -> ACIFabricBaseModel:
        """Return the parent object of the instance."""
        return self.aci_pod

    @property
    def assigned_device(self) -> Device | None:
        """Return the NetBox device assigned to the node, if any.

        Named "assigned" because the plain "device" attribute is already
        taken by the reverse relation from dcim.Device.
        """
        return self._device

    @cached_property
    def vpc_protection_group(self) -> ACIVPCProtectionGroup | None:
        """Return the VPC protection group this node is a member of."""
        protection_group_model = apps.get_model(
            "netbox_aci_plugin", "ACIVPCProtectionGroup"
        )
        try:
            return protection_group_model.objects.select_related(
                "aci_node_a", "aci_node_b"
            ).get(models.Q(aci_node_a=self) | models.Q(aci_node_b=self))
        except protection_group_model.DoesNotExist:
            return None

    @property
    def vpc_peer_node(self) -> ACINode | None:
        """Return the other node in this node's VPC Protection Group."""
        group = self.vpc_protection_group
        if group is None:
            return None
        return group.aci_node_b if group.aci_node_a_id == self.pk else group.aci_node_a

    @property
    def aci_leaf_switch_profiles(self) -> QuerySet[ACILeafSwitchProfile]:
        """Return every ACI Leaf Switch Profile whose blocks cover this Node.

        Walks node blocks up through their selector to the profile in
        one query. A Node's ID can fall within more than one profile's
        coverage, so this returns a queryset rather than a single
        object, and stays lazy so a caller can restrict it.
        """
        profile_model = apps.get_model("netbox_aci_plugin", "ACILeafSwitchProfile")
        if self.role != NodeRoleChoices.ROLE_LEAF:
            return profile_model.objects.none()
        return profile_model.objects.filter(
            aci_fabric_id=self._aci_fabric_id,
            aci_leaf_selectors__aci_leaf_node_blocks__node_id_from__lte=self.node_id,
            aci_leaf_selectors__aci_leaf_node_blocks__node_id_to__gte=self.node_id,
        ).distinct()

    def get_role_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return NodeRoleChoices.colors.get(self.role)

    def get_node_type_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return NodeTypeChoices.colors.get(self.node_type)

    def _get_paired_node_transition_issues(
        self, check_pod: bool = True, check_role: bool = True
    ) -> dict[str, str]:
        """Return field-to-message issues for a paired-node transition.

        Empty when the node is not a member of a VPC protection group.
        Callers must only invoke this when ``self.pk`` is set. Uses an
        existence query rather than the ``vpc_protection_group``
        property, which raises on a corrupt double membership and would
        turn a routine edit into a server error.

        ``check_pod`` and ``check_role`` narrow the check to the fields
        a partial update persists. Full validation leaves both enabled.
        """
        protection_group_model = apps.get_model(
            "netbox_aci_plugin", "ACIVPCProtectionGroup"
        )
        is_paired = protection_group_model.objects.filter(
            models.Q(aci_node_a=self) | models.Q(aci_node_b=self)
        ).exists()
        if not is_paired:
            return {}

        stored = ACINode.objects.only("aci_pod_id", "role").get(pk=self.pk)

        issues: dict[str, str] = {}
        if check_pod and stored.aci_pod_id != self.aci_pod_id:
            issues["aci_pod"] = _(
                "An ACI Node that belongs to a VPC Protection Group cannot "
                "be moved to another ACI Pod. Remove the Protection Group "
                "first."
            )
        if check_role and self.role != NodeRoleChoices.ROLE_LEAF:
            issues["role"] = _(
                "An ACI Node that belongs to a VPC Protection Group must "
                "retain the Leaf role."
            )
        return issues


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
