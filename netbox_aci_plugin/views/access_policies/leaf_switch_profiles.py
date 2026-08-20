# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.query import count_related
from utilities.views import ViewTab, register_model_view

from ...filtersets.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockFilterSet,
    ACILeafSelectorFilterSet,
    ACILeafSwitchProfileFilterSet,
    ACILeafSwitchProfileInterfaceBindingFilterSet,
)
from ...forms.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockBulkEditForm,
    ACILeafNodeBlockEditForm,
    ACILeafNodeBlockFilterForm,
    ACILeafNodeBlockImportForm,
    ACILeafSelectorBulkEditForm,
    ACILeafSelectorEditForm,
    ACILeafSelectorFilterForm,
    ACILeafSelectorImportForm,
    ACILeafSwitchProfileBulkEditForm,
    ACILeafSwitchProfileEditForm,
    ACILeafSwitchProfileFilterForm,
    ACILeafSwitchProfileImportForm,
    ACILeafSwitchProfileInterfaceBindingBulkEditForm,
    ACILeafSwitchProfileInterfaceBindingEditForm,
    ACILeafSwitchProfileInterfaceBindingFilterForm,
    ACILeafSwitchProfileInterfaceBindingImportForm,
)
from ...models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ...object_actions import add_child_action
from ...tables.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockTable,
    ACILeafSelectorTable,
    ACILeafSwitchProfileInterfaceBindingTable,
    ACILeafSwitchProfileTable,
)
from ...tables.fabric.nodes import ACINodeReducedTable

#
# Base children views
#


class ACILeafSelectorChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Leaf Selectors."""

    child_model = ACILeafSelector
    filterset = ACILeafSelectorFilterSet
    tab = ViewTab(
        label=_("Selectors"),
        badge=lambda obj: obj.aci_leaf_selectors.count(),
        permission="netbox_aci_plugin.view_acileafselector",
        weight=1000,
    )
    table = ACILeafSelectorTable

    def get_children(self, request, parent):
        """Return all ACILeafSelector objects."""
        return (
            ACILeafSelector.objects.restrict(request.user, "view")
            .select_related(
                "aci_leaf_switch_profile",
                "aci_leaf_switch_profile__aci_fabric",
                "nb_tenant",
                "owner",
            )
            .annotate(
                aci_leaf_node_block_count=count_related(
                    ACILeafNodeBlock, "aci_leaf_selector"
                )
            )
            .prefetch_related("tags")
        )


class ACILeafNodeBlockChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Leaf Node Blocks."""

    child_model = ACILeafNodeBlock
    filterset = ACILeafNodeBlockFilterSet
    tab = ViewTab(
        label=_("Node Blocks"),
        badge=lambda obj: obj.aci_leaf_node_blocks.count(),
        permission="netbox_aci_plugin.view_acileafnodeblock",
        weight=1000,
    )
    table = ACILeafNodeBlockTable

    def get_children(self, request, parent):
        """Return all ACILeafNodeBlock objects."""
        return (
            ACILeafNodeBlock.objects.restrict(request.user, "view")
            .select_related(
                "aci_leaf_selector",
                "aci_leaf_selector__aci_leaf_switch_profile",
                "aci_leaf_selector__aci_leaf_switch_profile__aci_fabric",
                "nb_tenant",
                "owner",
            )
            .annotate(aci_node_count=ACILeafNodeBlock.aci_node_count_annotation())
            .prefetch_related("tags")
        )


