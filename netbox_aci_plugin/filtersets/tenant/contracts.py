# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant
from users.filterset_mixins import OwnerFilterMixin
from utilities.filters import ContentTypeFilter
from utilities.filtersets import register_filterset

from ...choices import (
    ContractRelationRoleChoices,
    ContractScopeChoices,
    ContractSubjectFilterActionChoices,
    ContractSubjectFilterApplyDirectionChoices,
    ContractSubjectFilterPriorityChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.contract_filters import ACIContractFilter
from ...models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ...models.tenant.endpoint_groups import ACIEndpointGroup
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF
from ..mixins import ACITenantFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACIContractFilterSet(
    ACITenantFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Contract model."""

    qos_class = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceClassChoices,
        null_value=None,
        label=_("QoS class"),
    )
    scope = django_filters.MultipleChoiceFilter(
        choices=ContractScopeChoices,
        null_value=None,
        label=_("Scope"),
    )
    target_dscp = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceDSCPChoices,
        null_value=None,
        label=_("Target DSCP"),
    )

    # Filters extended with a custom filter method
    present_in_aci_tenant_or_common_id = django_filters.ModelChoiceFilter(
        queryset=ACITenant.objects.all(),
        method="filter_present_in_aci_tenant_or_common_id",
        label=_("ACI Tenant (ID)"),
    )

    class Meta:
        model = ACIContract
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "qos_class",
            "scope",
            "target_dscp",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)

    @extend_schema_field(OpenApiTypes.INT)
    def filter_present_in_aci_tenant_or_common_id(self, queryset, name, aci_tenant):
        """Return a QuerySet filtered by given ACI Tenant or 'common'."""
        if aci_tenant is None:
            return queryset.none()
        return queryset.filter(
            Q(aci_tenant=aci_tenant)
            | Q(
                aci_tenant__name="common",
                aci_tenant__aci_fabric_id=aci_tenant.aci_fabric_id,
            )
        )


@register_filterset
class ACIContractRelationFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Contract Relation model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__aci_tenant__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__aci_tenant__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant of Contract (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant of Contract (ID)"),
    )
    aci_contract = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__name",
        queryset=ACIContract.objects.all(),
        to_field_name="name",
        label=_("ACI Contract (name)"),
    )
    aci_contract_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIContract.objects.all(),
        to_field_name="id",
        label=_("ACI Contract (ID)"),
    )
    nb_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__nb_tenant__slug",
        queryset=Tenant.objects.all(),
        to_field_name="slug",
        label=_("NetBox tenant (slug)"),
    )
    nb_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__nb_tenant",
        queryset=Tenant.objects.all(),
        to_field_name="id",
        label=_("NetBox tenant (ID)"),
    )
    aci_object_type = ContentTypeFilter(
        label=_("ACI Object Type"),
    )
    role = django_filters.MultipleChoiceFilter(
        choices=ContractRelationRoleChoices,
        null_value=None,
        label=_("Role"),
    )

    # Cached related objects filters
    aci_endpoint_group_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_endpoint_group__aci_app_profile__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant of Endpoint Group (name)"),
    )
    aci_endpoint_group_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_endpoint_group__aci_app_profile__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant of Endpoint Group (ID)"),
    )
    aci_endpoint_group = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_endpoint_group__name",
        queryset=ACIEndpointGroup.objects.all(),
        to_field_name="name",
        label=_("ACI Endpoint Group (name)"),
    )
    aci_endpoint_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_endpoint_group",
        queryset=ACIEndpointGroup.objects.all(),
        to_field_name="id",
        label=_("ACI Endpoint Group (ID)"),
    )
    aci_vrf_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_vrf__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant of VRF (name)"),
    )
    aci_vrf_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_vrf__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant of VRF (ID)"),
    )
    aci_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_vrf__name",
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        label=_("ACI VRF (name)"),
    )
    aci_vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_vrf",
        queryset=ACIVRF.objects.all(),
        to_field_name="id",
        label=_("ACI VRF (ID)"),
    )

    class Meta:
        model = ACIContractRelation
        fields: tuple = (
            "id",
            "aci_contract",
            "aci_object_type",
            "aci_object_id",
            "role",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's related object names."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(aci_contract__name__icontains=value)
            | Q(aci_endpoint_group__name__icontains=value)
            | Q(aci_vrf__name__icontains=value)
        )
        return queryset.filter(queryset_filter)


@register_filterset
class ACIContractSubjectFilterSet(
    NBTenantFilterSetMixin, OwnerFilterMixin, NetBoxModelFilterSet
):
    """Filter set for the ACI Contract Subject model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__aci_tenant__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__aci_tenant__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_contract = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract__name",
        queryset=ACIContract.objects.all(),
        to_field_name="name",
        label=_("ACI Contract (name)"),
    )
    aci_contract_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIContract.objects.all(),
        to_field_name="id",
        label=_("ACI Contract (ID)"),
    )
    qos_class = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceClassChoices,
        null_value=None,
        label=_("QoS class"),
    )
    qos_class_cons_to_prov = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceClassChoices,
        null_value=None,
        label=_("QoS class (consumer to provider)"),
    )
    qos_class_prov_to_cons = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceClassChoices,
        null_value=None,
        label=_("QoS class (provider to consumer)"),
    )
    target_dscp = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceDSCPChoices,
        null_value=None,
        label=_("Target DSCP"),
    )
    target_dscp_cons_to_prov = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceDSCPChoices,
        null_value=None,
        label=_("Target DSCP (consumer to provider)"),
    )
    target_dscp_prov_to_cons = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceDSCPChoices,
        null_value=None,
        label=_("Target DSCP (provider to consumer)"),
    )

    class Meta:
        model = ACIContractSubject
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_contract",
            "nb_tenant",
            "apply_both_directions_enabled",
            "qos_class",
            "qos_class_cons_to_prov",
            "qos_class_prov_to_cons",
            "reverse_filter_ports_enabled",
            "service_graph_name",
            "service_graph_name_cons_to_prov",
            "service_graph_name_prov_to_cons",
            "target_dscp",
            "target_dscp_cons_to_prov",
            "target_dscp_prov_to_cons",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
            | Q(aci_contract__name__icontains=value)
        )
        return queryset.filter(queryset_filter)


