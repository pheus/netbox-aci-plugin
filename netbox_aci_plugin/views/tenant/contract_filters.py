# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from extras.ui.panels import CustomFieldsPanel, TagsPanel
from netbox.ui import actions, layout
from netbox.ui.breadcrumbs import Breadcrumb, filtered_list_url
from netbox.ui.panels import CommentsPanel, ObjectsTablePanel
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.contract_filters import (
    ACIContractFilterEntryFilterSet,
    ACIContractFilterFilterSet,
)
from ...forms.tenant.contract_filters import (
    ACIContractFilterBulkEditForm,
    ACIContractFilterEditForm,
    ACIContractFilterEntryBulkEditForm,
    ACIContractFilterEntryEditForm,
    ACIContractFilterEntryFilterForm,
    ACIContractFilterEntryImportForm,
    ACIContractFilterFilterForm,
    ACIContractFilterImportForm,
)
from ...models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ...object_actions import add_child_action
from ...tables.tenant.contract_filters import (
    ACIContractFilterEntryTable,
    ACIContractFilterTable,
)
from ...ui.panels.tenant.contract_filters import (
    ACIContractFilterEntryARPPanel,
    ACIContractFilterEntryEthernetPanel,
    ACIContractFilterEntryICMPPanel,
    ACIContractFilterEntryIPProtocolPanel,
    ACIContractFilterEntryPanel,
    ACIContractFilterEntryPortRangePanel,
    ACIContractFilterEntryTCPPanel,
    ACIContractFilterPanel,
)

#
# Base children views
#


class ACIContractFilterEntryChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Contract Filter Entry."""

    child_model = ACIContractFilterEntry
    filterset = ACIContractFilterEntryFilterSet
    tab = ViewTab(
        label=_("Filter Entries"),
        badge=lambda obj: obj.aci_contract_filter_entries.count(),
        permission="netbox_aci_plugin.view_acicontractfilterentry",
        weight=1000,
    )
    table = ACIContractFilterEntryTable

    def get_children(self, request, parent):
        """Return all objects of ACIContractFilterEntry."""
        return (
            ACIContractFilterEntry.objects.restrict(request.user, "view")
            .select_related("aci_contract_filter", "nb_tenant", "owner")
            .prefetch_related(
                "tags",
            )
        )


#
# Contract Filter views
#


@register_model_view(ACIContractFilter)
class ACIContractFilterView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        breadcrumbs=[
            Breadcrumb(
                "aci_fabric",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acicontractfilter_list",
                    "aci_fabric_id",
                ),
            ),
            Breadcrumb(
                "aci_tenant",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acicontractfilter_list",
                    "aci_tenant_id",
                ),
            ),
        ],
        left_panels=[
            ACIContractFilterPanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
        bottom_panels=[
            ObjectsTablePanel(
                "netbox_aci_plugin.ACIContractFilterEntry",
                title=_("Entries"),
                filters={"aci_contract_filter_id": lambda ctx: ctx["object"].pk},
                include_columns=[
                    "match_only_fragments_enabled",
                    "tcp_rules",
                ],
                exclude_columns=[
                    "aci_tenant",
                    "aci_contract_filter",
                    "description",
                    "tags",
                ],
                actions=[
                    actions.AddObject(
                        "netbox_aci_plugin.ACIContractFilterEntry",
                        label=_("Add an Entry"),
                        url_params={
                            "aci_contract_filter": lambda ctx: ctx["object"].pk,
                        },
                    ),
                ],
            ),
        ],
    )


@register_model_view(ACIContractFilter, "list", path="", detail=False)
class ACIContractFilterListView(generic.ObjectListView):
    """List view for listing all objects of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACIContractFilterFilterSet
    filterset_form = ACIContractFilterFilterForm
    table = ACIContractFilterTable


@register_model_view(ACIContractFilter, "add", detail=False)
@register_model_view(ACIContractFilter, "edit")
class ACIContractFilterEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACIContractFilterEditForm


@register_model_view(ACIContractFilter, "delete")
class ACIContractFilterDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIContractFilter, "contractfilterentries", path="entries")
class ACIContractFilterContractFilterEntryView(ACIContractFilterEntryChildrenView):
    """Children view of ACI Contract Filter Entry of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIContractFilterEntry",
            _("Add an Entry"),
            url_params={
                "aci_tenant": lambda ctx: ctx["object"].aci_tenant_id,
                "aci_contract_filter": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACIContractFilterEntryChildrenView.actions

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super().get_children(request, parent).filter(aci_contract_filter=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACIContractFilter column hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIContractFilter column
        table.columns.hide("aci_contract_filter")

        return table


@register_model_view(ACIContractFilter, "bulk_import", path="import", detail=False)
class ACIContractFilterBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    model_form = ACIContractFilterImportForm


@register_model_view(ACIContractFilter, "bulk_edit", path="edit", detail=False)
class ACIContractFilterBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    filterset = ACIContractFilterFilterSet
    table = ACIContractFilterTable
    form = ACIContractFilterBulkEditForm


@register_model_view(ACIContractFilter, "bulk_delete", path="delete", detail=False)
class ACIContractFilterBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    filterset = ACIContractFilterFilterSet
    table = ACIContractFilterTable


#
# Contract Filter Entry views
#


@register_model_view(ACIContractFilterEntry)
class ACIContractFilterEntryView(generic.ObjectView):
    """Detail view for displaying a single object of ACIContractFilterEntry."""

    queryset = ACIContractFilterEntry.objects.select_related(
        "aci_contract_filter",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        breadcrumbs=[
            Breadcrumb(
                "aci_fabric",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acicontractfilterentry_list",
                    "aci_fabric_id",
                ),
            ),
            Breadcrumb(
                "aci_tenant",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acicontractfilterentry_list",
                    "aci_tenant_id",
                ),
            ),
            Breadcrumb(
                "aci_contract_filter",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acicontractfilterentry_list",
                    "aci_contract_filter_id",
                ),
            ),
        ],
        left_panels=[
            ACIContractFilterEntryPanel(),
            ACIContractFilterEntryEthernetPanel(),
            ACIContractFilterEntryARPPanel(),
            ACIContractFilterEntryIPProtocolPanel(),
            ACIContractFilterEntryICMPPanel(),
            ACIContractFilterEntryPortRangePanel(),
            ACIContractFilterEntryTCPPanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
    )


@register_model_view(ACIContractFilterEntry, "list", path="", detail=False)
class ACIContractFilterEntryListView(generic.ObjectListView):
    """List view for listing all objects of ACIContractFilterEntry."""

    queryset = ACIContractFilterEntry.objects.select_related(
        "aci_contract_filter",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACIContractFilterEntryFilterSet
    filterset_form = ACIContractFilterEntryFilterForm
    table = ACIContractFilterEntryTable


@register_model_view(ACIContractFilterEntry, "add", detail=False)
@register_model_view(ACIContractFilterEntry, "edit")
class ACIContractFilterEntryEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACIContractFilterEntry."""

    queryset = ACIContractFilterEntry.objects.select_related(
        "aci_contract_filter",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACIContractFilterEntryEditForm


@register_model_view(ACIContractFilterEntry, "delete")
class ACIContractFilterEntryDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACIContractFilterEntry."""

    queryset = ACIContractFilterEntry.objects.select_related(
        "aci_contract_filter",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIContractFilterEntry, "bulk_import", path="import", detail=False)
class ACIContractFilterEntryBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of Filter Entry."""

    queryset = ACIContractFilterEntry.objects.all()
    model_form = ACIContractFilterEntryImportForm


@register_model_view(ACIContractFilterEntry, "bulk_edit", path="edit", detail=False)
class ACIContractFilterEntryBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of Filter Entry."""

    queryset = ACIContractFilterEntry.objects.all()
    filterset = ACIContractFilterEntryFilterSet
    table = ACIContractFilterEntryTable
    form = ACIContractFilterEntryBulkEditForm


@register_model_view(ACIContractFilterEntry, "bulk_delete", path="delete", detail=False)
class ACIContractFilterEntryBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of Filter Entry."""

    queryset = ACIContractFilterEntry.objects.all()
    filterset = ACIContractFilterEntryFilterSet
    table = ACIContractFilterEntryTable
