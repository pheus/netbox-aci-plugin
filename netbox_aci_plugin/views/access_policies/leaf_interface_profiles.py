# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from extras.ui.panels import CustomFieldsPanel, TagsPanel
from netbox.ui import layout
from netbox.ui.breadcrumbs import Breadcrumb, filtered_list_url
from netbox.ui.panels import CommentsPanel
from netbox.views import generic
from utilities.query import count_related
from utilities.views import ViewTab, register_model_view

from ...filtersets.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfileFilterSet,
    ACILeafInterfaceSelectorFilterSet,
    ACILeafPortBlockFilterSet,
)
from ...forms.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfileBulkEditForm,
    ACILeafInterfaceProfileEditForm,
    ACILeafInterfaceProfileFilterForm,
    ACILeafInterfaceProfileImportForm,
    ACILeafInterfaceSelectorBulkEditForm,
    ACILeafInterfaceSelectorEditForm,
    ACILeafInterfaceSelectorFilterForm,
    ACILeafInterfaceSelectorImportForm,
    ACILeafPortBlockBulkEditForm,
    ACILeafPortBlockEditForm,
    ACILeafPortBlockFilterForm,
    ACILeafPortBlockImportForm,
)
from ...models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ...object_actions import add_child_action
from ...tables.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfileTable,
    ACILeafInterfaceSelectorTable,
    ACILeafPortBlockTable,
)
from ...ui.panels.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfilePanel,
    ACILeafInterfaceSelectorPanel,
    ACILeafPortBlockPanel,
    ACILeafPortBlockRangePanel,
)
from .leaf_switch_profiles import ACILeafSwitchProfileInterfaceBindingChildrenView

#
# Base children views
#


class ACILeafInterfaceSelectorChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of Leaf Interface Selectors."""

    child_model = ACILeafInterfaceSelector
    filterset = ACILeafInterfaceSelectorFilterSet
    tab = ViewTab(
        label=_("Selectors"),
        badge=lambda obj: obj.aci_leaf_interface_selectors.count(),
        permission="netbox_aci_plugin.view_acileafinterfaceselector",
        weight=1000,
    )
    table = ACILeafInterfaceSelectorTable

    def get_children(self, request, parent):
        """Return all ACILeafInterfaceSelector objects."""
        return (
            ACILeafInterfaceSelector.objects.restrict(request.user, "view")
            .select_related(
                "aci_leaf_interface_profile",
                "aci_leaf_interface_profile__aci_fabric",
                "aci_leaf_interface_policy_group",
                "nb_tenant",
                "owner",
            )
            .annotate(
                aci_leaf_port_block_count=count_related(
                    ACILeafPortBlock, "aci_leaf_interface_selector"
                )
            )
            .prefetch_related("tags")
        )


class ACILeafPortBlockChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Leaf Port Blocks."""

    child_model = ACILeafPortBlock
    filterset = ACILeafPortBlockFilterSet
    tab = ViewTab(
        label=_("Port Blocks"),
        badge=lambda obj: obj.aci_leaf_port_blocks.count(),
        permission="netbox_aci_plugin.view_acileafportblock",
        weight=1000,
    )
    table = ACILeafPortBlockTable

    def get_children(self, request, parent):
        """Return all ACILeafPortBlock objects."""
        return (
            ACILeafPortBlock.objects.restrict(request.user, "view")
            .select_related(
                "aci_leaf_interface_selector",
                "aci_leaf_interface_selector__aci_leaf_interface_profile",
                "aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric",
                "nb_tenant",
                "owner",
            )
            .prefetch_related("tags")
        )


#
# Leaf Interface Profile views
#


@register_model_view(ACILeafInterfaceProfile)
class ACILeafInterfaceProfileView(generic.ObjectView):
    """Detail view for displaying a single object of Leaf Interface Profile."""

    queryset = ACILeafInterfaceProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        breadcrumbs=[
            Breadcrumb(
                "aci_fabric",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafinterfaceprofile_list",
                    "aci_fabric_id",
                ),
            ),
        ],
        left_panels=[
            ACILeafInterfaceProfilePanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
    )


