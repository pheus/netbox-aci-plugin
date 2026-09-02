# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Model for ACI pods within a fabric."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from dcim.models.mixins import CachedScopeMixin

from ...constants import POD_ID_MAX, POD_ID_MIN
from ..base import ACIFabricBaseModel
from .nodes import ACINode

if TYPE_CHECKING:
    from ..fabric.fabrics import ACIFabric


@dataclass
class _PodFabricMoveContext:
    """Resolved state of a pending ACIPod fabric move.

    Carries ACI VPC Protection Group IDs rather than loaded instances,
    so the cascade re-reads each row instead of writing back a stale
    snapshot.
    """

    issues: list[str]
    affected_group_ids: list[int]


class ACIPod(CachedScopeMixin, ACIFabricBaseModel):
    """Pod (a leaf-spine cluster) within an ACI Fabric.

    Parented by an ACIFabric and may be scoped to a NetBox site or
    location. Holds the TEP pool from which member nodes draw their
    tunnel endpoint addresses.

    Notes:
        The TEP pool must be an IPv4 unicast prefix no more specific
        than /21. Moving the Pod to another ACI Fabric cascades to its
        child ACI Nodes and ACI VPC Protection Groups, and is refused
        on a Node ID or Protection Group conflict in the target Fabric.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_pods",
        verbose_name=_("ACI Fabric"),
    )
    pod_id = models.PositiveSmallIntegerField(
        verbose_name=_("Pod ID"),
        validators=[
            MinValueValidator(POD_ID_MIN),
            MaxValueValidator(POD_ID_MAX),
        ],
    )
    tep_pool = models.ForeignKey(
        to="ipam.Prefix",
        on_delete=models.SET_NULL,
        related_name="aci_pods",
        verbose_name=_("TEP Pool"),
        blank=True,
        null=True,
        help_text=_(
            "The internal TEP pool used to assign Tunnel Endpoint (TEP) "
            "addresses to leaf and spine nodes within the pod."
        ),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_fabric",
        "scope_type",
        "scope_id",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "pod_id"),
                name="%(app_label)s_%(class)s_unique_pod_per_aci_fabric",
            ),
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_unique_pod_name_per_aci_fabric",
            ),
        ]
        default_related_name: str = "aci_pods"
        ordering: tuple = ("aci_fabric", "pod_id")
        verbose_name: str = _("ACI Pod")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        # Ensure tep_pool is an IPv4 unicast prefix with a prefix
        # length of /0-/21 (inclusive).
        if self.tep_pool and (
            self.tep_pool.prefix.version != 4
            or self.tep_pool.prefix.prefixlen > 21
            or self.tep_pool.prefix.is_multicast()
        ):
            errors.setdefault("tep_pool", []).append(
                _("TEP Pool must be an IPv4 unicast prefix no more specific than /21.")
            )

        # Validate a pending ACI Fabric move against the target Fabric
        context = self._build_fabric_move_context()
        if context and context.issues:
            for issue in context.issues:
                errors.setdefault("aci_fabric", []).append(issue)

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        """Save the current instance, cascading a pending ACI Fabric move."""
        # update_fields may be a one-shot iterable, so materialize it first
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            kwargs["update_fields"] = update_fields
        fabric_will_be_saved = update_fields is None or bool(
            {"aci_fabric", "aci_fabric_id"} & update_fields
        )

        with transaction.atomic():
            # Resolve immediately before the write, so validation and
            # cascade describe one transition. Skipped when this save
            # cannot persist the Fabric, whose result would be discarded
            context = (
                self._build_fabric_move_context() if fabric_will_be_saved else None
            )
            fabric_changed = context is not None
            if fabric_changed and context.issues:
                raise ValidationError(list(context.issues))

            super().save(*args, **kwargs)

            if fabric_changed:
                # Private cache: bulk update, no lifecycle effects wanted
                self.aci_nodes.update(_aci_fabric_id=self.aci_fabric_id)

                # Public field: per-object saves, so the fabric change goes
                # through the normal save path rather than raw SQL
                protection_group_model = apps.get_model(
                    "netbox_aci_plugin", "ACIVPCProtectionGroup"
                )
                for protection_group in protection_group_model.objects.filter(
                    pk__in=context.affected_group_ids
                ):
                    protection_group.snapshot()
                    protection_group.aci_fabric_id = self.aci_fabric_id
                    # last_updated is auto_now and only advances when named
                    protection_group.save(update_fields={"aci_fabric", "last_updated"})

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric

    def _build_fabric_move_context(self) -> _PodFabricMoveContext | None:
        """Return the resolved state of a pending ACI Fabric move, or None.

        None means no move is pending. Otherwise resolves the target
        Fabric's Node ID and Protection Group conflicts, any Protection
        Group split across two Pods, and the Protection Group IDs to
        cascade.

        Builds fresh on every call. Do not memoize the result: the
        target Fabric and the Protection Group set are both mutable, so
        a cached resolution would let save() cascade a transition that
        clean() never validated.
        """
        if not self.pk:
            return None

        context = None
        # A missing row means there is no stored Fabric to move away from,
        # so degrade to "no move pending" rather than raising
        stored_fabric_id = (
            ACIPod.objects.filter(pk=self.pk)
            .values_list("aci_fabric_id", flat=True)
            .first()
        )
        if stored_fabric_id is not None and stored_fabric_id != self.aci_fabric_id:
            protection_group_model = apps.get_model(
                "netbox_aci_plugin", "ACIVPCProtectionGroup"
            )
            issues: list[str] = []

            # The target ACI Fabric may already use one of these Node IDs
            conflicting_node_ids = sorted(
                set(
                    ACINode.objects.filter(
                        _aci_fabric_id=self.aci_fabric_id,
                        node_id__in=self.aci_nodes.values_list("node_id", flat=True),
                    )
                    .exclude(aci_pod=self)
                    .values_list("node_id", flat=True)
                )
            )
            if conflicting_node_ids:
                issues.append(
                    _(
                        "The target ACI Fabric already has ACI Nodes using "
                        "these Node IDs: {node_ids}."
                    ).format(node_ids=", ".join(str(n) for n in conflicting_node_ids))
                )

            # The ACI VPC Protection Groups formed by this Pod's Nodes.
            collected_groups = protection_group_model.objects.filter(
                models.Q(aci_node_a__aci_pod=self) | models.Q(aci_node_b__aci_pod=self)
            )

            # The target ACI Fabric may already have a Protection Group
            # with a colliding name or logical pair ID
            conflicting_groups = list(
                protection_group_model.objects.filter(aci_fabric_id=self.aci_fabric_id)
                .filter(
                    models.Q(name__in=collected_groups.values("name"))
                    | models.Q(
                        logical_pair_id__in=collected_groups.values("logical_pair_id")
                    )
                )
                .exclude(pk__in=collected_groups.values("pk"))
            )
            if conflicting_groups:
                issues.append(
                    _(
                        "The target ACI Fabric already has ACI VPC "
                        "Protection Groups with a conflicting name or "
                        "logical pair ID: {groups}."
                    ).format(
                        groups=", ".join(
                            f"{group.name} ({group.logical_pair_id})"
                            for group in conflicting_groups
                        )
                    )
                )

            # Validation keeps a pair in one Pod, but unvalidated data
            # can straddle two. Refuse rather than move a half-present
            # Protection Group.
            straddling_groups = list(
                collected_groups.exclude(
                    aci_node_a__aci_pod=self, aci_node_b__aci_pod=self
                )
            )
            if straddling_groups:
                issues.append(
                    _(
                        "The following ACI VPC Protection Groups have "
                        "members in more than one ACI Pod and must be "
                        "corrected before this ACI Pod can move: {groups}."
                    ).format(
                        groups=", ".join(group.name for group in straddling_groups)
                    )
                )

            # The Override cannot see an ACI Fabric move made on this object
            override_model = apps.get_model(
                "netbox_aci_plugin", "ACILeafInterfaceOverride"
            )
            stranded_overrides = list(
                override_model.objects.filter(
                    aci_node_interface__aci_node__aci_pod=self
                )
                .exclude(
                    aci_leaf_interface_policy_group__aci_fabric_id=self.aci_fabric_id
                )
                .select_related("aci_node_interface__aci_node")[:10]
            )
            if stranded_overrides:
                issues.append(
                    _(
                        "The ACI Leaf Interface Overrides on these ACI Node "
                        "Interfaces reference an ACI Leaf Interface Policy "
                        "Group in another ACI Fabric: {interfaces}."
                    ).format(
                        interfaces=", ".join(
                            sorted(
                                str(override.aci_node_interface)
                                for override in stranded_overrides
                            )
                        )
                    )
                )

            context = _PodFabricMoveContext(
                issues=issues,
                affected_group_ids=list(collected_groups.values_list("pk", flat=True)),
            )

        return context
