# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Models for ACI Endpoint Group domain bindings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel

from ...choices import (
    DeploymentImmediacyChoices,
    PortModeChoices,
    ResolutionImmediacyChoices,
)
from ...constants import (
    EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES,
    EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES,
    VLAN_VID_MAX,
    VLAN_VID_MIN,
)
from ..mixins import UniqueGenericForeignKeyMixin

if TYPE_CHECKING:
    from core.models import ObjectChange

    from ..access_policies.aaep import ACIAttachableAccessEntityProfile
    from ..fabric.fabrics import ACIFabric
    from .endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
    from .tenants import ACITenant


class ACIEndpointGroupDomainBinding(NetBoxModel, UniqueGenericForeignKeyMixin):
    """Association of an ACI Endpoint Group with an ACI domain (fvRsDomAtt).

    Links an ACIEndpointGroup or ACIUSegEndpointGroup to an ACI domain
    through generic foreign keys, mirrored into cached foreign keys for
    efficient querying. This binding is a prerequisite every EPG
    deployment method requires.

    Notes:
        The referenced domain must belong to the same ACI Fabric as the
        Endpoint Group.
    """

    aci_epg_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES,
        verbose_name=_("ACI EPG object type"),
        blank=True,
        null=True,
    )
    aci_epg_object_id = models.PositiveBigIntegerField(
        verbose_name=_("ACI EPG object ID"),
        blank=True,
        null=True,
    )
    aci_epg_object = GenericForeignKey(
        ct_field="aci_epg_object_type",
        fk_field="aci_epg_object_id",
    )
    aci_domain_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES,
        verbose_name=_("ACI domain object type"),
        blank=True,
        null=True,
    )
    aci_domain_object_id = models.PositiveBigIntegerField(
        verbose_name=_("ACI domain object ID"),
        blank=True,
        null=True,
    )
    aci_domain_object = GenericForeignKey(
        ct_field="aci_domain_object_type",
        fk_field="aci_domain_object_id",
    )
    deployment_immediacy = models.CharField(
        verbose_name=_("deployment immediacy"),
        max_length=9,
        default=DeploymentImmediacyChoices.IMMEDIACY_LAZY,
        choices=DeploymentImmediacyChoices,
        help_text=_(
            "When the policy is pushed into the leaf hardware. Default is 'On Demand'."
        ),
    )
    resolution_immediacy = models.CharField(
        verbose_name=_("resolution immediacy"),
        max_length=13,
        default=ResolutionImmediacyChoices.IMMEDIACY_LAZY,
        choices=ResolutionImmediacyChoices,
        help_text=_(
            "When the policy is downloaded to the leaf software. Default is "
            "'On Demand'."
        ),
    )

    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    # Cached related objects by association name for faster access
    _aci_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIEndpointGroup",
        on_delete=models.CASCADE,
        related_name="_aci_endpoint_group_domain_bindings",
        verbose_name=_("ACI Endpoint Group"),
        blank=True,
        null=True,
    )
    _aci_useg_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIUSegEndpointGroup",
        on_delete=models.CASCADE,
        related_name="_aci_endpoint_group_domain_bindings",
        verbose_name=_("ACI uSeg Endpoint Group"),
        blank=True,
        null=True,
    )
    _aci_physical_domain = models.ForeignKey(
        to="netbox_aci_plugin.ACIPhysicalDomain",
        on_delete=models.CASCADE,
        related_name="_aci_endpoint_group_domain_bindings",
        verbose_name=_("ACI Physical Domain"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = (
        "aci_epg_object_type",
        "aci_domain_object_type",
        "deployment_immediacy",
        "resolution_immediacy",
    )

    # Unique GenericForeignKey validation
    generic_fk_field = "aci_epg_object"
    generic_unique_fields = ("aci_domain_object_type", "aci_domain_object_id")

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=(
                    "aci_epg_object_type",
                    "aci_epg_object_id",
                    "aci_domain_object_type",
                    "aci_domain_object_id",
                ),
                name="%(app_label)s_%(class)s_unique_aci_domain_object_per_epg",
            ),
        ]
        default_related_name: str = "aci_endpoint_group_domain_bindings"
        indexes: tuple = (
            models.Index(fields=("aci_epg_object_type", "aci_epg_object_id")),
            models.Index(fields=("aci_domain_object_type", "aci_domain_object_id")),
        )
        ordering: tuple = (
            "_aci_endpoint_group",
            "_aci_useg_endpoint_group",
            "_aci_physical_domain",
        )
        verbose_name: str = _("ACI Endpoint Group Domain Binding")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.aci_epg_object} - {self.aci_domain_object}"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        # Validate EPG object assignment before validation of other fields
        if self.aci_epg_object_type_id and not (
            self.aci_epg_object or self.aci_epg_object_id
        ):
            aci_model_class = self.aci_epg_object_type.model_class()
            raise ValidationError(
                {
                    "aci_epg_object": _(
                        "The {aci_epg_object} field is required, if an ACI "
                        "EPG object type is selected."
                    ).format(aci_epg_object=aci_model_class._meta.verbose_name)
                }
            )

        # Validate domain object assignment before validation of other fields
        if self.aci_domain_object_type_id and not (
            self.aci_domain_object or self.aci_domain_object_id
        ):
            aci_model_class = self.aci_domain_object_type.model_class()
            raise ValidationError(
                {
                    "aci_domain_object": _(
                        "The {aci_domain_object} field is required, if an ACI "
                        "domain object type is selected."
                    ).format(aci_domain_object=aci_model_class._meta.verbose_name)
                }
            )

        super().clean()

        errors = {}

        # Validate the domain object belongs to the same ACI Fabric as the
        # endpoint group
        if (
            self.aci_epg_object_id
            and self.aci_domain_object_id
            and hasattr(self.aci_epg_object, "aci_fabric")
            and hasattr(self.aci_domain_object, "aci_fabric")
            and self.aci_epg_object.aci_fabric != self.aci_domain_object.aci_fabric
        ):
            aci_epg_model_class = self.aci_epg_object_type.model_class()
            aci_domain_model_class = self.aci_domain_object_type.model_class()
            errors.setdefault("aci_domain_object", []).append(
                _(
                    "The assigned {aci_domain_object} must belong to the "
                    "same ACI Fabric as the {aci_epg_object}."
                ).format(
                    aci_domain_object=aci_domain_model_class._meta.verbose_name,
                    aci_epg_object=aci_epg_model_class._meta.verbose_name,
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
        self._aci_endpoint_group = self._aci_useg_endpoint_group = None
        self._aci_physical_domain = None
        if self.aci_epg_object_type:
            aci_epg_object_type = self.aci_epg_object_type.model_class()
            if aci_epg_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIEndpointGroup"
            ):
                self._aci_endpoint_group = self.aci_epg_object
            elif aci_epg_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIUSegEndpointGroup"
            ):
                self._aci_useg_endpoint_group = self.aci_epg_object
        if self.aci_domain_object_type:
            aci_domain_object_type = self.aci_domain_object_type.model_class()
            if aci_domain_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIPhysicalDomain"
            ):
                self._aci_physical_domain = self.aci_domain_object

    cache_related_objects.alters_data = True

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_epg_object
        return objectchange

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ACI EPG object."""
        return self.aci_epg_object.aci_tenant

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric instance of the related ACI Tenant."""
        return self.aci_tenant.aci_fabric

    @property
    def parent_object(self) -> ACIEndpointGroup | ACIUSegEndpointGroup:
        """Return the parent object of the instance."""
        return self.aci_epg_object

    def get_deployment_immediacy_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return DeploymentImmediacyChoices.colors.get(self.deployment_immediacy)

    def get_resolution_immediacy_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return ResolutionImmediacyChoices.colors.get(self.resolution_immediacy)


