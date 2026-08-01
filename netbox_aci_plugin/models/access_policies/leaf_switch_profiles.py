# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Models for ACI access-policy Leaf Switch Profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _

from ...choices import NodeRoleChoices
from ...constants import LEAF_NODE_ID_MIN, NODE_ID_MAX
from ..base import ACIFabricBaseModel
from ..fabric.nodes import ACINode

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models import ObjectChange

    from ..fabric.fabrics import ACIFabric


class ACILeafSwitchProfile(ACIFabricBaseModel):
    """ACI Leaf Switch Profile (infraNodeP) scoped to a fabric.

    Groups the selectors that select the leaf nodes an interface
    profile applies to.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_leaf_switch_profiles",
        verbose_name=_("ACI Fabric"),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + ("aci_fabric",)
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_uniq_name_per_fabric",
            ),
        ]
        default_related_name: str = "aci_leaf_switch_profiles"
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI Leaf Switch Profile")

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric


class ACILeafSelector(ACIFabricBaseModel):
    """ACI Leaf Selector (infraLeafS) within a leaf switch profile.

    Names leaf nodes through its node blocks. Only the range
    selector type is modeled.
    """

    aci_leaf_switch_profile = models.ForeignKey(
        to="netbox_aci_plugin.ACILeafSwitchProfile",
        on_delete=models.CASCADE,
        related_name="aci_leaf_selectors",
        verbose_name=_("ACI Leaf Switch Profile"),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + ("aci_leaf_switch_profile",)
    prerequisite_models: tuple = ("netbox_aci_plugin.ACILeafSwitchProfile",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_leaf_switch_profile", "name"),
                name="%(app_label)s_%(class)s_uniq_name_per_profile",
            ),
        ]
        default_related_name: str = "aci_leaf_selectors"
        ordering: tuple = ("aci_leaf_switch_profile", "name")
        verbose_name: str = _("ACI Leaf Selector")

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_leaf_switch_profile
        return objectchange

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric of the related ACILeafSwitchProfile."""
        return self.aci_leaf_switch_profile.aci_fabric

    @property
    def parent_object(self) -> ACILeafSwitchProfile:
        """Return the parent object of the instance."""
        return self.aci_leaf_switch_profile

    @property
    def aci_nodes(self) -> QuerySet[ACINode]:
        """Return the leaf ACI Nodes covered by the selector's blocks."""
        blocks = self.aci_leaf_node_blocks.all()
        if not blocks:
            return ACINode.objects.none()
        node_id_q = models.Q()
        for block in blocks:
            node_id_q |= block.node_id_query
        return ACINode.objects.filter(
            node_id_q,
            _aci_fabric_id=self.aci_leaf_switch_profile.aci_fabric_id,
            role=NodeRoleChoices.ROLE_LEAF,
        )


class ACILeafNodeBlock(ACIFabricBaseModel):
    """ACI Leaf Node Block (infraNodeBlk) within a leaf selector.

    A contiguous ACI node ID range covered by its selector.
    """

    aci_leaf_selector = models.ForeignKey(
        to="netbox_aci_plugin.ACILeafSelector",
        on_delete=models.CASCADE,
        related_name="aci_leaf_node_blocks",
        verbose_name=_("ACI Leaf Selector"),
    )
    node_id_from = models.PositiveSmallIntegerField(
        verbose_name=_("Node ID (from)"),
        validators=[
            MinValueValidator(LEAF_NODE_ID_MIN),
            MaxValueValidator(NODE_ID_MAX),
        ],
    )
    node_id_to = models.PositiveSmallIntegerField(
        verbose_name=_("Node ID (to)"),
        validators=[
            MinValueValidator(LEAF_NODE_ID_MIN),
            MaxValueValidator(NODE_ID_MAX),
        ],
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + ("aci_leaf_selector",)
    prerequisite_models: tuple = ("netbox_aci_plugin.ACILeafSelector",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_leaf_selector", "name"),
                name="%(app_label)s_%(class)s_uniq_name_per_selector",
            ),
        ]
        default_related_name: str = "aci_leaf_node_blocks"
        ordering: tuple = ("aci_leaf_selector", "node_id_from")
        verbose_name: str = _("ACI Leaf Node Block")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if (
            self.node_id_from is not None
            and self.node_id_to is not None
            and self.node_id_from > self.node_id_to
        ):
            errors.setdefault("node_id_to", []).append(
                _("The starting Node ID must not be greater than the ending Node ID.")
            )

        if errors:
            raise ValidationError(errors)

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_leaf_selector
        return objectchange

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric of the related ACILeafSelector."""
        return self.aci_leaf_selector.aci_fabric

    @property
    def parent_object(self) -> ACILeafSelector:
        """Return the parent object of the instance."""
        return self.aci_leaf_selector

    @property
    def node_id_query(self) -> models.Q:
        """Return the node ID lookup covering the block's range."""
        return models.Q(node_id__gte=self.node_id_from, node_id__lte=self.node_id_to)

    @property
    def aci_nodes(self) -> QuerySet[ACINode]:
        """Return the leaf ACI Nodes covered by the block's ID range."""
        selector = self.aci_leaf_selector
        return ACINode.objects.filter(
            self.node_id_query,
            _aci_fabric_id=selector.aci_leaf_switch_profile.aci_fabric_id,
            role=NodeRoleChoices.ROLE_LEAF,
        )

    @staticmethod
    def aci_node_count_annotation() -> Coalesce:
        """Return a Subquery annotation counting a block's covered ACI Nodes.

        A correlated Subquery avoids the per-row query the aci_nodes
        property would need when resolved on every table row. Coalesce
        keeps a block covering no ACI Nodes at 0 instead of NULL.
        """
        count_subquery = (
            ACINode.objects.filter(
                _aci_fabric=models.OuterRef(
                    "aci_leaf_selector__aci_leaf_switch_profile__aci_fabric"
                ),
                role=NodeRoleChoices.ROLE_LEAF,
                node_id__gte=models.OuterRef("node_id_from"),
                node_id__lte=models.OuterRef("node_id_to"),
            )
            .order_by()
            .values("_aci_fabric")
            .annotate(c=models.Count("pk"))
            .values("c")
        )
        return Coalesce(
            models.Subquery(count_subquery, output_field=models.IntegerField()), 0
        )
