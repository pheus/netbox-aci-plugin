# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from utilities.forms.fields import (
    CommentField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ...choices import LeafInterfacePolicyGroupTypeChoices, NodeRoleChoices
from ...constants import ACI_DESC_MAX_LEN, NODE_INTERFACE_SUB_PORT_NONE
from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ...models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.node_interfaces import ACINodeInterface
from ...models.fabric.nodes import ACINode
from ...models.fabric.pods import ACIPod

#
# Leaf Interface Override forms
#


class ACILeafInterfaceOverrideEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Leaf Interface Override model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_pods__aci_nodes__aci_node_interfaces": "$aci_node_interface"
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_pod = DynamicModelChoiceField(
        queryset=ACIPod.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={"aci_nodes__aci_node_interfaces": "$aci_node_interface"},
        required=False,
        label=_("ACI Pod"),
    )
    aci_node = DynamicModelChoiceField(
        queryset=ACINode.objects.all(),
        query_params={
            "aci_pod_id": "$aci_pod",
            "role": NodeRoleChoices.ROLE_LEAF,
        },
        initial_params={"aci_node_interfaces": "$aci_node_interface"},
        required=False,
        label=_("ACI Node"),
    )
    aci_node_interface = DynamicModelChoiceField(
        queryset=ACINodeInterface.objects.all(),
        query_params={"aci_node_id": "$aci_node"},
        label=_("ACI Node Interface"),
    )
    aci_leaf_interface_policy_group = DynamicModelChoiceField(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        },
        label=_("ACI Leaf Interface Policy Group"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "aci_pod",
            "aci_node",
            "aci_node_interface",
            "aci_leaf_interface_policy_group",
            "description",
            "tags",
            name=_("ACI Leaf Interface Override"),
        ),
    )

    class Meta:
        model = ACILeafInterfaceOverride
        fields: tuple = (
            "aci_node_interface",
            "aci_leaf_interface_policy_group",
            "description",
            "comments",
            "tags",
        )


class ACILeafInterfaceOverrideBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Leaf Interface Override model."""

    description = forms.CharField(
        max_length=ACI_DESC_MAX_LEN,
        required=False,
        label=_("Description"),
    )
    aci_leaf_interface_policy_group = DynamicModelChoiceField(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Policy Group"),
    )
    comments = CommentField()

    model = ACILeafInterfaceOverride
    fieldsets: tuple = (
        FieldSet(
            "aci_leaf_interface_policy_group",
            "description",
            name=_("ACI Leaf Interface Override"),
        ),
    )
    nullable_fields: tuple = ("comments", "description")


class ACILeafInterfaceOverrideFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Leaf Interface Override model."""

    model = ACILeafInterfaceOverride
    fieldsets: tuple = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "description",
            "aci_fabric_id",
            "aci_pod_id",
            "aci_node_id",
            "aci_node_interface_id",
            "aci_leaf_interface_policy_group_id",
            name=_("Attributes"),
        ),
    )

    description = forms.CharField(
        required=False,
    )
    # Top-level Fabric, Pod, Node and Node Interface stay flat with each
    # other, matching ACINodeInterfaceFilterForm one hop shallower.
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_pod_id = DynamicModelMultipleChoiceField(
        queryset=ACIPod.objects.all(),
        required=False,
        label=_("ACI Pod"),
    )
    aci_node_id = DynamicModelMultipleChoiceField(
        queryset=ACINode.objects.all(),
        required=False,
        label=_("ACI Node"),
    )
    aci_node_interface_id = DynamicModelMultipleChoiceField(
        queryset=ACINodeInterface.objects.all(),
        required=False,
        label=_("ACI Node Interface"),
    )
    aci_leaf_interface_policy_group_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Policy Group"),
    )
    tag = TagFilterField(model)


class ACILeafInterfaceOverrideImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Leaf Interface Override model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of the ACI Node."),
    )
    aci_pod = CSVModelChoiceField(
        queryset=ACIPod.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Pod"),
        help_text=_("Parent ACI Pod of the ACI Node."),
    )
    aci_node = CSVModelChoiceField(
        queryset=ACINode.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Node"),
        help_text=_("ACI Node the overridden ACI Node Interface belongs to."),
    )
    module = forms.IntegerField(
        required=False,
        label=_("Module"),
        help_text=_(
            "Module (slot) number of the ACI Node Interface. Left blank, defaults to 1."
        ),
    )
    port = forms.IntegerField(
        required=True,
        label=_("Port"),
        help_text=_("Port number of the ACI Node Interface."),
    )
    sub_port = forms.IntegerField(
        required=False,
        label=_("Sub port"),
        help_text=_(
            "Breakout sub port number of the ACI Node Interface. Left "
            "blank, defaults to 0 (none)."
        ),
    )
    aci_leaf_interface_policy_group = CSVModelChoiceField(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Interface Policy Group"),
        help_text=_("Assigned ACI Leaf Interface Policy Group."),
    )

    class Meta:
        model = ACILeafInterfaceOverride
        fields: tuple = (
            "aci_fabric",
            "aci_pod",
            "aci_node",
            "module",
            "port",
            "sub_port",
            "aci_leaf_interface_policy_group",
            "description",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if self.instance.pk:
            # On update a present but blank coordinate must fail cleanly
            # rather than fall back to the create-time default and
            # silently re-point the Override at another port. The import
            # view drops the fields of absent columns only after
            # __init__ returns, so a row that omits them is unaffected.
            for field_name in ("module", "sub_port"):
                self.fields[field_name].required = True

        if not data:
            return

        if data.get("aci_fabric"):
            # A Fabric alone is enough to narrow the candidate Pods.
            self.fields["aci_pod"].queryset = ACIPod.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            if data.get("aci_pod") and data.get("aci_node"):
                # ACINode names are unique per Pod only, not per Fabric,
                # so both links are required to resolve the name without
                # ambiguity.
                self.fields["aci_node"].queryset = ACINode.objects.filter(
                    aci_pod__aci_fabric__name=data["aci_fabric"],
                    aci_pod__name=data["aci_pod"],
                )
        elif data.get("aci_pod") and self.instance.pk:
            # A sparse update row may omit aci_fabric entirely
            stored_pod = self.instance.aci_node_interface.aci_node.aci_pod
            self.fields["aci_pod"].queryset = ACIPod.objects.filter(
                aci_fabric_id=stored_pod.aci_fabric_id
            )

    def clean(self) -> None:
        """Resolve the ACI Node Interface from the submitted coordinates.

        aci_node_interface is not a form field, so Django excludes it
        from both the model's NOT NULL check and its OneToOneField
        uniqueness check. All three are enforced here instead, or a bad
        row would surface as a raw IntegrityError rather than a clean
        row-level form error.
        """
        super().clean()

        errors: dict[str, list] = {}

        coordinate_fields = ("aci_node", "module", "port", "sub_port")
        if self.instance.pk:
            # The import view deletes the fields of absent columns, so a
            # partial set saves unchanged while the row reports as updated.
            missing = [f for f in coordinate_fields if f not in self.fields]
            if 0 < len(missing) < len(coordinate_fields):
                errors.setdefault(NON_FIELD_ERRORS, []).append(
                    _(
                        "Re-pointing an Override requires every coordinate "
                        "column. Missing: {fields}."
                    ).format(fields=", ".join(missing))
                )
        else:
            if not self.data.get(self.add_prefix("module")):
                self.cleaned_data["module"] = 1
            if not self.data.get(self.add_prefix("sub_port")):
                self.cleaned_data["sub_port"] = NODE_INTERFACE_SUB_PORT_NONE

        aci_node = self.cleaned_data.get("aci_node")
        module = self.cleaned_data.get("module")
        port = self.cleaned_data.get("port")
        sub_port = self.cleaned_data.get("sub_port")

        # A coordinate that failed its own validation is absent from
        # cleaned_data and already carries its own error
        if None not in (aci_node, module, port, sub_port):
            try:
                aci_node_interface = ACINodeInterface.objects.get(
                    aci_node=aci_node,
                    module=module,
                    port=port,
                    sub_port=sub_port,
                )
            except ACINodeInterface.DoesNotExist:
                errors.setdefault("port", []).append(
                    _("No ACI Node Interface matches these coordinates.")
                )
            else:
                duplicate_overrides = ACILeafInterfaceOverride.objects.filter(
                    aci_node_interface=aci_node_interface
                )
                if self.instance.pk:
                    duplicate_overrides = duplicate_overrides.exclude(
                        pk=self.instance.pk
                    )
                if duplicate_overrides.exists():
                    errors.setdefault("port", []).append(
                        _("This ACI Node Interface already has an Override.")
                    )
                else:
                    self.instance.aci_node_interface = aci_node_interface

        if errors:
            raise ValidationError(errors)
