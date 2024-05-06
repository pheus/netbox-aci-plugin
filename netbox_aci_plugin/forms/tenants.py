# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.forms import NetBoxModelForm
from utilities.forms.fields import CommentField

from ..models.tenants import ACITenant


class ACITenantForm(NetBoxModelForm):
    """NetBox form for ACI Tenant model."""

    comments = CommentField()

    class Meta:
        model = ACITenant
        fields: tuple = ("name", "alias", "description", "comments", "tags")