class ACILeafSwitchProfileInterfaceBindingChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching ACI Profile Bindings."""

    child_model = ACILeafSwitchProfileInterfaceBinding
    filterset = ACILeafSwitchProfileInterfaceBindingFilterSet
    tab = ViewTab(
        label=_("Interface Profiles"),
        badge=lambda obj: obj.aci_leaf_interface_profile_bindings.count(),
        permission="netbox_aci_plugin.view_acileafswitchprofileinterfacebinding",
        weight=1000,
    )
    table = ACILeafSwitchProfileInterfaceBindingTable

    def get_children(self, request, parent):
        """Return all ACILeafSwitchProfileInterfaceBinding objects."""
        return (
            ACILeafSwitchProfileInterfaceBinding.objects.restrict(request.user, "view")
            .select_related(
                "aci_leaf_switch_profile",
                "aci_leaf_switch_profile__aci_fabric",
                "aci_leaf_interface_profile",
                "aci_leaf_interface_profile__aci_fabric",
            )
            .prefetch_related("tags")
        )


#
# Leaf Switch Profile views
#


@register_model_view(ACILeafSwitchProfile)
class ACILeafSwitchProfileView(generic.ObjectView):
    """Detail view for displaying a single object of Leaf Switch Profile."""

    queryset = ACILeafSwitchProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACILeafSwitchProfile, "list", path="", detail=False)
class ACILeafSwitchProfileListView(generic.ObjectListView):
    """List view for listing all objects of ACI Leaf Switch Profile."""

    queryset = ACILeafSwitchProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    filterset = ACILeafSwitchProfileFilterSet
    filterset_form = ACILeafSwitchProfileFilterForm
    table = ACILeafSwitchProfileTable


@register_model_view(ACILeafSwitchProfile, "add", detail=False)
@register_model_view(ACILeafSwitchProfile, "edit")
class ACILeafSwitchProfileEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Leaf Switch Profile."""

    queryset = ACILeafSwitchProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACILeafSwitchProfileEditForm


@register_model_view(ACILeafSwitchProfile, "delete")
class ACILeafSwitchProfileDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Leaf Switch Profile."""

    queryset = ACILeafSwitchProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACILeafSwitchProfile, "leafselectors", path="selectors")
class ACILeafSwitchProfileLeafSelectorView(ACILeafSelectorChildrenView):
    """Children view of ACI Leaf Selectors of ACI Leaf Switch Profile."""

    queryset = ACILeafSwitchProfile.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACILeafSelector",
            _("Add a Selector"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_fabric_id,
                "aci_leaf_switch_profile": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACILeafSelectorChildrenView.actions

    def get_children(self, request, parent):
        """Return all Leaf Selectors for the current Leaf Switch Profile."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_leaf_switch_profile=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACILeafSwitchProfile column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_leaf_switch_profile")
        return table