class ACIEndpointGroupVLANBindingBase(NetBoxModel):
    """Abstract base for VLAN-encapsulated regular-EPG deployment bindings.

    Carries the reference to the ACI Endpoint Group and the VLAN encapsulation,
    either linked to a NetBox VLAN or entered directly as a VLAN ID. The encap
    VLAN ID is snapshotted from the NetBox VLAN on save and survives its
    deletion.
    """

    aci_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIEndpointGroup",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name=_("ACI Endpoint Group"),
    )
    nb_vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.SET_NULL,
        related_name="%(class)ss",
        verbose_name=_("NetBox VLAN"),
        blank=True,
        null=True,
    )
    encap_vlan_id = models.PositiveSmallIntegerField(
        verbose_name=_("encap VLAN ID"),
        validators=[
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX),
        ],
        blank=True,
        null=True,
        help_text=_(
            "VLAN encapsulation of the deployment. Snapshotted from the "
            "NetBox VLAN when one is assigned."
        ),
    )
    primary_nb_vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("primary NetBox VLAN"),
        blank=True,
        null=True,
    )
    primary_encap_vlan_id = models.PositiveSmallIntegerField(
        verbose_name=_("primary encap VLAN ID"),
        validators=[
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX),
        ],
        blank=True,
        null=True,
        help_text=_(
            "Primary VLAN encapsulation used when the deployment requires a paired "
            "encapsulation, for example for intra-EPG isolation."
        ),
    )
    mode = models.CharField(
        verbose_name=_("mode"),
        max_length=8,
        choices=PortModeChoices,
        default=PortModeChoices.MODE_REGULAR,
        help_text=_("VLAN tagging mode of the deployment. Default is 'Trunk'."),
    )
    deployment_immediacy = models.CharField(
        verbose_name=_("deployment immediacy"),
        max_length=9,
        default=DeploymentImmediacyChoices.IMMEDIACY_LAZY,
        choices=DeploymentImmediacyChoices,
        help_text=_(
            "When the policy is pushed into the leaf hardware. Default is 'On Demand'."
        ),
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    class Meta:
        abstract = True

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        # An encapsulation source is required
        if not self.nb_vlan_id and self.encap_vlan_id is None:
            errors.setdefault("encap_vlan_id", []).append(
                _("Either a NetBox VLAN or an encap VLAN ID is required.")
            )

        # The main NetBox VLAN and encap VLAN ID must agree when both are set
        if (
            self.nb_vlan_id
            and self.encap_vlan_id is not None
            and self.nb_vlan.vid != self.encap_vlan_id
        ):
            errors.setdefault("encap_vlan_id", []).append(
                _(
                    "The encap VLAN ID does not match the selected NetBox "
                    "VLAN's ID. Clear the encap VLAN ID to re-sync it from "
                    "the selected VLAN."
                )
            )

        # The primary NetBox VLAN and primary encap VLAN ID must agree
        # when both are set
        if (
            self.primary_nb_vlan_id
            and self.primary_encap_vlan_id is not None
            and self.primary_nb_vlan.vid != self.primary_encap_vlan_id
        ):
            errors.setdefault("primary_encap_vlan_id", []).append(
                _(
                    "The primary encap VLAN ID does not match the selected "
                    "primary NetBox VLAN's ID. Clear the primary encap "
                    "VLAN ID to re-sync it from the selected primary VLAN."
                )
            )

        # A primary encapsulation requires, and must differ from, the main
        # encapsulation
        if self.primary_nb_vlan_id or self.primary_encap_vlan_id is not None:
            if self.effective_encap_vlan_id is None:
                errors.setdefault("primary_encap_vlan_id", []).append(
                    _(
                        "A primary encap VLAN requires a main NetBox VLAN "
                        "or encap VLAN ID to be set."
                    )
                )
            elif self.effective_primary_encap_vlan_id == self.effective_encap_vlan_id:
                errors.setdefault("primary_encap_vlan_id", []).append(
                    _("The primary encap VLAN must differ from the main encap VLAN.")
                )

        # A single shared physical domain's VLAN pool must satisfy the
        # whole binding together: both encap IDs and both NetBox VLAN
        # groups (APIC resolves a deployment through one domain).
        # ACIPhysicalDomain requires a VLAN pool (PROTECT, non-null), so
        # aci_vlan_pool is never None. Dedup by pool pk (several shared
        # domains may point at one pool).
        pools = list(
            {
                physical_domain.aci_vlan_pool_id: physical_domain.aci_vlan_pool
                for physical_domain in self._pool_physical_domains()
            }.values()
        )
        if pools and self.effective_encap_vlan_id is not None:
            candidate_pools = [
                pool for pool in pools if pool.covers_vid(self.effective_encap_vlan_id)
            ]
            if not candidate_pools:
                errors.setdefault("encap_vlan_id", []).append(
                    _(
                        "The encap VLAN ID {vid} is not within any shared "
                        "ACI Physical Domain's ACI VLAN Pool ({pools})."
                    ).format(
                        vid=self.effective_encap_vlan_id,
                        pools=", ".join(pool.name for pool in pools),
                    )
                )
            else:
                if self.effective_primary_encap_vlan_id is not None:
                    candidate_pools = [
                        pool
                        for pool in candidate_pools
                        if pool.covers_vid(self.effective_primary_encap_vlan_id)
                    ]
                if self.effective_primary_encap_vlan_id is not None and (
                    not candidate_pools
                ):
                    errors.setdefault("primary_encap_vlan_id", []).append(
                        _(
                            "No shared ACI Physical Domain's ACI VLAN Pool "
                            "contains both the encap VLAN ID {vid} and the "
                            "primary encap VLAN ID {primary}."
                        ).format(
                            vid=self.effective_encap_vlan_id,
                            primary=self.effective_primary_encap_vlan_id,
                        )
                    )
                else:
                    # candidate_pools now cover both encap IDs. Narrow by the
                    # main NetBox VLAN group, then the primary VLAN group.
                    # The same pool must accept both.
                    main_group_pools = [
                        pool
                        for pool in candidate_pools
                        if self._pool_accepts_nb_vlan(pool, self.nb_vlan)
                    ]
                    if self.nb_vlan_id and not main_group_pools:
                        errors.setdefault("nb_vlan", []).append(
                            _(
                                "The NetBox VLAN must belong to the assigned "
                                "NetBox VLAN group of an ACI VLAN Pool that "
                                "covers the encapsulation."
                            )
                        )
                    elif self.primary_nb_vlan_id and not any(
                        self._pool_accepts_nb_vlan(pool, self.primary_nb_vlan)
                        for pool in main_group_pools
                    ):
                        errors.setdefault("primary_nb_vlan", []).append(
                            _(
                                "The primary NetBox VLAN must belong to the "
                                "assigned NetBox VLAN group of an ACI VLAN "
                                "pool that covers the encapsulation."
                            )
                        )

        if errors:
            raise ValidationError(errors)

    def sync_encap_vlan_ids(self) -> None:
        """Sync the encap VLAN IDs from their NetBox VLANs."""
        if self.nb_vlan_id:
            self.encap_vlan_id = self.nb_vlan.vid
        if self.primary_nb_vlan_id:
            self.primary_encap_vlan_id = self.primary_nb_vlan.vid

    sync_encap_vlan_ids.alters_data = True

    def save(self, *args, **kwargs) -> None:
        """Sync encap VLAN IDs before saving."""
        self.sync_encap_vlan_ids()

        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            synced_fields = {"encap_vlan_id"} if self.nb_vlan_id else set()
            if self.primary_nb_vlan_id:
                synced_fields.add("primary_encap_vlan_id")
            if synced_fields:
                kwargs["update_fields"] = set(update_fields) | synced_fields

        super().save(*args, **kwargs)

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.parent_object
        return objectchange

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric instance of the related ACI Endpoint Group."""
        return self.aci_endpoint_group.aci_fabric

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ACI Endpoint Group."""
        return self.aci_endpoint_group.aci_tenant

    @property
    def parent_object(self) -> ACIEndpointGroup:
        """Return the parent object of the instance."""
        return self.aci_endpoint_group

    @property
    def effective_encap_vlan_id(self) -> int | None:
        """Return the live NetBox VLAN's ID, else the snapshotted ID."""
        if self.nb_vlan_id:
            return self.nb_vlan.vid
        return self.encap_vlan_id

    @property
    def effective_primary_encap_vlan_id(self) -> int | None:
        """Return the live primary NetBox VLAN's ID, else the snapshot."""
        if self.primary_nb_vlan_id:
            return self.primary_nb_vlan.vid
        return self.primary_encap_vlan_id

    def get_mode_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return PortModeChoices.colors.get(self.mode)

    def get_deployment_immediacy_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return DeploymentImmediacyChoices.colors.get(self.deployment_immediacy)

    def _pool_physical_domains(self):
        """Return the Physical Domains whose VLAN Pools constrain the encap."""
        raise NotImplementedError(
            "Concrete VLAN-binding models must implement _pool_physical_domains()."
        )

    @staticmethod
    def _pool_accepts_nb_vlan(pool, nb_vlan) -> bool:
        """Return whether the pool's VLAN group admits the NetBox VLAN."""
        return (
            nb_vlan is None
            or not pool.nb_vlan_group_id
            or nb_vlan.group_id == pool.nb_vlan_group_id
        )


class ACIEndpointGroupAAEPBinding(ACIEndpointGroupVLANBindingBase):
    """Deployment of an EPG on an AAEP's interfaces (infraRsFuncToEpg).

    Statically deploys the Endpoint Group with its VLAN encapsulation on
    all interfaces associated with the Attachable Access Entity Profile.

    Notes:
        The AAEP and the Endpoint Group must share at least one bound
        ACI domain, or the fabric raises fault F0467.
    """

    aci_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIEndpointGroup",
        on_delete=models.CASCADE,
        related_name="aci_aaep_bindings",
        verbose_name=_("ACI Endpoint Group"),
    )
    aci_aaep = models.ForeignKey(
        to="netbox_aci_plugin.ACIAttachableAccessEntityProfile",
        on_delete=models.CASCADE,
        related_name="aci_endpoint_group_bindings",
        verbose_name=_("ACI AAEP"),
    )

    clone_fields: tuple = (
        "aci_endpoint_group",
        "aci_aaep",
        "mode",
        "deployment_immediacy",
    )
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIEndpointGroup",
        "netbox_aci_plugin.ACIAttachableAccessEntityProfile",
    )

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_endpoint_group", "aci_aaep"),
                name="%(app_label)s_%(class)s_unique_binding",
            ),
        ]
        default_related_name: str = "aci_endpoint_group_aaep_bindings"
        ordering: tuple = ("aci_endpoint_group", "aci_aaep")
        verbose_name: str = _("ACI Endpoint Group AAEP Binding")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.aci_endpoint_group} - {self.aci_aaep.name}"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if self.aci_aaep_id and self.aci_endpoint_group_id:
            # The AAEP must belong to the same ACI Fabric as the
            # endpoint group
            if (
                self.aci_aaep.aci_fabric_id
                != self.aci_endpoint_group.aci_app_profile.aci_tenant.aci_fabric_id
            ):
                errors.setdefault("aci_aaep", []).append(
                    _(
                        "The assigned ACI AAEP must belong to the same "
                        "ACI Fabric as the ACI Endpoint Group."
                    )
                )
            # The AAEP and the endpoint group must share at least one
            # bound ACI domain, or the fabric raises fault F0467
            elif not self._pool_physical_domains().exists():
                errors.setdefault("aci_aaep", []).append(
                    _(
                        "The ACI AAEP must share at least one bound ACI "
                        "domain with the ACI Endpoint Group."
                    )
                )

        # Encap VLAN IDs must stay unique and modes compatible across
        # all bindings sharing the AAEP
        self._validate_aaep_sibling_bindings(errors)

        if errors:
            raise ValidationError(errors)

    @property
    def parent_object(self) -> ACIAttachableAccessEntityProfile:
        """Return the parent object of the instance.

        Overrides the base's EPG default: the AAEP is the MIM containment
        parent of ``infraRsFuncToEpg``.
        """
        return self.aci_aaep

    def _pool_physical_domains(self):
        """Return Physical Domains shared by the Endpoint Group and the AAEP.

        Domains bound to both the Endpoint Group and the AAEP (each via
        their own domain bindings). Their VLAN Pools constrain the
        deployment's encapsulation, and sharing at least one is the
        F0467 precondition.
        """
        aci_physical_domain_model = apps.get_model(
            "netbox_aci_plugin", "ACIPhysicalDomain"
        )

        # Nothing to intersect until both sides of the binding are set.
        if not (self.aci_endpoint_group_id and self.aci_aaep_id):
            return aci_physical_domain_model.objects.none()

        aci_aaep_domain_binding_model = apps.get_model(
            "netbox_aci_plugin", "ACIAAEPDomainBinding"
        )

        # Physical domains the endpoint group is bound to.
        epg_domain_ids = ACIEndpointGroupDomainBinding.objects.filter(
            _aci_endpoint_group_id=self.aci_endpoint_group_id,
            _aci_physical_domain__isnull=False,
        ).values_list("_aci_physical_domain_id", flat=True)

        # Physical domains the AAEP is bound to.
        aaep_domain_ids = aci_aaep_domain_binding_model.objects.filter(
            aci_aaep_id=self.aci_aaep_id,
            _aci_physical_domain__isnull=False,
        ).values_list("_aci_physical_domain_id", flat=True)

        # A deployment resolves through domains bound to both sides, so
        # intersect the two sets and prefetch each pool for clean().
        return aci_physical_domain_model.objects.filter(
            pk__in=set(epg_domain_ids) & set(aaep_domain_ids)
        ).select_related("aci_vlan_pool")

    def _validate_aaep_sibling_bindings(self, errors: dict) -> None:
        """Validate encap uniqueness and mode compatibility on the AAEP.

        Fetches only the sibling bindings on the same AAEP that can
        conflict with this instance: encap VLAN ID collisions on the
        main or primary slot (cross-slot included), an existing
        untagged binding, or a second native binding. An untagged
        binding must be the only binding on its AAEP, and at most one
        native binding is allowed per AAEP.
        """
        # An unset AAEP cannot conflict with an existing sibling
        # binding; defer to required-field validation.
        if not self.aci_aaep_id:
            return

        encap_vid = self.effective_encap_vlan_id
        primary_vid = self.effective_primary_encap_vlan_id
        vids = [vid for vid in (encap_vid, primary_vid) if vid is not None]

        siblings = ACIEndpointGroupAAEPBinding.objects.filter(
            aci_aaep_id=self.aci_aaep_id
        )
        # If updating an existing instance, exclude the current record.
        if self.pk:
            siblings = siblings.exclude(pk=self.pk)

        if self.mode == PortModeChoices.MODE_UNTAGGED:
            # An untagged binding conflicts with every sibling.
            conflicts = siblings
        else:
            # Let the database narrow the siblings to actual
            # conflicts: encap collisions on either slot, an existing
            # untagged binding and, for a native binding, a second
            # native one.
            conflict_q = models.Q(mode=PortModeChoices.MODE_UNTAGGED)
            if vids:
                conflict_q |= models.Q(encap_vlan_id__in=vids) | models.Q(
                    primary_encap_vlan_id__in=vids
                )
            if self.mode == PortModeChoices.MODE_NATIVE:
                conflict_q |= models.Q(mode=PortModeChoices.MODE_NATIVE)
            conflicts = siblings.filter(conflict_q)

        conflict_rows = conflicts.values_list(
            "aci_endpoint_group__name",
            "encap_vlan_id",
            "primary_encap_vlan_id",
            "mode",
        )

        conflicting_epgs = []
        untagged_epgs = []
        native_epg = None
        # Classify each conflicting sibling; encap collisions report
        # per slot, mode conflicts resolve after the loop.
        for epg_name, sib_encap, sib_primary, sib_mode in conflict_rows:
            conflicting_epgs.append(epg_name)
            for sib_vid in (sib_encap, sib_primary):
                if sib_vid is None:
                    continue
                if encap_vid is not None and encap_vid == sib_vid:
                    errors.setdefault("encap_vlan_id", []).append(
                        _(
                            "The encap VLAN ID {vid} is already used on "
                            "this ACI AAEP by ACI Endpoint Group {epg}."
                        ).format(vid=encap_vid, epg=epg_name)
                    )
                if primary_vid is not None and primary_vid == sib_vid:
                    errors.setdefault("primary_encap_vlan_id", []).append(
                        _(
                            "The primary encap VLAN ID {vid} is already "
                            "used on this ACI AAEP by ACI Endpoint "
                            "Group {epg}."
                        ).format(vid=primary_vid, epg=epg_name)
                    )
            if sib_mode == PortModeChoices.MODE_UNTAGGED:
                untagged_epgs.append(epg_name)
            elif sib_mode == PortModeChoices.MODE_NATIVE and native_epg is None:
                native_epg = epg_name

        # An untagged binding must be the only binding on its AAEP
        # (the hardware supports a single untagged VLAN per port and
        # no tagged EPGs beside it); at most one native binding is
        # allowed per AAEP.
        if self.mode == PortModeChoices.MODE_UNTAGGED and conflicting_epgs:
            errors.setdefault("mode", []).append(
                _(
                    "An 'untagged' mode binding must be the only ACI "
                    "Endpoint Group AAEP Binding on its ACI AAEP. This "
                    "ACI AAEP is already used by ACI Endpoint Group "
                    "{epgs}."
                ).format(epgs=", ".join(conflicting_epgs))
            )
        elif untagged_epgs:
            errors.setdefault("mode", []).append(
                _(
                    "The ACI AAEP already has an 'untagged' mode "
                    "binding for ACI Endpoint Group {epg}, which must "
                    "remain the only binding on its ACI AAEP."
                ).format(epg=untagged_epgs[0])
            )
        elif self.mode == PortModeChoices.MODE_NATIVE and native_epg:
            errors.setdefault("mode", []).append(
                _(
                    "Only one 'native' mode binding is allowed per ACI "
                    "AAEP. ACI Endpoint Group {epg} already uses "
                    "'native' mode on this ACI AAEP."
                ).format(epg=native_epg)
            )
