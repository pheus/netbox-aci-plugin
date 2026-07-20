# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from ipam.models import VLAN, VLANGroup
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from utilities.forms import add_blank_choice, get_field_value
from utilities.forms.fields import (
    CommentField,
    ContentTypeChoiceField,
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle

from ...choices import (
    DeploymentImmediacyChoices,
    PortModeChoices,
    ResolutionImmediacyChoices,
)
from ...constants import (
    EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES,
    EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES,
)
from ...models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ...models.access_policies.domains import ACIPhysicalDomain
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBinding,
    ACIEndpointGroupDomainBinding,
)
from ...models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ...models.tenant.tenants import ACITenant

#
# Endpoint Group Domain Binding forms
#


class ACIEndpointGroupDomainBindingEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Endpoint Group Domain Binding model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_epg_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES),
        widget=HTMXSelect(),
        label=_("ACI EPG object type"),
    )
    aci_epg_object = DynamicModelChoiceField(
        queryset=ACIEndpointGroup.objects.none(),  # Initial queryset
        query_params={"aci_fabric_id": "$aci_fabric"},
        selector=True,
        label=_("ACI EPG object"),
        disabled=True,
    )
    aci_domain_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES),
        widget=HTMXSelect(),
        label=_("ACI domain object type"),
    )
    aci_domain_object = DynamicModelChoiceField(
        queryset=ACIPhysicalDomain.objects.none(),  # Initial queryset
        query_params={"aci_fabric_id": "$aci_fabric"},
        selector=True,
        label=_("ACI domain object"),
        disabled=True,
    )
    deployment_immediacy = forms.ChoiceField(
        choices=DeploymentImmediacyChoices,
        label=_("Deployment immediacy"),
        help_text=_(
            "When the policy is pushed into the leaf hardware. Default is 'On Demand'."
        ),
    )
    resolution_immediacy = forms.ChoiceField(
        choices=ResolutionImmediacyChoices,
        label=_("Resolution immediacy"),
        help_text=_(
            "When the policy is downloaded to the leaf software. Default is "
            "'On Demand'."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "aci_epg_object_type",
            "aci_epg_object",
            "aci_domain_object_type",
            "aci_domain_object",
            "tags",
            name=_("ACI Endpoint Group Domain Binding"),
        ),
        FieldSet(
            "deployment_immediacy",
            "resolution_immediacy",
            name=_("Immediacy Settings"),
        ),
    )

    class Meta:
        model = ACIEndpointGroupDomainBinding
        fields: tuple = (
            "aci_epg_object_type",
            "aci_domain_object_type",
            "deployment_immediacy",
            "resolution_immediacy",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI Endpoint Group Domain Binding form."""
        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.aci_epg_object:
            # Initialize ACI EPG object field
            initial["aci_epg_object"] = instance.aci_epg_object

        if instance is not None and instance.aci_domain_object:
            # Initialize ACI domain object field
            initial["aci_domain_object"] = instance.aci_domain_object
            # Seed helper aci_fabric from the bound domain's fabric
            initial["aci_fabric"] = instance.aci_domain_object.aci_fabric

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if aci_epg_object_type_id := get_field_value(self, "aci_epg_object_type"):
            try:
                # Retrieve the ContentType model class based on the ACI EPG
                # object type
                aci_epg_object_type = ContentType.objects.get(pk=aci_epg_object_type_id)
                aci_epg_model = aci_epg_object_type.model_class()

                # Configure queryset and label for the aci_epg_object field
                self.fields["aci_epg_object"].queryset = aci_epg_model.objects.all()
                self.fields["aci_epg_object"].widget.attrs["selector"] = (
                    aci_epg_model._meta.label_lower
                )
                self.fields["aci_epg_object"].disabled = False
                self.fields["aci_epg_object"].label = _(
                    bettertitle(aci_epg_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:  # pragma: no cover
                pass

            # Clear the aci_epg_object field if the selected type changes
            if (
                self.instance
                and self.instance.pk
                and aci_epg_object_type_id != self.instance.aci_epg_object_type_id
            ):
                self.initial["aci_epg_object"] = None

        if aci_domain_object_type_id := get_field_value(self, "aci_domain_object_type"):
            try:
                # Retrieve the ContentType model class based on the ACI domain
                # object type
                aci_domain_object_type = ContentType.objects.get(
                    pk=aci_domain_object_type_id
                )
                aci_domain_model = aci_domain_object_type.model_class()

                # Configure queryset and label for the aci_domain_object field
                self.fields[
                    "aci_domain_object"
                ].queryset = aci_domain_model.objects.all()
                self.fields["aci_domain_object"].widget.attrs["selector"] = (
                    aci_domain_model._meta.label_lower
                )
                self.fields["aci_domain_object"].disabled = False
                self.fields["aci_domain_object"].label = _(
                    bettertitle(aci_domain_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:  # pragma: no cover
                pass

            # Clear the aci_domain_object field if the selected type changes
            if (
                self.instance
                and self.instance.pk
                and aci_domain_object_type_id != self.instance.aci_domain_object_type_id
            ):
                self.initial["aci_domain_object"] = None

    def clean(self) -> None:
        """Validate fields for the ACI Endpoint Group Domain Binding form."""
        super().clean()

        # Ensure the selected ACI EPG and domain objects get assigned
        self.instance.aci_epg_object = self.cleaned_data.get("aci_epg_object")
        self.instance.aci_domain_object = self.cleaned_data.get("aci_domain_object")


class ACIEndpointGroupDomainBindingBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for ACI Endpoint Group Domain Binding model."""

    deployment_immediacy = forms.ChoiceField(
        choices=add_blank_choice(DeploymentImmediacyChoices),
        required=False,
        label=_("Deployment immediacy"),
    )
    resolution_immediacy = forms.ChoiceField(
        choices=add_blank_choice(ResolutionImmediacyChoices),
        required=False,
        label=_("Resolution immediacy"),
    )
    comments = CommentField()

    model = ACIEndpointGroupDomainBinding
    fieldsets: tuple = (
        FieldSet(
            "deployment_immediacy",
            "resolution_immediacy",
            name=_("ACI Endpoint Group Domain Binding"),
        ),
    )
    nullable_fields: tuple = ("comments",)


class ACIEndpointGroupDomainBindingFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Endpoint Group Domain Binding model."""

    model = ACIEndpointGroupDomainBinding
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "aci_fabric_id",
            "deployment_immediacy",
            "resolution_immediacy",
            name=_("Attributes"),
        ),
        FieldSet(
            "aci_endpoint_group_id",
            "aci_useg_endpoint_group_id",
            name=_("ACI Endpoint Group Assignment"),
        ),
        FieldSet(
            "aci_physical_domain_id",
            name=_("ACI Domain Assignment"),
        ),
    )

    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    deployment_immediacy = forms.MultipleChoiceField(
        choices=add_blank_choice(DeploymentImmediacyChoices),
        required=False,
        label=_("Deployment immediacy"),
    )
    resolution_immediacy = forms.MultipleChoiceField(
        choices=add_blank_choice(ResolutionImmediacyChoices),
        required=False,
        label=_("Resolution immediacy"),
    )
    aci_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointGroup.objects.all(),
        required=False,
        label=_("ACI Endpoint Group"),
    )
    aci_useg_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIUSegEndpointGroup.objects.all(),
        required=False,
        label=_("ACI uSeg Endpoint Group"),
    )
    aci_physical_domain_id = DynamicModelMultipleChoiceField(
        queryset=ACIPhysicalDomain.objects.all(),
        required=False,
        label=_("ACI Physical Domain"),
    )
    tag = TagFilterField(model)


class ACIEndpointGroupDomainBindingImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Endpoint Group Domain Binding model."""

    aci_epg_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES),
        label=_("ACI EPG object type (app & model)"),
    )
    aci_epg_object_id = forms.IntegerField(
        required=True,
        label=_("ACI EPG object ID"),
    )
    aci_domain_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES),
        label=_("ACI domain object type (app & model)"),
    )
    aci_domain_object_id = forms.IntegerField(
        required=True,
        label=_("ACI domain object ID"),
    )
    deployment_immediacy = CSVChoiceField(
        choices=DeploymentImmediacyChoices,
        required=False,
        label=_("Deployment immediacy"),
        help_text=_(
            "When the policy is pushed into the leaf hardware. Default is 'On Demand'."
        ),
    )
    resolution_immediacy = CSVChoiceField(
        choices=ResolutionImmediacyChoices,
        required=False,
        label=_("Resolution immediacy"),
        help_text=_(
            "When the policy is downloaded to the leaf software. Default is "
            "'On Demand'."
        ),
    )

    class Meta:
        model = ACIEndpointGroupDomainBinding
        fields: tuple = (
            "aci_epg_object_type",
            "aci_epg_object_id",
            "aci_domain_object_type",
            "aci_domain_object_id",
            "deployment_immediacy",
            "resolution_immediacy",
            "comments",
            "tags",
        )

    def _clean_field_default_lazy(self, field_name) -> str:
        """Return default value for empty imported field."""
        field_value = self.cleaned_data.get(field_name, None)
        if not field_value:
            return DeploymentImmediacyChoices.IMMEDIACY_LAZY
        return field_value

    def clean_deployment_immediacy(self) -> str:
        """Return a cleaned and validated value for deployment_immediacy."""
        return self._clean_field_default_lazy("deployment_immediacy")

    def clean_resolution_immediacy(self) -> str:
        """Return a cleaned and validated value for resolution_immediacy."""
        return self._clean_field_default_lazy("resolution_immediacy")