@register_model_view(
    ACILeafSwitchProfile, "interfaceprofilebindings", path="interface-profiles"
)
class ACILeafSwitchProfileInterfaceBindingsView(
    ACILeafSwitchProfileInterfaceBindingChildrenView
):
    """Children view of Profile Bindings of ACI Leaf Switch Profile."""

    queryset = ACILeafSwitchProfile.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACILeafSwitchProfileInterfaceBinding",
            _("Attach an Interface Profile"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_fabric_id,
                "aci_leaf_switch_profile": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACILeafSwitchProfileInterfaceBindingChildrenView.actions

    def get_children(self, request, parent):
        """Return all Profile Bindings for the current Switch Profile."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_leaf_switch_profile=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACILeafSwitchProfile column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_leaf_switch_profile")
        return table


@register_model_view(ACILeafSwitchProfile, "bulk_import", path="import", detail=False)
class ACILeafSwitchProfileBulkImportView(generic.BulkImportView):
    """Bulk import view for importing Leaf Switch Profile objects."""

    queryset = ACILeafSwitchProfile.objects.all()
    model_form = ACILeafSwitchProfileImportForm


@register_model_view(ACILeafSwitchProfile, "bulk_edit", path="edit", detail=False)
class ACILeafSwitchProfileBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of Leaf Switch Profile."""

    queryset = ACILeafSwitchProfile.objects.all()
    filterset = ACILeafSwitchProfileFilterSet
    table = ACILeafSwitchProfileTable
    form = ACILeafSwitchProfileBulkEditForm


@register_model_view(ACILeafSwitchProfile, "bulk_delete", path="delete", detail=False)
class ACILeafSwitchProfileBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting Leaf Switch Profile objects."""

    queryset = ACILeafSwitchProfile.objects.all()
    filterset = ACILeafSwitchProfileFilterSet
    table = ACILeafSwitchProfileTable


#
# Leaf Selector views
#


@register_model_view(ACILeafSelector)
class ACILeafSelectorView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Leaf Selector."""

    queryset = ACILeafSelector.objects.select_related(
        "aci_leaf_switch_profile",
        "aci_leaf_switch_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")

    def get_extra_context(self, request, instance) -> dict:
        """Return the resolved ACI Nodes as extra context."""
        aci_nodes_table = ACINodeReducedTable(
            instance.aci_nodes.restrict(request.user, "view").order_by("node_id")
        )
        aci_nodes_table.configure(request=request)
        return {"aci_nodes_table": aci_nodes_table}


@register_model_view(ACILeafSelector, "list", path="", detail=False)
class ACILeafSelectorListView(generic.ObjectListView):
    """List view for listing all objects of ACI Leaf Selector."""

    queryset = (
        ACILeafSelector.objects.select_related(
            "aci_leaf_switch_profile",
            "aci_leaf_switch_profile__aci_fabric",
            "nb_tenant",
            "owner",
        )
        .annotate(
            aci_leaf_node_block_count=count_related(
                ACILeafNodeBlock, "aci_leaf_selector"
            )
        )
        .prefetch_related("tags")
    )
    filterset = ACILeafSelectorFilterSet
    filterset_form = ACILeafSelectorFilterForm
    table = ACILeafSelectorTable


@register_model_view(ACILeafSelector, "add", detail=False)
@register_model_view(ACILeafSelector, "edit")
class ACILeafSelectorEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Leaf Selector."""

    queryset = ACILeafSelector.objects.select_related(
        "aci_leaf_switch_profile",
        "aci_leaf_switch_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACILeafSelectorEditForm


@register_model_view(ACILeafSelector, "delete")
class ACILeafSelectorDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Leaf Selector."""

    queryset = ACILeafSelector.objects.select_related(
        "aci_leaf_switch_profile",
        "aci_leaf_switch_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACILeafSelector, "leafnodeblocks", path="node-blocks")
class ACILeafSelectorLeafNodeBlockView(ACILeafNodeBlockChildrenView):
    """Children view of ACI Leaf Node Blocks of ACI Leaf Selector."""

    # The Profile and its Fabric are joined so the prefill below costs no
    # extra query.
    queryset = ACILeafSelector.objects.select_related(
        "aci_leaf_switch_profile__aci_fabric"
    )
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACILeafNodeBlock",
            _("Add a Node Block"),
            url_params={
                "aci_fabric": (
                    lambda ctx: ctx["object"].aci_leaf_switch_profile.aci_fabric_id
                ),
                "aci_leaf_switch_profile": (
                    lambda ctx: ctx["object"].aci_leaf_switch_profile_id
                ),
                "aci_leaf_selector": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACILeafNodeBlockChildrenView.actions

    def get_children(self, request, parent):
        """Return all Leaf Node Block objects for the current Leaf Selector."""
        return super().get_children(request, parent).filter(aci_leaf_selector=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACILeafSelector column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_leaf_selector")
        return table


@register_model_view(ACILeafSelector, "bulk_import", path="import", detail=False)
class ACILeafSelectorBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Leaf Selector."""

    queryset = ACILeafSelector.objects.all()
    model_form = ACILeafSelectorImportForm


@register_model_view(ACILeafSelector, "bulk_edit", path="edit", detail=False)
class ACILeafSelectorBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Leaf Selector."""

    # The table's node block count is an annotation, so the confirmation
    # table renders a placeholder without it.
    queryset = ACILeafSelector.objects.annotate(
        aci_leaf_node_block_count=count_related(ACILeafNodeBlock, "aci_leaf_selector")
    )
    filterset = ACILeafSelectorFilterSet
    table = ACILeafSelectorTable
    form = ACILeafSelectorBulkEditForm


@register_model_view(ACILeafSelector, "bulk_delete", path="delete", detail=False)
class ACILeafSelectorBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Leaf Selector."""

    # The table's node block count is an annotation, so the confirmation
    # table renders a placeholder without it.
    queryset = ACILeafSelector.objects.annotate(
        aci_leaf_node_block_count=count_related(ACILeafNodeBlock, "aci_leaf_selector")
    )
    filterset = ACILeafSelectorFilterSet
    table = ACILeafSelectorTable


#
# Leaf Node Block views
#


@register_model_view(ACILeafNodeBlock)
class ACILeafNodeBlockView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Leaf Node Block."""

    queryset = ACILeafNodeBlock.objects.select_related(
        "aci_leaf_selector",
        "aci_leaf_selector__aci_leaf_switch_profile",
        "aci_leaf_selector__aci_leaf_switch_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")

    def get_extra_context(self, request, instance) -> dict:
        """Return the covered ACI Nodes as extra context."""
        aci_nodes_table = ACINodeReducedTable(
            instance.aci_nodes.restrict(request.user, "view").order_by("node_id")
        )
        aci_nodes_table.configure(request=request)
        return {"aci_nodes_table": aci_nodes_table}


@register_model_view(ACILeafNodeBlock, "list", path="", detail=False)
class ACILeafNodeBlockListView(generic.ObjectListView):
    """List view for listing all objects of ACI Leaf Node Block."""

    queryset = (
        ACILeafNodeBlock.objects.select_related(
            "aci_leaf_selector",
            "aci_leaf_selector__aci_leaf_switch_profile",
            "aci_leaf_selector__aci_leaf_switch_profile__aci_fabric",
            "nb_tenant",
            "owner",
        )
        .annotate(aci_node_count=ACILeafNodeBlock.aci_node_count_annotation())
        .prefetch_related("tags")
    )
    filterset = ACILeafNodeBlockFilterSet
    filterset_form = ACILeafNodeBlockFilterForm
    table = ACILeafNodeBlockTable


@register_model_view(ACILeafNodeBlock, "add", detail=False)
@register_model_view(ACILeafNodeBlock, "edit")
class ACILeafNodeBlockEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Leaf Node Block."""

    queryset = ACILeafNodeBlock.objects.select_related(
        "aci_leaf_selector",
        "aci_leaf_selector__aci_leaf_switch_profile",
        "aci_leaf_selector__aci_leaf_switch_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACILeafNodeBlockEditForm


@register_model_view(ACILeafNodeBlock, "delete")
class ACILeafNodeBlockDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Leaf Node Block."""

    queryset = ACILeafNodeBlock.objects.select_related(
        "aci_leaf_selector",
        "aci_leaf_selector__aci_leaf_switch_profile",
        "aci_leaf_selector__aci_leaf_switch_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACILeafNodeBlock, "bulk_import", path="import", detail=False)
class ACILeafNodeBlockBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of Leaf Node Block."""

    queryset = ACILeafNodeBlock.objects.all()
    model_form = ACILeafNodeBlockImportForm


@register_model_view(ACILeafNodeBlock, "bulk_edit", path="edit", detail=False)
class ACILeafNodeBlockBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Leaf Node Block."""

    # The table's node count is an annotation, so the confirmation table
    # renders a placeholder without it.
    queryset = ACILeafNodeBlock.objects.annotate(
        aci_node_count=ACILeafNodeBlock.aci_node_count_annotation()
    )
    filterset = ACILeafNodeBlockFilterSet
    table = ACILeafNodeBlockTable
    form = ACILeafNodeBlockBulkEditForm


@register_model_view(ACILeafNodeBlock, "bulk_delete", path="delete", detail=False)
class ACILeafNodeBlockBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of Leaf Node Block."""

    # The table's node count is an annotation, so the confirmation table
    # renders a placeholder without it.
    queryset = ACILeafNodeBlock.objects.annotate(
        aci_node_count=ACILeafNodeBlock.aci_node_count_annotation()
    )
    filterset = ACILeafNodeBlockFilterSet
    table = ACILeafNodeBlockTable


#
# Leaf Switch Profile Interface Binding views
#


@register_model_view(ACILeafSwitchProfileInterfaceBinding)
class ACILeafSwitchProfileInterfaceBindingView(generic.ObjectView):
    """Detail view for a single object of ACI Profile Binding."""

    queryset = ACILeafSwitchProfileInterfaceBinding.objects.select_related(
        "aci_leaf_switch_profile",
        "aci_leaf_switch_profile__aci_fabric",
        "aci_leaf_interface_profile",
        "aci_leaf_interface_profile__aci_fabric",
    ).prefetch_related("tags")


@register_model_view(
    ACILeafSwitchProfileInterfaceBinding, "list", path="", detail=False
)
class ACILeafSwitchProfileInterfaceBindingListView(generic.ObjectListView):
    """List view for listing all objects of ACI Profile Binding."""

    queryset = ACILeafSwitchProfileInterfaceBinding.objects.select_related(
        "aci_leaf_switch_profile",
        "aci_leaf_switch_profile__aci_fabric",
        "aci_leaf_interface_profile",
        "aci_leaf_interface_profile__aci_fabric",
    ).prefetch_related("tags")
    filterset = ACILeafSwitchProfileInterfaceBindingFilterSet
    filterset_form = ACILeafSwitchProfileInterfaceBindingFilterForm
    table = ACILeafSwitchProfileInterfaceBindingTable


@register_model_view(ACILeafSwitchProfileInterfaceBinding, "add", detail=False)
@register_model_view(ACILeafSwitchProfileInterfaceBinding, "edit")
class ACILeafSwitchProfileInterfaceBindingEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Profile Binding."""

    queryset = ACILeafSwitchProfileInterfaceBinding.objects.select_related(
        "aci_leaf_switch_profile",
        "aci_leaf_switch_profile__aci_fabric",
        "aci_leaf_interface_profile",
        "aci_leaf_interface_profile__aci_fabric",
    ).prefetch_related("tags")
    form = ACILeafSwitchProfileInterfaceBindingEditForm


@register_model_view(ACILeafSwitchProfileInterfaceBinding, "delete")
class ACILeafSwitchProfileInterfaceBindingDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Profile Binding."""

    queryset = ACILeafSwitchProfileInterfaceBinding.objects.select_related(
        "aci_leaf_switch_profile",
        "aci_leaf_switch_profile__aci_fabric",
        "aci_leaf_interface_profile",
        "aci_leaf_interface_profile__aci_fabric",
    ).prefetch_related("tags")


@register_model_view(
    ACILeafSwitchProfileInterfaceBinding, "bulk_import", path="import", detail=False
)
class ACILeafSwitchProfileInterfaceBindingBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple ACI Profile Bindings."""

    queryset = ACILeafSwitchProfileInterfaceBinding.objects.all()
    model_form = ACILeafSwitchProfileInterfaceBindingImportForm


@register_model_view(
    ACILeafSwitchProfileInterfaceBinding, "bulk_edit", path="edit", detail=False
)
class ACILeafSwitchProfileInterfaceBindingBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple ACI Profile Bindings."""

    queryset = ACILeafSwitchProfileInterfaceBinding.objects.all()
    filterset = ACILeafSwitchProfileInterfaceBindingFilterSet
    table = ACILeafSwitchProfileInterfaceBindingTable
    form = ACILeafSwitchProfileInterfaceBindingBulkEditForm


@register_model_view(
    ACILeafSwitchProfileInterfaceBinding, "bulk_delete", path="delete", detail=False
)
class ACILeafSwitchProfileInterfaceBindingBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple ACI Profile Bindings."""

    queryset = ACILeafSwitchProfileInterfaceBinding.objects.all()
    filterset = ACILeafSwitchProfileInterfaceBindingFilterSet
    table = ACILeafSwitchProfileInterfaceBindingTable
