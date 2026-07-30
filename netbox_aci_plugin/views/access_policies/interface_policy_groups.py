# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupFilterSet,
)
from ...forms.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupBulkEditForm,
    ACILeafInterfacePolicyGroupEditForm,
    ACILeafInterfacePolicyGroupFilterForm,
    ACILeafInterfacePolicyGroupImportForm,
)
from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ...tables.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupTable,
)

#
# Base children views
#


class ACILeafInterfacePolicyGroupChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Policy Groups."""

    child_model = ACILeafInterfacePolicyGroup
    filterset = ACILeafInterfacePolicyGroupFilterSet
    tab = ViewTab(
        label=_("Policy Groups"),
        badge=lambda obj: obj.aci_leaf_interface_policy_groups.count(),
        permission="netbox_aci_plugin.view_acileafinterfacepolicygroup",
        weight=2000,
    )
    table = ACILeafInterfacePolicyGroupTable

    def get_children(self, request, parent):
        """Return all objects of ACILeafInterfacePolicyGroup."""
        return (
            ACILeafInterfacePolicyGroup.objects.restrict(request.user, "view")
            .select_related(
                "aci_fabric",
                "aci_aaep",
                "nb_tenant",
                "owner",
            )
            .prefetch_related(
                "tags",
            )
        )


#
# Leaf Interface Policy Group views
#


@register_model_view(ACILeafInterfacePolicyGroup)
class ACILeafInterfacePolicyGroupView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Policy Group."""

    queryset = ACILeafInterfacePolicyGroup.objects.select_related(
        "aci_fabric",
        "aci_aaep",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACILeafInterfacePolicyGroup, "list", path="", detail=False)
class ACILeafInterfacePolicyGroupListView(generic.ObjectListView):
    """List view for listing all objects of ACI Leaf Interface Policy Group."""

    queryset = ACILeafInterfacePolicyGroup.objects.select_related(
        "aci_fabric",
        "aci_aaep",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACILeafInterfacePolicyGroupFilterSet
    filterset_form = ACILeafInterfacePolicyGroupFilterForm
    table = ACILeafInterfacePolicyGroupTable


@register_model_view(ACILeafInterfacePolicyGroup, "add", detail=False)
@register_model_view(ACILeafInterfacePolicyGroup, "edit")
class ACILeafInterfacePolicyGroupEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Leaf Interface Policy Group."""

    queryset = ACILeafInterfacePolicyGroup.objects.select_related(
        "aci_fabric",
        "aci_aaep",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACILeafInterfacePolicyGroupEditForm


@register_model_view(ACILeafInterfacePolicyGroup, "delete")
class ACILeafInterfacePolicyGroupDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Policy Group."""

    queryset = ACILeafInterfacePolicyGroup.objects.select_related(
        "aci_fabric",
        "aci_aaep",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(
    ACILeafInterfacePolicyGroup, "bulk_import", path="import", detail=False
)
class ACILeafInterfacePolicyGroupBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Policy Group."""

    queryset = ACILeafInterfacePolicyGroup.objects.all()
    model_form = ACILeafInterfacePolicyGroupImportForm


@register_model_view(
    ACILeafInterfacePolicyGroup, "bulk_edit", path="edit", detail=False
)
class ACILeafInterfacePolicyGroupBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Policy Group."""

    queryset = ACILeafInterfacePolicyGroup.objects.all()
    filterset = ACILeafInterfacePolicyGroupFilterSet
    table = ACILeafInterfacePolicyGroupTable
    form = ACILeafInterfacePolicyGroupBulkEditForm


@register_model_view(
    ACILeafInterfacePolicyGroup, "bulk_delete", path="delete", detail=False
)
class ACILeafInterfacePolicyGroupBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Policy Group."""

    queryset = ACILeafInterfacePolicyGroup.objects.all()
    filterset = ACILeafInterfacePolicyGroupFilterSet
    table = ACILeafInterfacePolicyGroupTable
