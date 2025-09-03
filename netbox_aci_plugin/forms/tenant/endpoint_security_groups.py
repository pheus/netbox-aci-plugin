# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from ipam.models import VRF, IPAddress, Prefix
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    BOOLEAN_WITH_BLANK_CHOICES,
    get_field_value,
)
from utilities.forms.fields import (
    CommentField,
    ContentTypeChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle

from ...constants import (
    ESG_ENDPOINT_GROUP_SELECTORS_MODELS,
    ESG_ENDPOINT_SELECTORS_MODELS,
)
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
)
from ...models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

#
# Endpoint Security Group forms
#


class ACIEndpointSecurityGroupEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Endpoint Security Group model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={"aci_app_profiles": "$aci_app_profile"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        label=_("ACI Application Profile"),
    )
    aci_vrf = DynamicModelChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
        label=_("ACI VRF"),
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
    admin_shutdown = forms.BooleanField(
        required=False,
        label=_("Admin state shutdown"),
        help_text=_(
            "Whether the ESG is in shutdown mode removing all policy "
            "configuration from all switches. Default is disabled."
        ),
    )
    intra_esg_isolation_enabled = forms.BooleanField(
        required=False,
        label=_("Intra-ESG isolation enabled"),
        help_text=_(
            "Prevents communication between endpoints in an ESG when "
            "enabled. Default is disabled."
        ),
    )
    preferred_group_member_enabled = forms.BooleanField(
        required=False,
        label=_("Preferred Group member enabled"),
        help_text=_(
            "Whether this ESG is a member of the preferred group and allows "
            "communication without contracts. Default is disabled."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_vrf",
            "description",
            "tags",
            "admin_shutdown",
            name=_("ACI Endpoint Security Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_esg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "name",
            "name_alias",
            "aci_app_profile",
            "aci_vrf",
            "description",
            "nb_tenant",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
            "comments",
            "tags",
        )

    def clean(self):
        """Clean and validate the ACI Endpoint Security Group form."""
        super().clean()

        aci_app_profile = self.cleaned_data.get("aci_app_profile")
        aci_vrf = self.cleaned_data.get("aci_vrf")

        # Ensure aci_app_profile and aci_vrf are present before validating
        if aci_app_profile and aci_vrf:
            # Check if the ACI Tenant IDs mismatch
            aci_tenant_mismatch = aci_app_profile.aci_tenant.id != aci_vrf.aci_tenant.id
            # Check if the ACI VRF Tenant name is not 'common'
            not_aci_tenant_common = aci_vrf.aci_tenant.name != "common"
            # Raise the validation error if both conditions are met
            if aci_tenant_mismatch and not_aci_tenant_common:
                self.add_error(
                    "aci_vrf",
                    _(
                        "A VRF can only be assigned belonging to same"
                        "ACI Tenant as the Application Profile or to the "
                        "special ACI Tenant 'common'."
                    ),
                )


class ACIEndpointSecurityGroupBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Endpoint Security Group model."""

    name_alias = forms.CharField(
        max_length=64,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=128,
        required=False,
        label=_("Description"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_vrf = DynamicModelChoiceField(
        queryset=ACIVRF.objects.all(),
        required=False,
        label=_("ACI VRF"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    admin_shutdown = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Admin shutdown"),
    )
    intra_esg_isolation_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Intra-ESG isolation enabled"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Preferred group member enabled"),
    )
    comments = CommentField()

    model = ACIEndpointSecurityGroup
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_app_profile",
            "aci_vrf",
            "description",
            "tags",
            "admin_shutdown",
            name=_("ACI Endpoint Security Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_epg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )


class ACIEndpointSecurityGroupFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Endpoint Security Group model."""

    model = ACIEndpointSecurityGroup
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant_id",
            "aci_app_profile_id",
            "aci_vrf_id",
            "description",
            "admin_shutdown",
            name="Attributes",
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_esg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "nb_tenant_group_id",
            "nb_tenant_id",
            name="NetBox Tenancy",
        ),
    )

    name = forms.CharField(
        required=False,
    )
    name_alias = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        null_option="None",
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        null_option="None",
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_vrf_id = DynamicModelMultipleChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        null_option="None",
        required=False,
        label=_("ACI VRF"),
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
    admin_shutdown = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Admin shutdown"),
    )
    intra_esg_isolation_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Intra-ESG isolation enabled"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Preferred group member enabled"),
    )
    tag = TagFilterField(model)


class ACIEndpointSecurityGroupImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Endpoint Security Group model."""

    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Parent ACI Tenant of ACI Application Profile"),
    )
    aci_app_profile = CSVModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Application Profile"),
        help_text=_("Assigned ACI Application Profile"),
    )
    aci_vrf = CSVModelChoiceField(
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI VRF"),
        help_text=_("Assigned ACI VRF"),
    )
    is_aci_vrf_in_common = forms.BooleanField(
        label=_("Is ACI VRF in 'common'"),
        required=False,
        help_text=_("Assigned ACI VRF is in ACI Tenant 'common'"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )

    class Meta:
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_vrf",
            "description",
            "nb_tenant",
            "is_aci_vrf_in_common",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIEndpointSecurityGroup queryset by parent ACIAppProfile
        # and ACITenant
        if data.get("aci_tenant") and data.get("aci_app_profile"):
            # Limit ACIAppProfile queryset by parent ACITenant
            aci_appprofile_queryset = ACIAppProfile.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_app_profile"].queryset = aci_appprofile_queryset

        # Limit ACIVRF queryset by "common" ACITenant
        if data.get("is_aci_vrf_in_common") == "true":
            aci_vrf_queryset = ACIVRF.objects.filter(aci_tenant__name="common")
            self.fields["aci_vrf"].queryset = aci_vrf_queryset
        # Limit ACIVRF queryset by ACITenant
        elif data.get("aci_tenant") and data.get("aci_vrf"):
            # Limit ACIVRF queryset by parent ACITenant
            aci_vrf_queryset = ACIVRF.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_vrf"].queryset = aci_vrf_queryset


#
# ESG Endpoint Group (EPG) Selector forms
#


class ACIEsgEndpointGroupSelectorEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI ESG Endpoint Group (EPG) Selector model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={
            "aci_app_profiles__aci_endpoint_security_groups": (
                "$aci_endpoint_security_group"
            )
        },
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        initial_params={"aci_endpoint_security_groups": "$aci_endpoint_security_group"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group = DynamicModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_app_profile",
        },
        label=_("ACI Endpoint Security Group"),
    )
    aci_epg_object_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Application Profile of Endpoint Group"),
    )
    aci_epg_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_GROUP_SELECTORS_MODELS),
        widget=HTMXSelect(),
        label=_("ACI EPG Object Type"),
    )
    aci_epg_object = DynamicModelChoiceField(
        queryset=ACIEndpointGroup.objects.none(),  # Initial queryset
        query_params={
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_epg_object_app_profile",
            "shares_aci_vrf_with_aci_esg_id": "$aci_endpoint_security_group",
        },
        selector=True,
        label=_("ACI EPG Object"),
        disabled=True,
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
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            "tags",
            name=_("ACI ESG Endpoint Group (EPG) Selector"),
        ),
        FieldSet(
            "aci_epg_object_app_profile",
            "aci_epg_object_type",
            "aci_epg_object",
            name=_("Endpoint Group Assignment"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIEsgEndpointGroupSelector
        fields: tuple = (
            "name",
            "name_alias",
            "aci_endpoint_security_group",
            "aci_epg_object_type",
            "description",
            "nb_tenant",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI ESG Endpoint Group Selector form."""
        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.aci_epg_object:
            # Initialize the Endpoint Group object field
            initial["aci_epg_object"] = instance.aci_epg_object

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if aci_epg_object_type_id := get_field_value(self, "aci_epg_object_type"):
            try:
                # Retrieve the ContentType model class based on the
                # Endpoint Group object type
                aci_epg_object_type = ContentType.objects.get(pk=aci_epg_object_type_id)
                aci_epg_model = aci_epg_object_type.model_class()

                # Configure the queryset and label for the aci_epg_object field
                self.fields["aci_epg_object"].queryset = aci_epg_model.objects.all()
                self.fields["aci_epg_object"].widget.attrs["selector"] = (
                    aci_epg_model._meta.label_lower
                )
                self.fields["aci_epg_object"].disabled = False
                self.fields["aci_epg_object"].label = _(
                    bettertitle(aci_epg_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:
                pass

            # Clears the aci_epg_object field if the selected type changes
            if (
                self.instance
                and self.instance.pk
                and aci_epg_object_type_id != self.instance.aci_epg_object_type_id
            ):
                self.initial["aci_epg_object"] = None

    def clean(self):
        """Validate fields for the ACI ESG Endpoint Group Selector form."""
        super().clean()

        # Ensure the selected Endpoint Group object gets assigned
        self.instance.aci_epg_object = self.cleaned_data.get("aci_epg_object")


class ACIEsgEndpointGroupSelectorBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI ESG EPG Selector model."""

    name_alias = forms.CharField(
        max_length=64,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=128,
        required=False,
        label=_("Description"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group = DynamicModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_app_profile",
        },
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    aci_epg_object_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Application Profile of Endpoint Group"),
    )
    aci_epg_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_GROUP_SELECTORS_MODELS),
        required=False,
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        label=_("ACI EPG Object Type"),
    )
    aci_epg_object = DynamicModelChoiceField(
        queryset=ACIEndpointGroup.objects.none(),  # Initial queryset
        query_params={
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_epg_object_app_profile",
        },
        selector=True,
        required=False,
        label=_("ACI EPG Object"),
        disabled=True,
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    comments = CommentField()

    model = ACIEsgEndpointGroupSelector
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            "tags",
            name=_("ACI ESG Endpoint Group (EPG) Selector"),
        ),
        FieldSet(
            "aci_epg_object_app_profile",
            "aci_epg_object_type",
            "aci_epg_object",
            name=_("Endpoint Group Assignment"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI ESG Endpoint Group Selector bulk edit form."""
        super().__init__(*args, **kwargs)

        if aci_epg_object_type_id := get_field_value(self, "aci_epg_object_type"):
            try:
                # Retrieve the ContentType model class based on the
                # Endpoint Group object type
                aci_epg_object_type = ContentType.objects.get(pk=aci_epg_object_type_id)
                aci_epg_model = aci_epg_object_type.model_class()

                # Configure the queryset and label for the aci_epg_object field
                self.fields["aci_epg_object"].queryset = aci_epg_model.objects.all()
                self.fields["aci_epg_object"].widget.attrs["selector"] = (
                    aci_epg_model._meta.label_lower
                )
                self.fields["aci_epg_object"].disabled = False
                self.fields["aci_epg_object"].label = _(
                    bettertitle(aci_epg_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:
                pass


class ACIEsgEndpointGroupSelectorFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI ESG Endpoint Group Selector model."""

    model = ACIEsgEndpointGroupSelector
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant_id",
            "aci_app_profile_id",
            "aci_endpoint_security_group_id",
            "description",
            "tags",
            name=_("ACI ESG Endpoint Group (EPG) Selector"),
        ),
        FieldSet(
            "aci_endpoint_group_app_profile_id",
            "aci_endpoint_group_id",
            name=_("Endpoint Group Assignment"),
        ),
        FieldSet(
            "aci_useg_endpoint_group_app_profile_id",
            "aci_useg_endpoint_group_id",
            name=_("uSeg Endpoint Group Assignment"),
        ),
        FieldSet(
            "nb_tenant_group_id",
            "nb_tenant_id",
            name=_("NetBox Tenancy"),
        ),
    )

    name = forms.CharField(
        required=False,
    )
    name_alias = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        null_option="None",
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        null_option="None",
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={"aci_app_profile_id": "$aci_app_profile_id"},
        null_option="None",
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    aci_endpoint_group_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile of Endpoint Group"),
    )
    aci_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointGroup.objects.all(),
        required=False,
        label=_("ACI Endpoint Group"),
    )
    aci_useg_endpoint_group_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile of uSeg Endpoint Group"),
    )
    aci_useg_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIUSegEndpointGroup.objects.all(),
        required=False,
        label=_("ACI uSeg Endpoint Group"),
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
    tag = TagFilterField(model)


class ACIEsgEndpointGroupSelectorImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI ESG EPG Selector model."""

    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Parent ACI Tenant of ACI Application Profile"),
    )
    aci_app_profile = CSVModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Application Profile"),
        help_text=_("Parent ACI Application Profile of ACI Endpoint Security Group"),
    )
    aci_endpoint_security_group = CSVModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Endpoint Security Group"),
        help_text=_("Assigned ACI Endpoint Security Group"),
    )
    aci_epg_object_id = forms.IntegerField(
        required=True,
        label=_("ACI Endpoint Group Object ID"),
    )
    aci_epg_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_GROUP_SELECTORS_MODELS),
        required=True,
        label=_("ACI Endpoint Group Object Type (app & model)"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )

    class Meta:
        model = ACIEsgEndpointGroupSelector
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            "nb_tenant",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIEndpointSecurityGroup queryset by parent ACI objects
        if data.get("aci_tenant") and data.get("aci_app_profile"):
            # Limit ACIAppProfile queryset by parent ACITenant
            aci_appprofile_queryset = ACIAppProfile.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_app_profile"].queryset = aci_appprofile_queryset
            # Limit ACIEndpointSecurityGroup queryset by parent ACIAppProfile
            aci_endpoint_security_group_queryset = (
                ACIEndpointSecurityGroup.objects.filter(
                    aci_app_profile__name=data["aci_app_profile"]
                )
            )
            self.fields[
                "aci_endpoint_security_group"
            ].queryset = aci_endpoint_security_group_queryset