@register_model_view(ACILeafInterfaceProfile, "list", path="", detail=False)
class ACILeafInterfaceProfileListView(generic.ObjectListView):
    """List view for listing all objects of ACI Leaf Interface Profile."""

    queryset = ACILeafInterfaceProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    filterset = ACILeafInterfaceProfileFilterSet
    filterset_form = ACILeafInterfaceProfileFilterForm
    table = ACILeafInterfaceProfileTable


@register_model_view(ACILeafInterfaceProfile, "add", detail=False)
@register_model_view(ACILeafInterfaceProfile, "edit")
class ACILeafInterfaceProfileEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Leaf Interface Profile."""

    queryset = ACILeafInterfaceProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACILeafInterfaceProfileEditForm


@register_model_view(ACILeafInterfaceProfile, "delete")
class ACILeafInterfaceProfileDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Leaf Interface Profile."""

    queryset = ACILeafInterfaceProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(
    ACILeafInterfaceProfile, "leafinterfaceselectors", path="selectors"
)
class ACILeafInterfaceProfileLeafInterfaceSelectorView(
    ACILeafInterfaceSelectorChildrenView
):
    """Children view of Leaf Interface Selectors of Leaf Interface Profile."""

    queryset = ACILeafInterfaceProfile.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACILeafInterfaceSelector",
            _("Add a Selector"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_fabric_id,
                "aci_leaf_interface_profile": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACILeafInterfaceSelectorChildrenView.actions

    def get_children(self, request, parent):
        """Return all Leaf Interface Selectors for the current Profile."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_leaf_interface_profile=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACILeafInterfaceProfile column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_leaf_interface_profile")
        return table


@register_model_view(
    ACILeafInterfaceProfile, "switchprofilebindings", path="switch-profiles"
)
class ACILeafInterfaceProfileSwitchProfileBindingsView(
    ACILeafSwitchProfileInterfaceBindingChildrenView
):
    """Children view of Profile Bindings of ACI Leaf Interface Profile."""

    queryset = ACILeafInterfaceProfile.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACILeafSwitchProfileInterfaceBinding",
            _("Attach a Switch Profile"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_fabric_id,
                "aci_leaf_interface_profile": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACILeafSwitchProfileInterfaceBindingChildrenView.actions
    tab = ViewTab(
        label=_("Switch Profiles"),
        badge=lambda obj: obj.aci_leaf_switch_profile_bindings.count(),
        permission="netbox_aci_plugin.view_acileafswitchprofileinterfacebinding",
        weight=1000,
    )

    def get_children(self, request, parent):
        """Return all children objects of the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_leaf_interface_profile=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACILeafInterfaceProfile column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_leaf_interface_profile")
        return table


@register_model_view(
    ACILeafInterfaceProfile, "bulk_import", path="import", detail=False
)
class ACILeafInterfaceProfileBulkImportView(generic.BulkImportView):
    """Bulk import view for importing ACI Leaf Interface Profile objects."""

    queryset = ACILeafInterfaceProfile.objects.all()
    model_form = ACILeafInterfaceProfileImportForm


@register_model_view(ACILeafInterfaceProfile, "bulk_edit", path="edit", detail=False)
class ACILeafInterfaceProfileBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing ACI Leaf Interface Profile objects."""

    queryset = ACILeafInterfaceProfile.objects.all()
    filterset = ACILeafInterfaceProfileFilterSet
    table = ACILeafInterfaceProfileTable
    form = ACILeafInterfaceProfileBulkEditForm


@register_model_view(
    ACILeafInterfaceProfile, "bulk_delete", path="delete", detail=False
)
class ACILeafInterfaceProfileBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting ACI Leaf Interface Profile objects."""

    queryset = ACILeafInterfaceProfile.objects.all()
    filterset = ACILeafInterfaceProfileFilterSet
    table = ACILeafInterfaceProfileTable


#
# Leaf Interface Selector views
#


@register_model_view(ACILeafInterfaceSelector)
class ACILeafInterfaceSelectorView(generic.ObjectView):
    """Detail view for a single object of ACI Leaf Interface Selector."""

    queryset = ACILeafInterfaceSelector.objects.select_related(
        "aci_leaf_interface_profile",
        "aci_leaf_interface_profile__aci_fabric",
        "aci_leaf_interface_policy_group",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        breadcrumbs=[
            Breadcrumb(
                "aci_fabric",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafinterfaceselector_list",
                    "aci_fabric_id",
                ),
            ),
            Breadcrumb(
                "aci_leaf_interface_profile",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafinterfaceselector_list",
                    "aci_leaf_interface_profile_id",
                ),
            ),
        ],
        left_panels=[
            ACILeafInterfaceSelectorPanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
    )