@register_filterset
class ACIContractSubjectFilterFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Contract Subject Filter model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_subject__aci_contract__aci_tenant__aci_fabric__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_subject__aci_contract__aci_tenant__aci_fabric",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_subject__aci_contract__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_subject__aci_contract__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_contract = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_subject__aci_contract__name",
        queryset=ACIContract.objects.all(),
        to_field_name="name",
        label=_("ACI Contract (name)"),
    )
    aci_contract_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_subject__aci_contract",
        queryset=ACIContract.objects.all(),
        to_field_name="id",
        label=_("ACI Contract (ID)"),
    )
    aci_contract_subject = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_subject__name",
        queryset=ACIContractSubject.objects.all(),
        to_field_name="name",
        label=_("ACI Contract Subject (name)"),
    )
    aci_contract_subject_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIContractSubject.objects.all(),
        to_field_name="id",
        label=_("ACI Contract Subject (ID)"),
    )
    aci_contract_filter = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_filter__name",
        queryset=ACIContractFilter.objects.all(),
        to_field_name="name",
        label=_("ACI Contract Filter (name)"),
    )
    aci_contract_filter_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIContractFilter.objects.all(),
        to_field_name="id",
        label=_("ACI Contract Filter (ID)"),
    )
    action = django_filters.MultipleChoiceFilter(
        choices=ContractSubjectFilterActionChoices,
        null_value=None,
        label=_("Action"),
    )
    apply_direction = django_filters.MultipleChoiceFilter(
        choices=ContractSubjectFilterApplyDirectionChoices,
        null_value=None,
        label=_("Apply direction"),
    )
    priority = django_filters.MultipleChoiceFilter(
        choices=ContractSubjectFilterPriorityChoices,
        null_value=None,
        label=_("(Deny) Priority"),
    )

    class Meta:
        model = ACIContractSubjectFilter
        fields: tuple = (
            "id",
            "aci_contract_filter",
            "aci_contract_subject",
            "action",
            "apply_direction",
            "log_enabled",
            "policy_compression_enabled",
            "priority",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(aci_contract_filter__name__icontains=value)
            | Q(aci_contract_subject__name__icontains=value)
            | Q(aci_contract_subject__aci_contract__name__icontains=value)
        )
        return queryset.filter(queryset_filter)