#
# Endpoint Group AAEP Binding forms
#


class ACIEndpointGroupAAEPBindingEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Endpoint Group AAEP Binding model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_tenants__aci_app_profiles__aci_endpoint_groups": (
                "$aci_endpoint_group"
            ),
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={"aci_app_profiles__aci_endpoint_groups": "$aci_endpoint_group"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
        },
        initial_params={"aci_endpoint_groups": "$aci_endpoint_group"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_group = DynamicModelChoiceField(
        queryset=ACIEndpointGroup.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_app_profile",
        },
        label=_("ACI Endpoint Group"),
    )
    aci_aaep = DynamicModelChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI AAEP"),
    )
    nb_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_("NetBox VLAN"),
    )
    primary_nb_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_("Primary NetBox VLAN"),
    )
    mode = forms.ChoiceField(
        choices=PortModeChoices,
        label=_("Mode"),
        help_text=_("VLAN tagging mode of the deployment (default 'Trunk')."),
    )
    deployment_immediacy = forms.ChoiceField(
        choices=DeploymentImmediacyChoices,
        label=_("Deployment immediacy"),
        help_text=_(
            "When the policy is pushed into the leaf hardware. Default is 'On Demand'."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_group",
            "aci_aaep",
            "tags",
            name=_("ACI Endpoint Group AAEP Binding"),
        ),
        FieldSet(
            "nb_vlan",
            "encap_vlan_id",
            "primary_nb_vlan",
            "primary_encap_vlan_id",
            "mode",
            name=_("VLAN Encapsulation"),
        ),
        FieldSet(
            "deployment_immediacy",
            name=_("Immediacy Settings"),
        ),
    )

    class Meta:
        model = ACIEndpointGroupAAEPBinding
        fields: tuple = (
            "aci_endpoint_group",
            "aci_aaep",
            "nb_vlan",
            "encap_vlan_id",
            "primary_nb_vlan",
            "primary_encap_vlan_id",
            "mode",
            "deployment_immediacy",
            "comments",
            "tags",
        )


class ACIEndpointGroupAAEPBindingBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Endpoint Group AAEP Binding model."""

    mode = forms.ChoiceField(
        choices=add_blank_choice(PortModeChoices),
        required=False,
        label=_("Mode"),
    )
    deployment_immediacy = forms.ChoiceField(
        choices=add_blank_choice(DeploymentImmediacyChoices),
        required=False,
        label=_("Deployment immediacy"),
    )
    comments = CommentField()

    model = ACIEndpointGroupAAEPBinding
    fieldsets: tuple = (
        FieldSet(
            "mode",
            "deployment_immediacy",
            name=_("ACI Endpoint Group AAEP Binding"),
        ),
    )
    nullable_fields: tuple = ("comments",)


class ACIEndpointGroupAAEPBindingFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Endpoint Group AAEP Binding model."""

    model = ACIEndpointGroupAAEPBinding
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "aci_fabric_id",
            "aci_aaep_id",
            "mode",
            "deployment_immediacy",
            name=_("Attributes"),
        ),
        FieldSet(
            "aci_tenant_id",
            "aci_app_profile_id",
            "aci_endpoint_group_id",
            name=_("ACI Endpoint Group Assignment"),
        ),
        FieldSet(
            "nb_vlan_id",
            "encap_vlan_id",
            "effective_encap_vlan_id",
            name=_("VLAN Encapsulation"),
        ),
    )

    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_aaep_id = DynamicModelMultipleChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        required=False,
        label=_("ACI AAEP"),
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointGroup.objects.all(),
        required=False,
        label=_("ACI Endpoint Group"),
    )
    nb_vlan_id = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_("NetBox VLAN"),
    )
    encap_vlan_id = forms.IntegerField(
        required=False,
        label=_("Encap VLAN ID"),
    )
    effective_encap_vlan_id = forms.IntegerField(
        required=False,
        label=_("Effective Encap VLAN ID"),
    )
    mode = forms.MultipleChoiceField(
        choices=add_blank_choice(PortModeChoices),
        required=False,
        label=_("Mode"),
    )
    deployment_immediacy = forms.MultipleChoiceField(
        choices=add_blank_choice(DeploymentImmediacyChoices),
        required=False,
        label=_("Deployment immediacy"),
    )
    tag = TagFilterField(model)


class ACIEndpointGroupAAEPBindingImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Endpoint Group AAEP Binding model."""

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
    aci_app_profile = CSVModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_group = CSVModelChoiceField(
        queryset=ACIEndpointGroup.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Endpoint Group"),
    )
    aci_aaep = CSVModelChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI AAEP"),
    )
    nb_vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        to_field_name="vid",
        required=False,
        label=_("NetBox VLAN"),
        help_text=_("Assigned NetBox VLAN"),
    )
    nb_vlan_group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox VLAN group"),
        help_text=_("VLAN group used to resolve the NetBox VLAN's VID."),
    )
    primary_nb_vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        to_field_name="vid",
        required=False,
        label=_("Primary NetBox VLAN"),
        help_text=_("Assigned primary NetBox VLAN"),
    )
    primary_nb_vlan_group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Primary NetBox VLAN group"),
        help_text=_("VLAN group used to resolve the primary NetBox VLAN's VID."),
    )
    mode = CSVChoiceField(
        choices=PortModeChoices,
        required=False,
        label=_("Mode"),
        help_text=_("VLAN tagging mode of the deployment (default 'Trunk')."),
    )
    deployment_immediacy = CSVChoiceField(
        choices=DeploymentImmediacyChoices,
        required=False,
        label=_("Deployment immediacy"),
        help_text=_(
            "When the policy is pushed into the leaf hardware. Default is 'On Demand'."
        ),
    )

    class Meta:
        model = ACIEndpointGroupAAEPBinding
        fields: tuple = (
            "aci_fabric",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_group",
            "aci_aaep",
            "nb_vlan",
            "nb_vlan_group",
            "encap_vlan_id",
            "primary_nb_vlan",
            "primary_nb_vlan_group",
            "primary_encap_vlan_id",
            "mode",
            "deployment_immediacy",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)
        if not data:
            return
        if data.get("aci_fabric"):
            self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            self.fields[
                "aci_aaep"
            ].queryset = ACIAttachableAccessEntityProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            if data.get("aci_tenant"):
                self.fields["aci_app_profile"].queryset = ACIAppProfile.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name=data["aci_tenant"],
                )
                if data.get("aci_app_profile"):
                    self.fields[
                        "aci_endpoint_group"
                    ].queryset = ACIEndpointGroup.objects.filter(
                        aci_app_profile__aci_tenant__aci_fabric__name=(
                            data["aci_fabric"]
                        ),
                        aci_app_profile__aci_tenant__name=data["aci_tenant"],
                        aci_app_profile__name=data["aci_app_profile"],
                    )
        if data.get("nb_vlan_group"):
            self.fields["nb_vlan"].queryset = self.fields["nb_vlan"].queryset.filter(
                group__name=data["nb_vlan_group"]
            )
        if data.get("primary_nb_vlan_group"):
            self.fields["primary_nb_vlan"].queryset = self.fields[
                "primary_nb_vlan"
            ].queryset.filter(group__name=data["primary_nb_vlan_group"])

    def _clean_field_default(self, field_name, default) -> str:
        """Return default value for empty imported field."""
        field_value = self.cleaned_data.get(field_name, None)
        if not field_value:
            return default
        return field_value

    def clean_mode(self) -> str:
        """Return a cleaned and validated value for mode."""
        return self._clean_field_default("mode", PortModeChoices.MODE_REGULAR)

    def clean_deployment_immediacy(self) -> str:
        """Return a cleaned and validated value for deployment_immediacy."""
        return self._clean_field_default(
            "deployment_immediacy", DeploymentImmediacyChoices.IMMEDIACY_LAZY
        )