@register_model_view(ACILeafInterfaceSelector, "list", path="", detail=False)
class ACILeafInterfaceSelectorListView(generic.ObjectListView):
    """List view for listing all objects of ACI Leaf Interface Selector."""

    queryset = (
        ACILeafInterfaceSelector.objects.select_related(
            "aci_leaf_interface_profile",
            "aci_leaf_interface_profile__aci_fabric",
            "aci_leaf_interface_policy_group",
            "nb_tenant",
            "owner",
        )
        .annotate(
            aci_leaf_port_block_count=count_related(
                ACILeafPortBlock, "aci_leaf_interface_selector"
            )
        )
        .prefetch_related("tags")
    )
    filterset = ACILeafInterfaceSelectorFilterSet
    filterset_form = ACILeafInterfaceSelectorFilterForm
    table = ACILeafInterfaceSelectorTable


@register_model_view(ACILeafInterfaceSelector, "add", detail=False)
@register_model_view(ACILeafInterfaceSelector, "edit")
class ACILeafInterfaceSelectorEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Leaf Interface Selector."""

    queryset = ACILeafInterfaceSelector.objects.select_related(
        "aci_leaf_interface_profile",
        "aci_leaf_interface_profile__aci_fabric",
        "aci_leaf_interface_policy_group",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACILeafInterfaceSelectorEditForm


@register_model_view(ACILeafInterfaceSelector, "delete")
class ACILeafInterfaceSelectorDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Leaf Interface Selector."""

    queryset = ACILeafInterfaceSelector.objects.select_related(
        "aci_leaf_interface_profile",
        "aci_leaf_interface_profile__aci_fabric",
        "aci_leaf_interface_policy_group",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACILeafInterfaceSelector, "leafportblocks", path="port-blocks")
