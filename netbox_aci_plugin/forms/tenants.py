# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import CommentField, TagFilterField
from utilities.forms.rendering import FieldSet

from ..models.tenants import ACITenant


class ACITenantForm(NetBoxModelForm):
    """NetBox form for ACI Tenant model."""

    comments = CommentField()

    fieldsets: tuple = (
        FieldSet("name", "alias", "description", "tags", name=_("ACI Tenant")),
    )

    class Meta:
        model = ACITenant
        fields: tuple = ("name", "alias", "description", "comments", "tags")


class ACITenantFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for ACI Tenant model."""

    model = ACITenant
    fieldsets: tuple = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "alias", "description", name="Attributes"),
    )

    name = forms.CharField(required=False)
    alias = forms.CharField(required=False)
    description = forms.CharField(required=False)
    tag = TagFilterField(ACITenant)
