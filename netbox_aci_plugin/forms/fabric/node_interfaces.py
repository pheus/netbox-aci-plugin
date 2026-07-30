# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant, TenantGroup
from users.models import Owner, OwnerGroup
from utilities.forms.fields import (
    CommentField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ...choices import NodeRoleChoices
from ...constants import (
    ACI_DESC_MAX_LEN,
    NODE_INTERFACE_MODULE_MAX,
    NODE_INTERFACE_MODULE_MIN,
    NODE_INTERFACE_PORT_MAX,
    NODE_INTERFACE_PORT_MIN,
    NODE_INTERFACE_SUB_PORT_MAX,
    NODE_INTERFACE_SUB_PORT_NONE,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.node_interfaces import ACINodeInterface
from ...models.fabric.nodes import ACINode
from ...models.fabric.pods import ACIPod
from ...validators import parse_interface_name

#
# Node Interface forms
#


def _apply_blank_coordinate_default(
    form: forms.BaseForm, field_name: str, default: int
) -> None:
    """Set field_name in the form's cleaned_data to default when blank.

    Reads the raw submitted value through add_prefix() rather than
    cleaned_data, so a field the widget renders but the user (or CSV
    row) leaves blank is treated as blank instead of falling back to
    the model's own field default, which construct_instance() only
    preserves when the field's key is absent from the data entirely.
    """
    if not form.data.get(form.add_prefix(field_name)):
        form.cleaned_data[field_name] = default


class ACINodeInterfaceEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Node Interface model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_pods__aci_nodes": "$aci_node"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_pod = DynamicModelChoiceField(
        queryset=ACIPod.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={"aci_nodes": "$aci_node"},
        required=False,
        label=_("ACI Pod"),
    )
    aci_node = DynamicModelChoiceField(
        queryset=ACINode.objects.all(),
        query_params={
            "aci_pod_id": "$aci_pod",
            "role": NodeRoleChoices.ROLE_LEAF,
        },
        label=_("ACI Node"),
    )
    nb_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("NetBox device"),
        help_text=_("Narrows the NetBox interface picker to this device."),
    )
    nb_interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={"device_id": "$nb_device"},
        required=False,
        label=_("NetBox interface"),
        help_text=_(
            "Leaving Module, Port and Sub port blank derives them from "
            "this interface's name."
        ),
    )
    module = forms.IntegerField(
        required=False,
        label=_("Module"),
        help_text=_(
            "Module (slot) number of the interface. Left blank, it is "
            "derived from the NetBox interface name or defaults to 1."
        ),
    )
    port = forms.IntegerField(
        required=False,
        label=_("Port"),
        help_text=_(
            "Port number of the interface. Left blank, it is derived "
            "from the NetBox interface name."
        ),
    )
    sub_port = forms.IntegerField(
        required=False,
        label=_("Sub port"),
        help_text=_(
            "Breakout sub port number. Left blank, it is derived from "
            "the NetBox interface name or defaults to 0 (none)."
        ),
    )
    nb_tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        initial_params={"tenants": "$nb_tenant"},
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group"},
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group = DynamicModelChoiceField(
        queryset=OwnerGroup.objects.all(),
        initial_params={"members": "$owner"},
        null_option="None",
        required=False,
        label=_("Owner group"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        query_params={"group_id": "$owner_group"},
        label=_("Owner"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "aci_pod",
            "aci_node",
            "nb_device",
            "nb_interface",
            "module",
            "port",
            "sub_port",
            "description",
            "tags",
            name=_("ACI Node Interface"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACINodeInterface
        fields: tuple = (
            "aci_node",
            "nb_interface",
            "module",
            "port",
            "sub_port",
            "description",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI Node Interface form."""
        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        # Resolve the ACI Node from the edited object, or on the add
        # path from the parent the child-add button passes through
        aci_node = None
        if instance is not None and instance.aci_node_id:
            aci_node = instance.aci_node
        elif initial.get("aci_node"):
            try:
                aci_node = ACINode.objects.filter(pk=initial["aci_node"]).first()
            except (TypeError, ValueError):
                # A malformed query parameter seeds nothing
                aci_node = None

        if aci_node is not None and "nb_device" not in initial:
            # Seed the nb_device helper from the Node's cached device.
            # The attribute is "assigned_device", not "device": the
            # GenericRelations on ACINode already claim that name.
            node_device = aci_node.assigned_device
            if node_device is not None:
                initial["nb_device"] = node_device

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if self.instance.pk:
            # Coordinates are authoritative once an object exists. A
            # cleared field must fail cleanly instead of silently
            # falling back to the create-time interface-derived default.
            for field_name in ("module", "port", "sub_port"):
                self.fields[field_name].required = True
        else:
            # The add view builds its form with an unsaved instance, so
            # model_to_dict() seeds the widgets with the model's own
            # defaults. Blank them so the coordinates can be derived from
            # the interface name, but never blank one the caller supplied:
            # the clone workflow passes clone_fields in as initial.
            for field_name in ("module", "sub_port"):
                if field_name not in initial:
                    self.initial[field_name] = None

    def clean(self) -> None:
        """Validate form fields for the ACI Node Interface form."""
        super().clean()

        errors: dict[str, list] = {}

        self._validate_nb_device_consistency(errors)

        if not self.instance.pk:
            self._prefill_coordinates(errors)

        if errors:
            raise ValidationError(errors)

    def _validate_nb_device_consistency(self, errors: dict) -> None:
        """Validate the nb_device helper against the ACI Node's device.

        nb_device is derived, never a competing source of truth: it
        must agree with the selected ACI Node's cached device, and the
        Node's cached device is what actually narrows the interface
        picker.
        """
        aci_node = self.cleaned_data.get("aci_node")
        if aci_node is None:
            return

        nb_device = self.cleaned_data.get("nb_device")
        nb_interface = self.cleaned_data.get("nb_interface")
        node_device = aci_node.assigned_device

        if node_device is not None:
            if nb_device is not None and nb_device != node_device:
                errors.setdefault("nb_device", []).append(
                    _("The NetBox device must match the ACI Node's assigned device.")
                )
        elif nb_interface is not None:
            errors.setdefault("nb_interface", []).append(
                _(
                    "The ACI Node has no assigned NetBox device, so no "
                    "NetBox interface can be selected."
                )
            )

    def _prefill_coordinates(self, errors: dict) -> None:
        """Fill blank coordinate fields from the selected interface name.

        Reads the raw submitted values through add_prefix() rather
        than cleaned_data, so a coordinate the user left untouched is
        treated as blank instead of the value the widget happened to
        render.
        """
        nb_interface = self.cleaned_data.get("nb_interface")
        parsed = parse_interface_name(nb_interface.name) if nb_interface else None

        _apply_blank_coordinate_default(self, "module", parsed.module if parsed else 1)

        if not self.data.get(self.add_prefix("port")):
            if parsed:
                self.cleaned_data["port"] = parsed.port
            else:
                errors.setdefault("port", []).append(
                    _(
                        "The port is required when it cannot be derived "
                        "from a NetBox interface name."
                    )
                )

        _apply_blank_coordinate_default(
            self,
            "sub_port",
            parsed.sub_port
            if parsed and parsed.sub_port is not None
            else NODE_INTERFACE_SUB_PORT_NONE,
        )


class ACINodeInterfaceBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Node Interface model."""

    description = forms.CharField(
        max_length=ACI_DESC_MAX_LEN,
        required=False,
        label=_("Description"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACINodeInterface
    fieldsets: tuple = (
        FieldSet(
            "description",
            name=_("ACI Node Interface"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "nb_tenant",
    )


class ACINodeInterfaceFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Node Interface model."""

    model = ACINodeInterface
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "description",
            "aci_fabric_id",
            "aci_pod_id",
            "aci_node_id",
            "nb_interface_id",
            "module",
            "port",
            "sub_port",
            name=_("Attributes"),
        ),
        FieldSet(
            "nb_tenant_group_id",
            "nb_tenant_id",
            name=_("NetBox Tenancy"),
        ),
        FieldSet(
            "owner_group_id",
            "owner_id",
            name=_("Ownership"),
        ),
    )

    description = forms.CharField(
        required=False,
    )
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
    nb_interface_id = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_("NetBox interface"),
    )
    module = forms.IntegerField(
        required=False,
        label=_("Module"),
        min_value=NODE_INTERFACE_MODULE_MIN,
        max_value=NODE_INTERFACE_MODULE_MAX,
    )
    port = forms.IntegerField(
        required=False,
        label=_("Port"),
        min_value=NODE_INTERFACE_PORT_MIN,
        max_value=NODE_INTERFACE_PORT_MAX,
    )
    sub_port = forms.IntegerField(
        required=False,
        label=_("Sub port"),
        min_value=NODE_INTERFACE_SUB_PORT_NONE,
        max_value=NODE_INTERFACE_SUB_PORT_MAX,
    )
    nb_tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group_id"},
        null_option="None",
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("Owner Group"),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group_id"},
        null_option="None",
        required=False,
        label=_("Owner"),
    )
    tag = TagFilterField(model)


class ACINodeInterfaceImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Node Interface model."""

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
        help_text=_("ACI Node the Node Interface belongs to."),
    )
    nb_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox device"),
        help_text=_(
            "Must match the ACI Node's assigned device. Optional cross "
            "check, never stored."
        ),
    )
    nb_interface = CSVModelChoiceField(
        queryset=Interface.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox interface"),
        help_text=_(
            "NetBox interface backing this Node Interface. Resolved "
            "through the ACI Node's assigned device."
        ),
    )
    module = forms.IntegerField(
        required=False,
        label=_("Module"),
        help_text=_(
            "Module (slot) number of the interface. Left blank, defaults to 1."
        ),
    )
    sub_port = forms.IntegerField(
        required=False,
        label=_("Sub port"),
        help_text=_("Breakout sub port number. Left blank, defaults to 0 (none)."),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant."),
    )
    owner = CSVModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Name of the object's owner"),
    )

    class Meta:
        model = ACINodeInterface
        fields: tuple = (
            "aci_fabric",
            "aci_pod",
            "aci_node",
            "nb_device",
            "nb_interface",
            "module",
            "port",
            "sub_port",
            "description",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if self.instance.pk:
            # An absent CSV column must leave the stored coordinate
            # untouched. A present but blank cell must fail cleanly
            # instead of silently falling back to the create-time
            # default. The import view drops the fields of absent
            # columns only after __init__ returns, so requiring them
            # here never affects a column the row omitted.
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
                # Limit ACINode queryset by parent ACIFabric and ACIPod.
                # ACINode names are unique per Pod only, not per Fabric,
                # so both links are required to resolve the name without
                # ambiguity.
                self.fields["aci_node"].queryset = ACINode.objects.filter(
                    aci_pod__aci_fabric__name=data["aci_fabric"],
                    aci_pod__name=data["aci_pod"],
                )

        resolved_node = None
        if data.get("aci_node"):
            try:
                resolved_node = self.fields["aci_node"].to_python(data["aci_node"])
            except ValidationError:
                # The aci_node field repeats this same lookup during
                # its own cleaning and reports it there. Leave the
                # device-derived querysets untouched.
                resolved_node = None
        elif self.instance.pk:
            # A sparse update row may omit aci_node entirely. Fall
            # back to the stored Node so nb_device and nb_interface
            # still narrow correctly. aci_node is a non-nullable FK,
            # so a persisted instance always resolves it.
            resolved_node = self.instance.aci_node

        if resolved_node is not None:
            # Resolve nb_device and nb_interface through the Node's
            # cached device, not the CSV's raw nb_device value: device
            # and interface names repeat across sites and devices.
            node_device = resolved_node.assigned_device
            if node_device is not None:
                self.fields["nb_device"].queryset = Device.objects.filter(
                    pk=node_device.pk
                )
                self.fields["nb_interface"].queryset = Interface.objects.filter(
                    device_id=node_device.pk
                )
            else:
                # Device-less or VM-backed Node: no interface can match.
                self.fields["nb_device"].queryset = Device.objects.none()
                self.fields["nb_interface"].queryset = Interface.objects.none()

    def clean(self) -> None:
        """Apply the plain coordinate defaults a CSV row may omit.

        CSV import does not derive coordinates from the NetBox interface
        name, unlike the edit form: module and sub port fall back to the
        model's own defaults. Port stays required, since it has no
        default. Skipped on update, since an absent column must leave the
        stored coordinate untouched.
        """
        super().clean()

        errors: dict[str, list] = {}

        if not self.instance.pk:
            _apply_blank_coordinate_default(self, "module", 1)
            _apply_blank_coordinate_default(
                self, "sub_port", NODE_INTERFACE_SUB_PORT_NONE
            )

        self._validate_nb_interface_requires_device(errors)

        if errors:
            raise ValidationError(errors)

    def _validate_nb_interface_requires_device(self, errors: dict) -> None:
        """Reject nb_interface when the resolved Node has no device.

        Reads the raw value because a field rejected by the now empty
        interface queryset leaves nothing in cleaned_data. The field
        may carry a second message alongside its own resolution error.
        """
        aci_node = self.cleaned_data.get("aci_node")
        if aci_node is None or aci_node.assigned_device is not None:
            return

        if self.data.get(self.add_prefix("nb_interface")):
            errors.setdefault("nb_interface", []).append(
                _(
                    "The ACI Node has no assigned NetBox device, so no "
                    "NetBox interface can be selected."
                )
            )