class ACILeafInterfaceSelectorLeafPortBlockView(ACILeafPortBlockChildrenView):
    """Children view of ACI Leaf Port Blocks of Leaf Interface Selector."""

    # The Profile and its Fabric are joined so the prefill below costs no
    # extra query.
    queryset = ACILeafInterfaceSelector.objects.select_related(
        "aci_leaf_interface_profile__aci_fabric"
    )
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACILeafPortBlock",
            _("Add a Port Block"),
            url_params={
                "aci_fabric": (
                    lambda ctx: ctx["object"].aci_leaf_interface_profile.aci_fabric_id
                ),
                "aci_leaf_interface_profile": (
                    lambda ctx: ctx["object"].aci_leaf_interface_profile_id
                ),
                "aci_leaf_interface_selector": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACILeafPortBlockChildrenView.actions

    def get_children(self, request, parent):
        """Return all Leaf Port Block objects for the current Selector."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_leaf_interface_selector=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACILeafInterfaceSelector column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_leaf_interface_selector")
        return table


@register_model_view(
    ACILeafInterfaceSelector, "bulk_import", path="import", detail=False
)
class ACILeafInterfaceSelectorBulkImportView(generic.BulkImportView):
    """Bulk import view for importing ACI Leaf Interface Selector objects."""

    queryset = ACILeafInterfaceSelector.objects.all()
    model_form = ACILeafInterfaceSelectorImportForm


@register_model_view(ACILeafInterfaceSelector, "bulk_edit", path="edit", detail=False)
class ACILeafInterfaceSelectorBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing ACI Leaf Interface Selector objects."""

    # The table's port block count is an annotation, so the confirmation
    # table renders a placeholder without it.
    queryset = ACILeafInterfaceSelector.objects.annotate(
        aci_leaf_port_block_count=count_related(
            ACILeafPortBlock, "aci_leaf_interface_selector"
        )
    )
    filterset = ACILeafInterfaceSelectorFilterSet
    table = ACILeafInterfaceSelectorTable
    form = ACILeafInterfaceSelectorBulkEditForm


@register_model_view(
    ACILeafInterfaceSelector, "bulk_delete", path="delete", detail=False
)
class ACILeafInterfaceSelectorBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting ACI Leaf Interface Selector objects."""

    # The table's port block count is an annotation, so the confirmation
    # table renders a placeholder without it.
    queryset = ACILeafInterfaceSelector.objects.annotate(
        aci_leaf_port_block_count=count_related(
            ACILeafPortBlock, "aci_leaf_interface_selector"
        )
    )
    filterset = ACILeafInterfaceSelectorFilterSet
    table = ACILeafInterfaceSelectorTable


#
# Leaf Port Block views
#


@register_model_view(ACILeafPortBlock)
class ACILeafPortBlockView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Leaf Port Block."""

    queryset = ACILeafPortBlock.objects.select_related(
        "aci_leaf_interface_selector",
        "aci_leaf_interface_selector__aci_leaf_interface_profile",
        "aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        breadcrumbs=[
            Breadcrumb(
                "aci_fabric",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafportblock_list",
                    "aci_fabric_id",
                ),
            ),
            Breadcrumb(
                lambda obj: obj.aci_leaf_interface_selector.aci_leaf_interface_profile,
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafportblock_list",
                    "aci_leaf_interface_profile_id",
                ),
            ),
            Breadcrumb(
                "aci_leaf_interface_selector",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafportblock_list",
                    "aci_leaf_interface_selector_id",
                ),
            ),
        ],
        left_panels=[
            ACILeafPortBlockPanel(),
            ACILeafPortBlockRangePanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
    )


@register_model_view(ACILeafPortBlock, "list", path="", detail=False)
class ACILeafPortBlockListView(generic.ObjectListView):
    """List view for listing all objects of ACI Leaf Port Block."""

    queryset = ACILeafPortBlock.objects.select_related(
        "aci_leaf_interface_selector",
        "aci_leaf_interface_selector__aci_leaf_interface_profile",
        "aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    filterset = ACILeafPortBlockFilterSet
    filterset_form = ACILeafPortBlockFilterForm
    table = ACILeafPortBlockTable


@register_model_view(ACILeafPortBlock, "add", detail=False)
@register_model_view(ACILeafPortBlock, "edit")
class ACILeafPortBlockEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Leaf Port Block."""

    queryset = ACILeafPortBlock.objects.select_related(
        "aci_leaf_interface_selector",
        "aci_leaf_interface_selector__aci_leaf_interface_profile",
        "aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACILeafPortBlockEditForm


@register_model_view(ACILeafPortBlock, "delete")
class ACILeafPortBlockDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Leaf Port Block."""

    queryset = ACILeafPortBlock.objects.select_related(
        "aci_leaf_interface_selector",
        "aci_leaf_interface_selector__aci_leaf_interface_profile",
        "aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACILeafPortBlock, "bulk_import", path="import", detail=False)
class ACILeafPortBlockBulkImportView(generic.BulkImportView):
    """Bulk import view for importing ACI Leaf Port Block objects."""

    queryset = ACILeafPortBlock.objects.all()
    model_form = ACILeafPortBlockImportForm


@register_model_view(ACILeafPortBlock, "bulk_edit", path="edit", detail=False)
class ACILeafPortBlockBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing ACI Leaf Port Block objects."""

    queryset = ACILeafPortBlock.objects.all()
    filterset = ACILeafPortBlockFilterSet
    table = ACILeafPortBlockTable
    form = ACILeafPortBlockBulkEditForm


@register_model_view(ACILeafPortBlock, "bulk_delete", path="delete", detail=False)
class ACILeafPortBlockBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting ACI Leaf Port Block objects."""

    queryset = ACILeafPortBlock.objects.all()
    filterset = ACILeafPortBlockFilterSet
    table = ACILeafPortBlockTable
