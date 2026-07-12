# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

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
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle

from ...choices import DeploymentImmediacyChoices, ResolutionImmediacyChoices
from ...constants import (
    EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES,
    EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES,
)
from ...models.access_policies.domains import ACIPhysicalDomain
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.endpoint_group_bindings import ACIEndpointGroupDomainBinding
from ...models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup

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
        required=False,
        label=_("Deployment immediacy"),
        help_text=_(
            "When the policy is pushed into the leaf hardware. Default is 'On Demand'."
        ),
    )
    resolution_immediacy = forms.ChoiceField(
        choices=ResolutionImmediacyChoices,
        required=False,
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
