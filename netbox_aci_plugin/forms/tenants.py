# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import CommentField
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