#
# ESG Endpoint Selector forms
#


class ACIEsgEndpointSelectorEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI ESG Endpoint Selector model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={
            "aci_app_profiles__aci_endpoint_security_groups": (
                "$aci_endpoint_security_group"
            )
        },
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        initial_params={"aci_endpoint_security_groups": "$aci_endpoint_security_group"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group = DynamicModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={"aci_app_profile_id": "$aci_app_profile"},
        label=_("ACI Endpoint Security Group"),
    )
    ep_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_SELECTORS_MODELS),
        widget=HTMXSelect(),
        label=_("Endpoint Object Type"),
    )
    ep_object = DynamicModelChoiceField(
        queryset=IPAddress.objects.none(),  # Initial queryset
        selector=True,
        label=_("Endpoint Object"),
        disabled=True,
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
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            "tags",
            name=_("ACI ESG Endpoint Selector"),
        ),
        FieldSet(
            "ep_object_type",
            "ep_object",
            name=_("Endpoint Assignment"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIEsgEndpointSelector
        fields: tuple = (
            "name",
            "name_alias",
            "aci_endpoint_security_group",
            "ep_object_type",
            "description",
            "nb_tenant",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI ESG Endpoint Selector form."""
        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.ep_object:
            # Initialize the Endpoint object field
            initial["ep_object"] = instance.ep_object

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if ep_object_type_id := get_field_value(self, "ep_object_type"):
            try:
                # Retrieve the ContentType model class based on the Endpoint
                # object type
                ep_object_type = ContentType.objects.get(pk=ep_object_type_id)
                ep_model = ep_object_type.model_class()

                # Configure the queryset and label for the ep_object field
                self.fields["ep_object"].queryset = ep_model.objects.all()
                self.fields["ep_object"].widget.attrs["selector"] = (
                    ep_model._meta.label_lower
                )
                self.fields["ep_object"].disabled = False
                self.fields["ep_object"].label = _(
                    bettertitle(ep_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:
                pass

            # Clears the ep_object field if the selected type changes
            if (
                self.instance
                and self.instance.pk
                and ep_object_type_id != self.instance.ep_object_type_id
            ):
                self.initial["ep_object"] = None

    def clean(self):
        """Validate form fields for the ACI ESG Endpoint Selector form."""
        super().clean()

        # Ensure the selected Endpoint object gets assigned
        self.instance.ep_object = self.cleaned_data.get("ep_object")


class ACIEsgEndpointSelectorBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI ESG Endpoint Selector model."""

    name_alias = forms.CharField(
        max_length=64,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=128,
        required=False,
        label=_("Description"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group = DynamicModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={"aci_app_profile_id": "$aci_app_profile"},
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    ep_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_SELECTORS_MODELS),
        required=False,
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        label=_("Endpoint Object Type"),
    )
    ep_object = DynamicModelChoiceField(
        queryset=IPAddress.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Endpoint Object"),
        disabled=True,
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    comments = CommentField()

    model = ACIEsgEndpointSelector
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            "tags",
            name=_("ACI ESG Endpoint Selector"),
        ),
        FieldSet(
            "ep_object_type",
            "ep_object",
            name=_("Endpoint Assignment"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI ESG Endpoint Selector bulk edit form."""
        super().__init__(*args, **kwargs)

        if ep_object_type_id := get_field_value(self, "ep_object_type"):
            try:
                # Retrieve the ContentType model class based on the Endpoint
                # object type
                ep_object_type = ContentType.objects.get(pk=ep_object_type_id)
                ep_model = ep_object_type.model_class()

                # Configure the queryset and label for the ep_object field
                self.fields["ep_object"].queryset = ep_model.objects.all()
                self.fields["ep_object"].widget.attrs["selector"] = (
                    ep_model._meta.label_lower
                )
                self.fields["ep_object"].disabled = False
                self.fields["ep_object"].label = _(
                    bettertitle(ep_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:
                pass


class ACIEsgEndpointSelectorFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI ESG Endpoint Selector model."""

    model = ACIEsgEndpointSelector
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant_id",
            "aci_app_profile_id",
            "aci_endpoint_security_group_id",
            "description",
            "tags",
            name=_("ACI ESG Endpoint Selector"),
        ),
        FieldSet(
            "ip_address_vrf_id",
            "ip_address_id",
            "prefix_vrf_id",
            "prefix_id",
            name=_("Endpoint Assignment"),
        ),
        FieldSet(
            "nb_tenant_group_id",
            "nb_tenant_id",
            name=_("NetBox Tenancy"),
        ),
    )

    name = forms.CharField(
        required=False,
    )
    name_alias = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        null_option="None",
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    ip_address_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        null_option="None",
        required=False,
        label=_("VRF of IP Address"),
    )
    ip_address_id = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        query_params={"vrf_id": "$ip_address_vrf_id"},
        null_option="None",
        required=False,
        label=_("IP Address"),
    )
    prefix_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        null_option="None",
        required=False,
        label=_("VRF of Prefix"),
    )
    prefix_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        query_params={"vrf_id": "$prefix_vrf_id"},
        null_option="None",
        required=False,
        label=_("Prefix"),
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
    tag = TagFilterField(model)


class ACIEsgEndpointSelectorImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI ESG Endpoint Selector model."""

    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Parent ACI Tenant of ACI Application Profile"),
    )
    aci_app_profile = CSVModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Application Profile"),
        help_text=_("Assigned ACI Application Profile"),
    )
    aci_endpoint_security_group = CSVModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Endpoint Security Group"),
        help_text=_("Assigned ACI Endpoint Security Group"),
    )
    ep_object_id = forms.IntegerField(
        required=True,
        label=_("Endpoint Object ID"),
    )
    ep_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_SELECTORS_MODELS),
        required=True,
        label=_("Endpoint Object Type (app & model)"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )

    class Meta:
        model = ACIEsgEndpointSelector
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            "nb_tenant",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIEndpointSecurityGroup queryset by parent ACI objects
        if data.get("aci_tenant") and data.get("aci_app_profile"):
            # Limit ACIAppProfile queryset by parent ACITenant
            aci_appprofile_queryset = ACIAppProfile.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_app_profile"].queryset = aci_appprofile_queryset
            # Limit ACIEndpointSecurityGroup queryset by parent ACIAppProfile
            aci_endpoint_security_group_queryset = (
                ACIEndpointSecurityGroup.objects.filter(
                    aci_app_profile__name=data["aci_app_profile"]
                )
            )
            self.fields[
                "aci_endpoint_security_group"
            ].queryset = aci_endpoint_security_group_queryset
