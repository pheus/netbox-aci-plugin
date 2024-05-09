# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from utilities.forms.rendering import FieldSet

from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenants import ACITenant


class ACIAppProfileForm(NetBoxModelForm):
    """NetBox form for ACI Application Profile model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        label=_("ACI Tenant"),
        query_params={"nb_tenant_id": "$nb_tenant"},
    )
    nb_tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("NetBox Tenant group"),
        initial_params={"tenants": "$nb_tenant"},
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
        query_params={"group_id": "$nb_tenant_group"},
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "alias",
            "aci_tenant",
            "description",
            "tags",
            name=_("ACI Application Profile"),
        ),
        FieldSet("nb_tenant_group", "nb_tenant", name=_("NetBox Tenancy")),
    )

    class Meta:
        model = ACIAppProfile
        fields: tuple = (
            "name",
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "comments",
            "tags",
        )
