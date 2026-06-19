# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Forms for tenant L3Out models."""

from django import forms
from django.utils.translation import gettext_lazy as _

from ipam.formfields import IPNetworkFormField
from ipam.models import VRF, Prefix
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant, TenantGroup
from users.models import Owner, OwnerGroup
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import (
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ...choices import QualityOfServiceClassChoices, QualityOfServiceDSCPChoices
from ...constants import ACI_DESC_MAX_LEN, ACI_NAME_MAX_LEN
from ...models.access_policies.domains import ACIRoutedDomain
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF


class ACIL3OutEditForm(NetBoxModelForm):
    """NetBox edit form for the ACIL3Out model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_tenants": "$aci_tenant"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI Tenant"),
    )
    aci_vrf = DynamicModelChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
        },
        label=_("ACI VRF"),
    )
    aci_routed_domain = DynamicModelChoiceField(
        queryset=ACIRoutedDomain.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
        },
        label=_("ACI Routed Domain"),
    )
    target_dscp = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        initial=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        label=_("Target DSCP"),
    )
    import_route_control_enforcement_enabled = forms.BooleanField(
        required=False,
        label=_("Import route control enforcement enabled"),
        help_text=_(
            "Enables import route control enforcement for the L3Out. "
            "Default is disabled."
        ),
    )
    export_route_control_enforcement_enabled = forms.BooleanField(
        required=False,
        disabled=True,
        initial=True,
        label=_("Export route control enforcement enabled"),
        help_text=_(
            "Export route control enforcement is always enabled for APIC "
            "L3Outs and cannot be disabled."
        ),
    )
    bgp_enabled = forms.BooleanField(
        required=False,
        label=_("BGP enabled"),
        help_text=_("Whether BGP is enabled for this L3Out. Default is disabled."),
    )
    ospf_enabled = forms.BooleanField(
        required=False,
        label=_("OSPF enabled"),
        help_text=_("Whether OSPF is enabled for this L3Out. Default is disabled."),
    )
    eigrp_enabled = forms.BooleanField(
        required=False,
        label=_("EIGRP enabled"),
        help_text=_("Whether EIGRP is enabled for this L3Out. Default is disabled."),
    )
    l3_multicast_ipv4_enabled = forms.BooleanField(
        required=False,
        label=_("L3 multicast IPv4 enabled"),
        help_text=_(
            "Whether IPv4 Layer 3 multicast is enabled for this L3Out. "
            "Default is disabled."
        ),
    )
    l3_multicast_ipv6_enabled = forms.BooleanField(
        required=False,
        label=_("L3 multicast IPv6 enabled"),
        help_text=_(
            "Whether IPv6 Layer 3 multicast is enabled for this L3Out. "
            "Default is disabled."
        ),
    )
    multipod_enabled = forms.BooleanField(
        required=False,
        label=_("Multi-Pod enabled"),
        help_text=_(
            "Designates this infra Tenant L3Out as used for ACI Multi-Pod. "
            "NetBox-side marker only; not pushed to APIC. Default is disabled."
        ),
    )
    custom_qos_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Custom QoS policy name"),
        help_text=_(
            "Name of the custom QoS policy applied to traffic for this L3Out. "
            "Default is none."
        ),
    )
    bfd_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("BFD policy name"),
        help_text=_(
            "Name of the BFD multihop node policy applied to this L3Out. "
            "Default is none."
        ),
    )
    pim_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("PIM policy name"),
        help_text=_("Name of the PIM policy applied to this L3Out. Default is none."),
    )
    igmp_interface_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("IGMP interface policy name"),
        help_text=_(
            "Name of the IGMP interface policy applied to this L3Out. Default is none."
        ),
    )
    ospf_external_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("OSPF external policy name"),
        help_text=_(
            "Name of the OSPF external policy applied to this L3Out. Default is none."
        ),
    )
    eigrp_interface_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("EIGRP interface policy name"),
        help_text=_(
            "Name of the EIGRP interface policy applied to this L3Out. Default is none."
        ),
    )
    interleak_route_map_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Interleak route map name"),
        help_text=_(
            "Name of the interleak route map applied to this L3Out. Default is none."
        ),
    )
    ingress_data_plane_policing_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Ingress data plane policing policy name"),
        help_text=_(
            "Name of the ingress data plane policing policy applied to "
            "this L3Out. Default is none."
        ),
    )
    egress_data_plane_policing_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Egress data plane policing policy name"),
        help_text=_(
            "Name of the egress data plane policing policy applied to "
            "this L3Out. Default is none."
        ),
    )
    nb_tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        initial_params={"tenants": "$nb_tenant"},
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group"},
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group = DynamicModelChoiceField(
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option="None",
        initial_params={"members": "$owner"},
        label=_("Owner group"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        query_params={"group_id": "$owner_group"},
        label=_("Owner"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_fabric",
            "aci_tenant",
            "aci_vrf",
            "description",
            "tags",
            name=_("ACI L3Out"),
        ),
        FieldSet("aci_routed_domain", name=_("Routed Domain")),
        FieldSet(
            "target_dscp",
            "import_route_control_enforcement_enabled",
            "export_route_control_enforcement_enabled",
            name=_("Policy"),
        ),
        FieldSet(
            "bgp_enabled",
            "ospf_enabled",
            "eigrp_enabled",
            "l3_multicast_ipv4_enabled",
            "l3_multicast_ipv6_enabled",
            name=_("Protocols"),
        ),
        FieldSet(
            "multipod_enabled",
            name=_("Multi-Pod"),
        ),
        FieldSet(
            "custom_qos_policy_name",
            "bfd_policy_name",
            "pim_policy_name",
            "igmp_interface_policy_name",
            "ospf_external_policy_name",
            "eigrp_interface_policy_name",
            "interleak_route_map_name",
            "ingress_data_plane_policing_policy_name",
            "egress_data_plane_policing_policy_name",
            name=_("Policy references"),
        ),
        FieldSet("nb_tenant_group", "nb_tenant", name=_("NetBox Tenancy")),
    )

    class Meta:
        model = ACIL3Out
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "aci_routed_domain",
            "target_dscp",
            "import_route_control_enforcement_enabled",
            "export_route_control_enforcement_enabled",
            "bgp_enabled",
            "ospf_enabled",
            "eigrp_enabled",
            "l3_multicast_ipv4_enabled",
            "l3_multicast_ipv6_enabled",
            "multipod_enabled",
            "custom_qos_policy_name",
            "bfd_policy_name",
            "pim_policy_name",
            "igmp_interface_policy_name",
            "ospf_external_policy_name",
            "eigrp_interface_policy_name",
            "interleak_route_map_name",
            "ingress_data_plane_policing_policy_name",
            "egress_data_plane_policing_policy_name",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIL3OutBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACIL3Out model."""

    name_alias = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=ACI_DESC_MAX_LEN,
        required=False,
        label=_("Description"),
    )
    target_dscp = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    import_route_control_enforcement_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Import route control enforcement enabled"),
    )
    bgp_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("BGP enabled"),
    )
    ospf_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("OSPF enabled"),
    )
    eigrp_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("EIGRP enabled"),
    )
    l3_multicast_ipv4_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("L3 multicast IPv4 enabled"),
    )
    l3_multicast_ipv6_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("L3 multicast IPv6 enabled"),
    )
    multipod_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Multi-Pod enabled"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACIL3Out
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "description",
            name=_("ACI L3Out"),
        ),
        FieldSet(
            "target_dscp",
            "import_route_control_enforcement_enabled",
            "bgp_enabled",
            "ospf_enabled",
            "eigrp_enabled",
            "l3_multicast_ipv4_enabled",
            "l3_multicast_ipv6_enabled",
            name=_("Policy"),
        ),
        FieldSet(
            "multipod_enabled",
            name=_("Multi-Pod"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "owner",
        "comments",
    )


class ACIL3OutFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACIL3Out model."""

    model = ACIL3Out
    fieldsets: tuple = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "name",
            "name_alias",
            "description",
            "aci_fabric_id",
            "aci_tenant_id",
            "aci_vrf_id",
            name=_("Attributes"),
        ),
        FieldSet("aci_routed_domain_id", name=_("Routed Domain")),
        FieldSet(
            "target_dscp",
            "import_route_control_enforcement_enabled",
            name=_("Policy"),
        ),
        FieldSet(
            "bgp_enabled",
            "ospf_enabled",
            "eigrp_enabled",
            "l3_multicast_ipv4_enabled",
            "l3_multicast_ipv6_enabled",
            name=_("Protocols"),
        ),
        FieldSet(
            "multipod_enabled",
            name=_("Multi-Pod"),
        ),
        FieldSet("nb_tenant_group_id", "nb_tenant_id", name=_("NetBox Tenancy")),
        FieldSet("owner_group_id", "owner_id", name=_("Ownership")),
    )
    name = forms.CharField(required=False)
    name_alias = forms.CharField(required=False)
    description = forms.CharField(required=False)
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric_id"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_vrf_id = DynamicModelMultipleChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant_id"},
        required=False,
        label=_("ACI VRF"),
    )
    aci_routed_domain_id = DynamicModelMultipleChoiceField(
        queryset=ACIRoutedDomain.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric_id"},
        required=False,
        label=_("ACI Routed Domain"),
    )
    target_dscp = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    import_route_control_enforcement_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Import route control enforcement enabled"),
    )
    bgp_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("BGP enabled"),
    )
    ospf_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("OSPF enabled"),
    )
    eigrp_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("EIGRP enabled"),
    )
    l3_multicast_ipv4_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("L3 multicast IPv4 enabled"),
    )
    l3_multicast_ipv6_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("L3 multicast IPv6 enabled"),
    )
    multipod_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Multi-Pod enabled"),
    )
    nb_tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group_id"},
        null_option="None",
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("Owner Group"),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group_id"},
        null_option="None",
        required=False,
        label=_("Owner"),
    )
    tag = TagFilterField(model)


class ACIL3OutImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACIL3Out model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
    )
    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
    )
    aci_vrf = CSVModelChoiceField(
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI VRF"),
    )
    aci_routed_domain = CSVModelChoiceField(
        queryset=ACIRoutedDomain.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Routed Domain"),
    )
    is_aci_vrf_in_common = forms.BooleanField(
        required=False,
        label=_("Is ACI VRF in 'common'"),
        help_text=_("Assigned ACI VRF is in ACI Tenant 'common'"),
    )
    target_dscp = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = CSVModelChoiceField(
        queryset=Owner.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Owner"),
    )

    class Meta:
        model = ACIL3Out
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_vrf",
            "is_aci_vrf_in_common",
            "aci_routed_domain",
            "target_dscp",
            "import_route_control_enforcement_enabled",
            "bgp_enabled",
            "ospf_enabled",
            "eigrp_enabled",
            "l3_multicast_ipv4_enabled",
            "l3_multicast_ipv6_enabled",
            "multipod_enabled",
            "custom_qos_policy_name",
            "bfd_policy_name",
            "pim_policy_name",
            "igmp_interface_policy_name",
            "ospf_external_policy_name",
            "eigrp_interface_policy_name",
            "interleak_route_map_name",
            "ingress_data_plane_policing_policy_name",
            "egress_data_plane_policing_policy_name",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)
        if not data:
            return
        if data.get("aci_fabric"):
            if data.get("aci_tenant"):
                self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
                    aci_fabric__name=data["aci_fabric"]
                )
                if data.get("is_aci_vrf_in_common") == "true":
                    self.fields["aci_vrf"].queryset = ACIVRF.objects.filter(
                        aci_tenant__aci_fabric__name=data["aci_fabric"],
                        aci_tenant__name="common",
                    )
                else:
                    self.fields["aci_vrf"].queryset = ACIVRF.objects.filter(
                        aci_tenant__aci_fabric__name=data["aci_fabric"],
                        aci_tenant__name=data["aci_tenant"],
                    )
            if data.get("aci_routed_domain"):
                self.fields[
                    "aci_routed_domain"
                ].queryset = ACIRoutedDomain.objects.filter(
                    aci_fabric__name=data["aci_fabric"]
                )


class ACIExternalEndpointGroupEditForm(NetBoxModelForm):
    """NetBox edit form for the ACIExternalEndpointGroup model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_tenants__aci_l3outs": "$aci_l3out"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={"aci_l3outs": "$aci_l3out"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_vrf = DynamicModelChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
        initial_params={"aci_l3outs": "$aci_l3out"},
        required=False,
        label=_("ACI VRF"),
    )
    aci_l3out = DynamicModelChoiceField(
        queryset=ACIL3Out.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant", "aci_vrf_id": "$aci_vrf"},
        label=_("ACI L3Out"),
    )
    target_dscp = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        initial=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        label=_("Target DSCP"),
    )
    qos_class = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        initial=QualityOfServiceClassChoices.CLASS_UNSPECIFIED,
        label=_("QoS class"),
    )
    preferred_group_member_enabled = forms.BooleanField(
        required=False,
        label=_("Preferred group member enabled"),
        help_text=_(
            "Whether this External EPG is a member of the preferred group. "
            "Default is disabled."
        ),
    )
    nb_tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        initial_params={"tenants": "$nb_tenant"},
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group"},
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group = DynamicModelChoiceField(
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option="None",
        initial_params={"members": "$owner"},
        label=_("Owner group"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group"},
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_fabric",
            "aci_tenant",
            "aci_vrf",
            "aci_l3out",
            "description",
            "tags",
            name=_("ACI External EPG"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "target_dscp",
            "qos_class",
            name=_("Policy"),
        ),
        FieldSet("nb_tenant_group", "nb_tenant", name=_("NetBox Tenancy")),
    )

    class Meta:
        model = ACIExternalEndpointGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_l3out",
            "preferred_group_member_enabled",
            "target_dscp",
            "qos_class",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIExternalEndpointGroupBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACIExternalEndpointGroup model."""

    name_alias = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=ACI_DESC_MAX_LEN,
        required=False,
        label=_("Description"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Preferred group member enabled"),
    )
    target_dscp = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    qos_class = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACIExternalEndpointGroup
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "description",
            "preferred_group_member_enabled",
            "target_dscp",
            "qos_class",
            name=_("ACI External EPG"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "owner",
        "comments",
    )


class ACIExternalEndpointGroupFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACIExternalEndpointGroup model."""

    model = ACIExternalEndpointGroup
    fieldsets: tuple = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "name",
            "name_alias",
            "description",
            "aci_fabric_id",
            "aci_tenant_id",
            "aci_vrf_id",
            "aci_l3out_id",
            name=_("Attributes"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "target_dscp",
            "qos_class",
            name=_("Policy"),
        ),
        FieldSet("nb_tenant_group_id", "nb_tenant_id", name=_("NetBox Tenancy")),
        FieldSet("owner_group_id", "owner_id", name=_("Ownership")),
    )
    name = forms.CharField(required=False)
    name_alias = forms.CharField(required=False)
    description = forms.CharField(required=False)
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric_id"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_vrf_id = DynamicModelMultipleChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant_id"},
        required=False,
        label=_("ACI VRF"),
    )
    aci_l3out_id = DynamicModelMultipleChoiceField(
        queryset=ACIL3Out.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id", "aci_vrf_id": "$aci_vrf_id"},
        required=False,
        label=_("ACI L3Out"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Preferred group member enabled"),
    )
    target_dscp = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    qos_class = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    nb_tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group_id"},
        null_option="None",
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("Owner Group"),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group_id"},
        null_option="None",
        required=False,
        label=_("Owner"),
    )
    tag = TagFilterField(model)


class ACIExternalEndpointGroupImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACIExternalEndpointGroup model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
    )
    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
    )
    aci_l3out = CSVModelChoiceField(
        queryset=ACIL3Out.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI L3Out"),
    )
    is_aci_l3out_in_common = forms.BooleanField(
        required=False,
        label=_("Is ACI L3Out in 'common'"),
        help_text=_("Assigned ACI L3Out is in ACI Tenant 'common'"),
    )
    target_dscp = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP"),
    )
    qos_class = CSVChoiceField(
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = CSVModelChoiceField(
        queryset=Owner.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Owner"),
    )

    class Meta:
        model = ACIExternalEndpointGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_l3out",
            "is_aci_l3out_in_common",
            "preferred_group_member_enabled",
            "target_dscp",
            "qos_class",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)
        if not data:
            return
        if data.get("aci_fabric") and data.get("aci_tenant"):
            self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            if data.get("is_aci_l3out_in_common") == "true":
                self.fields["aci_l3out"].queryset = ACIL3Out.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name="common",
                )
            else:
                self.fields["aci_l3out"].queryset = ACIL3Out.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name=data["aci_tenant"],
                )


class ACIExternalSubnetEditForm(NetBoxModelForm):
    """NetBox edit form for the ACIExternalSubnet model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_tenants__aci_l3outs__aci_external_endpoint_groups": (
                "$aci_external_endpoint_group"
            )
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={
            "aci_l3outs__aci_external_endpoint_groups": "$aci_external_endpoint_group"
        },
        required=False,
        label=_("ACI Tenant"),
    )
    aci_l3out = DynamicModelChoiceField(
        queryset=ACIL3Out.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        initial_params={"aci_external_endpoint_groups": "$aci_external_endpoint_group"},
        required=False,
        label=_("ACI L3Out"),
    )
    aci_external_endpoint_group = DynamicModelChoiceField(
        queryset=ACIExternalEndpointGroup.objects.all(),
        query_params={"aci_l3out_id": "$aci_l3out"},
        label=_("ACI External Endpoint Group"),
    )
    matched_prefix = IPNetworkFormField(
        required=False,
        label=_("Matched prefix"),
        help_text=_(
            "IPv4 or IPv6 prefix matched by this external subnet. "
            "Required when no NetBox prefix is selected."
        ),
    )
    import_route_control_enabled = forms.BooleanField(
        required=False,
        label=_("Import route control enabled"),
        help_text=_(
            "Classifies this external subnet for import route control. "
            "Default is disabled."
        ),
    )
    export_route_control_enabled = forms.BooleanField(
        required=False,
        label=_("Export route control enabled"),
        help_text=_(
            "Classifies this external subnet for export route control. "
            "Default is disabled."
        ),
    )
    shared_route_control_enabled = forms.BooleanField(
        required=False,
        label=_("Shared route control enabled"),
        help_text=_(
            "Classifies this external subnet for shared route control. "
            "Default is disabled."
        ),
    )
    import_security_enabled = forms.BooleanField(
        required=False,
        label=_("Import security enabled"),
        help_text=_(
            "Classifies this external subnet for security import. Default is enabled."
        ),
    )
    shared_security_enabled = forms.BooleanField(
        required=False,
        label=_("Shared security enabled"),
        help_text=_(
            "Classifies this external subnet for shared security import. "
            "Default is disabled."
        ),
    )
    aggregate_import_route_control_enabled = forms.BooleanField(
        required=False,
        label=_("Aggregate import route control enabled"),
        help_text=_(
            "Aggregates import route control prefixes for this external "
            "subnet. Default is disabled."
        ),
    )
    aggregate_export_route_control_enabled = forms.BooleanField(
        required=False,
        label=_("Aggregate export route control enabled"),
        help_text=_(
            "Aggregates export route control prefixes for this external "
            "subnet. Default is disabled."
        ),
    )
    aggregate_shared_route_control_enabled = forms.BooleanField(
        required=False,
        label=_("Aggregate shared route control enabled"),
        help_text=_(
            "Aggregates shared route control prefixes for this external "
            "subnet. Default is disabled."
        ),
    )
    bgp_route_summarization_enabled = forms.BooleanField(
        required=False,
        label=_("BGP route summarization enabled"),
        help_text=_(
            "Whether BGP route summarization is enabled for this external "
            "subnet. Default is disabled."
        ),
    )
    bgp_route_summarization_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("BGP route summarization policy name"),
        help_text=_(
            "Name of the BGP route summarization policy applied to this "
            "external subnet. Default is none."
        ),
    )
    ospf_route_summarization_enabled = forms.BooleanField(
        required=False,
        label=_("OSPF route summarization enabled"),
        help_text=_(
            "Whether OSPF route summarization is enabled for this external "
            "subnet. Default is disabled."
        ),
    )
    ospf_route_summarization_policy_name = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("OSPF route summarization policy name"),
        help_text=_(
            "Name of the OSPF route summarization policy applied to this "
            "external subnet. Default is none."
        ),
    )
    eigrp_route_summarization_enabled = forms.BooleanField(
        required=False,
        label=_("EIGRP route summarization enabled"),
        help_text=_(
            "Whether EIGRP route summarization is enabled for this external "
            "subnet. Default is disabled."
        ),
    )
    nb_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_("NetBox VRF"),
    )
    nb_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        query_params={"vrf_id": "$nb_vrf"},
        required=False,
        label=_("NetBox Prefix"),
        selector=True,
    )
    nb_tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        initial_params={"tenants": "$nb_tenant"},
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group"},
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group = DynamicModelChoiceField(
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option="None",
        initial_params={"members": "$owner"},
        label=_("Owner group"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group"},
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_fabric",
            "aci_tenant",
            "aci_l3out",
            "aci_external_endpoint_group",
            "description",
            "tags",
            name=_("ACI External Subnet"),
        ),
        FieldSet(
            "matched_prefix",
            "nb_vrf",
            "nb_prefix",
            name=_("Prefix"),
        ),
        FieldSet(
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_route_control_enabled",
            "import_security_enabled",
            "shared_security_enabled",
            name=_("Subnet scope"),
        ),
        FieldSet(
            "aggregate_import_route_control_enabled",
            "aggregate_export_route_control_enabled",
            "aggregate_shared_route_control_enabled",
            name=_("Aggregate scope"),
        ),
        FieldSet(
            "bgp_route_summarization_enabled",
            "bgp_route_summarization_policy_name",
            "ospf_route_summarization_enabled",
            "ospf_route_summarization_policy_name",
            "eigrp_route_summarization_enabled",
            name=_("Route summarization"),
        ),
        FieldSet("nb_tenant_group", "nb_tenant", name=_("NetBox Tenancy")),
    )

    class Meta:
        model = ACIExternalSubnet
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_external_endpoint_group",
            "matched_prefix",
            "nb_prefix",
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_route_control_enabled",
            "import_security_enabled",
            "shared_security_enabled",
            "aggregate_import_route_control_enabled",
            "aggregate_export_route_control_enabled",
            "aggregate_shared_route_control_enabled",
            "bgp_route_summarization_enabled",
            "bgp_route_summarization_policy_name",
            "ospf_route_summarization_enabled",
            "ospf_route_summarization_policy_name",
            "eigrp_route_summarization_enabled",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide the synced value so users aren't confused into thinking
        # they must manage matched_prefix manually when nb_prefix is set.
        if self.instance.pk and self.instance.nb_prefix_id:
            self.initial["matched_prefix"] = ""


class ACIExternalSubnetBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACIExternalSubnet model."""

    name_alias = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=ACI_DESC_MAX_LEN,
        required=False,
        label=_("Description"),
    )
    aci_external_endpoint_group = DynamicModelChoiceField(
        queryset=ACIExternalEndpointGroup.objects.all(),
        required=False,
        label=_("ACI External Endpoint Group"),
    )
    import_route_control_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Import route control enabled"),
    )
    export_route_control_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Export route control enabled"),
    )
    shared_route_control_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Shared route control enabled"),
    )
    import_security_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Import security enabled"),
    )
    shared_security_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Shared security enabled"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACIExternalSubnet
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "description",
            "aci_external_endpoint_group",
            name=_("ACI External Subnet"),
        ),
        FieldSet(
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_route_control_enabled",
            "import_security_enabled",
            "shared_security_enabled",
            name=_("Subnet scope"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "owner",
        "comments",
    )


class ACIExternalSubnetFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACIExternalSubnet model."""

    model = ACIExternalSubnet
    fieldsets: tuple = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "name",
            "name_alias",
            "description",
            "aci_fabric_id",
            "aci_tenant_id",
            "aci_vrf_id",
            "aci_l3out_id",
            "aci_external_endpoint_group_id",
            "matched_prefix_within_include",
            "nb_prefix_id",
            name=_("Attributes"),
        ),
        FieldSet(
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_route_control_enabled",
            "import_security_enabled",
            "shared_security_enabled",
            name=_("Subnet scope"),
        ),
        FieldSet("nb_tenant_group_id", "nb_tenant_id", name=_("NetBox Tenancy")),
        FieldSet("owner_group_id", "owner_id", name=_("Ownership")),
    )
    name = forms.CharField(required=False)
    name_alias = forms.CharField(required=False)
    description = forms.CharField(required=False)
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric_id"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_vrf_id = DynamicModelMultipleChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant_id"},
        required=False,
        label=_("ACI VRF"),
    )
    aci_l3out_id = DynamicModelMultipleChoiceField(
        queryset=ACIL3Out.objects.all(),
        query_params={
            "aci_tenant_id": "$aci_tenant_id",
            "aci_vrf_id": "$aci_vrf_id",
        },
        required=False,
        label=_("ACI L3Out"),
    )
    aci_external_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIExternalEndpointGroup.objects.all(),
        query_params={"aci_l3out_id": "$aci_l3out_id"},
        required=False,
        label=_("ACI External Endpoint Group"),
    )
    matched_prefix_within_include = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Prefix",
            }
        ),
        label=_("Matched Prefix within"),
    )
    nb_prefix_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("NetBox Prefix"),
    )
    import_route_control_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Import route control enabled"),
    )
    export_route_control_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Export route control enabled"),
    )
    shared_route_control_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Shared route control enabled"),
    )
    import_security_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Import security enabled"),
    )
    shared_security_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Shared security enabled"),
    )
    nb_tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group_id"},
        null_option="None",
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("Owner Group"),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group_id"},
        null_option="None",
        required=False,
        label=_("Owner"),
    )
    tag = TagFilterField(model)


class ACIExternalSubnetImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACIExternalSubnet model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
    )
    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
    )
    aci_l3out = CSVModelChoiceField(
        queryset=ACIL3Out.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI L3Out"),
    )
    is_aci_l3out_in_common = forms.BooleanField(
        required=False,
        label=_("Is ACI L3Out in 'common'"),
        help_text=_("Assigned ACI L3Out is in ACI Tenant 'common'"),
    )
    aci_external_endpoint_group = CSVModelChoiceField(
        queryset=ACIExternalEndpointGroup.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI External Endpoint Group"),
    )
    matched_prefix = IPNetworkFormField(
        required=False,
        label=_("Matched prefix"),
        help_text=_(
            "IPv4 or IPv6 prefix matched by this external subnet. "
            "Required when no NetBox prefix is selected."
        ),
    )
    nb_vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox VRF"),
        help_text=_("VRF to which the NetBox Prefix belongs"),
    )
    nb_prefix = CSVModelChoiceField(
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        required=False,
        label=_("NetBox Prefix"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = CSVModelChoiceField(
        queryset=Owner.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Owner"),
    )

    class Meta:
        model = ACIExternalSubnet
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_l3out",
            "is_aci_l3out_in_common",
            "aci_external_endpoint_group",
            "matched_prefix",
            "nb_prefix",
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_route_control_enabled",
            "import_security_enabled",
            "shared_security_enabled",
            "aggregate_import_route_control_enabled",
            "aggregate_export_route_control_enabled",
            "aggregate_shared_route_control_enabled",
            "bgp_route_summarization_enabled",
            "bgp_route_summarization_policy_name",
            "ospf_route_summarization_enabled",
            "ospf_route_summarization_policy_name",
            "eigrp_route_summarization_enabled",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)
        if not data:
            return
        if data.get("aci_fabric") and data.get("aci_tenant"):
            self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            if data.get("is_aci_l3out_in_common") == "true":
                self.fields["aci_l3out"].queryset = ACIL3Out.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name="common",
                )
            else:
                self.fields["aci_l3out"].queryset = ACIL3Out.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name=data["aci_tenant"],
                )
        if data.get("aci_l3out"):
            epg_params = {"aci_l3out__name": data["aci_l3out"]}
            if data.get("aci_fabric"):
                epg_params["aci_l3out__aci_tenant__aci_fabric__name"] = data[
                    "aci_fabric"
                ]
            if data.get("aci_tenant"):
                if data.get("is_aci_l3out_in_common") == "true":
                    epg_params["aci_l3out__aci_tenant__name"] = "common"
                else:
                    epg_params["aci_l3out__aci_tenant__name"] = data["aci_tenant"]
            self.fields[
                "aci_external_endpoint_group"
            ].queryset = ACIExternalEndpointGroup.objects.filter(**epg_params)
        if data.get("nb_prefix") and data.get("nb_vrf"):
            self.fields["nb_prefix"].queryset = Prefix.objects.filter(
                vrf__name=data["nb_vrf"]
            )
