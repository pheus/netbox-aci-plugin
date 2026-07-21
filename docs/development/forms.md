# Forms

Forms live under `netbox_aci_plugin/forms/<domain>/<model>.py`. The
plugin ships **four forms per primary model**, all in the same file
per model. Every form uses `utilities.forms.rendering.FieldSet` to
organize fields into named groups.

## Four-form suite per primary model

- `<Model>EditForm` extends `NetBoxModelForm` and handles create/edit
  behavior. Most form logic lives here.
- `<Model>BulkEditForm` extends `NetBoxModelBulkEditForm` and declares
  the fields that make sense in bulk, plus `nullable_fields`.
- `<Model>FilterForm` extends `NetBoxModelFilterSetForm` and powers the
  list-view filter sidebar. It mirrors the FilterSet's fields.
- `<Model>ImportForm` extends `NetBoxModelImportForm` and handles CSV
  import. It uses `CSVChoiceField` / `CSVModelChoiceField` for foreign
  keys.

Even when a form has no domain-specific fields beyond the inherited
ones (e.g. a relation/binding's BulkEditForm), declare the class
anyway so the four-form suite stays uniform across models.

## Auto-rendered sections (Ownership, Tags, Comments)

NetBox's form templates auto-render certain sections. Declaring them
in `fieldsets` causes them to render **twice** in the browser.

The auto-rendered sections are:

- `NetBoxModelForm` / `htmx/form.html`: Ownership and Comments.
- `NetBoxModelBulkEditForm` / `generic/bulk_edit.html`: Ownership,
  Tags, and Comments.
- `NetBoxModelFilterSetForm`: no auto-rendered sections.

Rules:

- **EditForm**: declare domain-specific FieldSets plus `Tags` and
  `NetBox Tenancy`. Do **not** add an Ownership or Comments FieldSet.
- **BulkEditForm**: declare domain-specific FieldSets plus
  `NetBox Tenancy`. Do **not** add Ownership, Tags, or Comments
  FieldSets. Still list `comments` and `nb_tenant` in
  `nullable_fields` so the bulk-nullable checkboxes render.
- **FilterForm**: an explicit `Ownership` FieldSet **is** required (the
  filter template has no auto-rendered section). Use `owner_group_id` /
  `owner_id` field names.

Reference: NetBox core's `dcim/forms/model_forms.py` (SiteForm,
RackForm, etc.) follows the same pattern, with no explicit Ownership or
Comments FieldSets on EditForms.

## Field declaration order

### EditForm

Declare fields in this order (skip any not applicable):

1. Parent FK cascade (`aci_fabric`, `aci_tenant`, `aci_vrf`, ...)
2. Domain-specific / feature fields (`security_domains`, `target_dscp`, ...)
3. `nb_tenant_group`, `nb_tenant` (NetBox tenancy)
4. `owner_group`, `owner` (ownership)
5. `comments` (always last)

### BulkEditForm

1. Identity fields (`name_alias`, `description`)
2. Parent FK reparenting fields (`aci_fabric`, `aci_bridge_domain`, ...)
3. Domain-specific / feature fields
4. `nb_tenant` (NetBox tenancy)
5. `owner` (ownership)
6. `comments` (always last)

### FilterForm

Body structure (order of class-level attributes):

1. `model = <Model>`
2. `fieldsets: tuple = (...)`
3. Field declarations (`aci_fabric_id`, `name`, ...)
4. `tag = TagFilterField(model)` (always last field)

FilterForm fieldsets AND field declarations must use identity-first
order: `name`, `name_alias`, `description` first, then FK/scope
fields (`aci_fabric_id`, `aci_tenant_id`, etc.), then domain-specific
fields. Past that identity-first prefix, the class body follows the
model's own field order, while fieldsets are free to regroup the same
fields into function-based sections (e.g. "Policy Control Settings",
"Multicast Settings"). Body order and fieldset order are allowed to
diverge beyond the identity-first fields - don't reorder the body to
mirror the fieldsets.

## Choice fields: blank values belong to bulk edit and filtering

A `ChoiceField` on an EditForm that maps to a model field carrying a
default and `blank=False` stays required, which is the Django default,
so simply omit `required=False`. Marking it optional looks harmless but
lets an empty submitted value through: Django treats a present-but-empty
value as a real value rather than an omission, assigns `""` to the
instance, and then skips the field during model validation precisely
because the model forbids blanks while the form does not require one.
The result is a stored empty string that matches no choice, so detail
views and colour helpers render nothing. Omitting the field entirely is
still safe - the model default applies - which is why the ImportForm
keeps `required=False` and falls back through its
`_clean_field_default_*` helpers.

For the same reason an EditForm never wraps its choices in
`add_blank_choice()`. Where the ACI object model needs a neutral value,
the ChoiceSet already carries an explicit member for it (for example
`unspecified` on the QoS and DSCP sets); pair that member with
`initial=` instead of offering a blank entry that validation rejects.
The blank entry does belong on a BulkEditForm, where it means "leave
this field unchanged", and on a FilterForm, where it means "do not
filter on this field".

The one edit-form exception is a choice field paired with a
`<field>_custom` input, built with `add_custom_choice()` from
`choices.py`. There the trailing `None` entry is a working "custom"
sentinel rather than a placeholder: the user picks it, types a numeric
value into the paired field, and the form's `clean()` substitutes that
value. Those fields keep `required=False` because `clean()` relies on
the choice arriving empty. `ACIContractFilterEntryEditForm` is the only
current example.

`tests/forms/test_choice_field_conventions.py` enforces all of the
above by walking every edit form at runtime, so a new form cannot
reintroduce either mistake.

```python
# EditForm - required, no blank entry
target_dscp = forms.ChoiceField(
    choices=QualityOfServiceDSCPChoices,
    initial=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
    label=_("Target DSCP"),
)

# BulkEditForm - optional, blank means "leave unchanged"
target_dscp = forms.ChoiceField(
    choices=add_blank_choice(QualityOfServiceDSCPChoices),
    required=False,
    label=_("Target DSCP"),
)
```

### `Meta.fields` ordering (EditForm and ImportForm)

```python
class Meta:
    model = <Model>
    fields: tuple = (
        "name",
        "name_alias",
        "description",
        # parent FKs (aci_fabric, aci_tenant, aci_vrf, ...)
        # domain-specific / feature fields
        "nb_tenant",
        "owner",
        "comments",
        "tags",
    )
```

Identity fields first, parent FKs next, then domain-specific,
then `nb_tenant`, `owner`, `comments`, `tags` last.

## `FieldSet` fieldset organization

Every Edit, BulkEdit, and Filter form declares a `fieldsets` tuple of
`FieldSet(...)` calls, with **no raw `fields` list at the form level**
(Meta still has `fields`; this is about presentational grouping).
`ImportForm` never declares `fieldsets`: CSV import renders as a flat
column-mapped table, not a sectioned web form. Each `FieldSet` takes
positional field names and a `name=` kwarg holding the section
heading:

```python
from utilities.forms.rendering import FieldSet

class ACIBridgeDomainEditForm(NetBoxModelForm):
    # ... field declarations ...

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_fabric",
            "aci_tenant",
            "aci_vrf",
            "description",
            "tags",
            name=_("ACI Bridge Domain"),
        ),
        FieldSet(
            "unicast_routing_enabled",
            "advertise_host_routes_enabled",
            "ep_move_detection_enabled",
            "mac_address",
            "virtual_mac_address",
            name=_("Routing Settings"),
        ),
        # ...
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
```

The fieldset names are user-facing; wrap them with `_()`. Order
fieldsets by logical importance (identity, behavior, scoping,
tags/comments). The last fieldset is usually `NetBox Tenancy` (or
`Tags` / `Comments` for narrow forms).

## Cascading dropdowns

Use `DynamicModelChoiceField` from `utilities.forms.fields`. The two
mechanisms:

- `query_params`: server-side filter applied when the dropdown
  fetches options. References other form fields with `$<fieldname>`.
- `initial_params`: runs once on bind to look up an existing
  related-object value (for edit mode). Use a single key; multi-key
  `initial_params` behaves as AND and breaks when one side lives in
  `common`.

```python
aci_fabric = DynamicModelChoiceField(
    queryset=ACIFabric.objects.all(),
    initial_params={"aci_tenants": "$aci_tenant"},
    required=False,
    label=_("ACI Fabric"),
)
aci_tenant = DynamicModelChoiceField(
    queryset=ACITenant.objects.all(),
    query_params={"aci_fabric_id": "$aci_fabric"},
    label=_("ACI Tenant"),
)
aci_vrf = DynamicModelChoiceField(
    queryset=ACIVRF.objects.all(),
    query_params={
        "aci_fabric_id": "$aci_fabric",
        "present_in_aci_tenant_or_common_id": "$aci_tenant",
    },
    label=_("ACI VRF"),
)
```

### Tenant-or-common cascade

For dropdowns whose target might live in the special `common` tenant
(VRF, BD, Contract, ContractFilter, L3Out), use
`present_in_aci_tenant_or_common_id` in `query_params` rather than
`aci_tenant_id`. The target FilterSet must inherit
`ACITenantOrCommonFilterSetMixin` (see [FilterSets - Mixins
catalog](filtersets.md#mixins-catalog) and the
[`present_in_aci_tenant_or_common_id`](filtersets.md#present_in_aci_tenant_or_common_id)
filter section).

## Single-mental-model relation forms

When a relation/binding model links two equal-looking parents (e.g.
`ACIBridgeDomainL3OutBinding` links a BD and an L3Out), **pick one
parent as the form's mental model**. All scope helpers (`aci_fabric`,
`aci_tenant`, `aci_vrf`) derive from that side via single-key
`initial_params`. The other side is reached via URL-param injection
from its detail page button (see [Templates - Secondary-side
parent-scope injection](templates.md#secondary-side-parent-scope-injection)).

Reference example: `ACIBridgeDomainL3OutBindingEditForm` chooses
**BD** as the mental model:

```python
aci_fabric = DynamicModelChoiceField(
    queryset=ACIFabric.objects.all(),
    initial_params={"aci_tenants__aci_bridge_domains": "$aci_bridge_domain"},
    required=False,
    label=_("ACI Fabric"),
)
aci_tenant = DynamicModelChoiceField(
    queryset=ACITenant.objects.all(),
    query_params={"aci_fabric_id": "$aci_fabric"},
    initial_params={"aci_bridge_domains": "$aci_bridge_domain"},
    required=False,
    label=_("ACI Tenant"),
)
aci_vrf = DynamicModelChoiceField(
    queryset=ACIVRF.objects.all(),
    query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
    initial_params={"aci_bridge_domains": "$aci_bridge_domain"},
    required=False,
    label=_("ACI VRF"),
)
aci_bridge_domain = DynamicModelChoiceField(
    queryset=ACIBridgeDomain.objects.all(),
    query_params={"aci_tenant_id": "$aci_tenant", "aci_vrf_id": "$aci_vrf"},
    label=_("ACI Bridge Domain"),
)
aci_l3out = DynamicModelChoiceField(
    queryset=ACIL3Out.objects.all(),
    query_params={
        "present_in_aci_tenant_or_common_id": "$aci_tenant",
        "aci_vrf_id": "$aci_vrf",
    },
    label=_("ACI L3Out"),
)
```

All `initial_params` use the same key (`aci_bridge_domains` /
`aci_tenants__aci_bridge_domains`); they all derive from the BD side,
not the L3Out side.

## Custom `__init__`: only for runtime queryset/widget swap

The declarative `initial_params` / `query_params` pattern handles
almost everything. Reach for a custom `__init__` only when the
**queryset or widget itself** must change at runtime based on another
field's value.

Reference example: `ACIContractRelationEditForm.__init__` swaps
`aci_object.queryset` based on the chosen `aci_object_type`:

```python
def __init__(self, *args, **kwargs) -> None:
    """Initialize the ACI Contract Relation form."""
    instance = kwargs.get("instance")
    initial = kwargs.get("initial", {}).copy()

    if instance is not None and instance.aci_object:
        initial["aci_object"] = instance.aci_object
        initial["aci_tenant"] = instance.aci_object_tenant
        initial["aci_fabric"] = instance.aci_object_tenant.aci_fabric

    kwargs["initial"] = initial
    super().__init__(*args, **kwargs)

    if aci_object_type_id := get_field_value(self, "aci_object_type"):
        aci_object_type = ContentType.objects.get(pk=aci_object_type_id)
        aci_model = aci_object_type.model_class()
        self.fields["aci_object"].queryset = aci_model.objects.all()
        self.fields["aci_object"].widget.attrs["selector"] = (
            aci_model._meta.label_lower
        )
        # ...
```

Don't override `__init__` to do cascade work that `query_params` can
already express.

## CSV `ImportForm` queryset narrowing

CSV imports arrive with parent FK values as strings (names). The
`ImportForm.__init__` narrows child querysets based on what the
incoming row references, so a `CSVModelChoiceField` resolves to the
right object even when the same child name exists in multiple parents:

```python
def __init__(self, data=None, *args, **kwargs) -> None:
    """Extend import data processing with enhanced query sets."""
    super().__init__(data, *args, **kwargs)

    if not data:
        return

    if data.get("aci_fabric") and data.get("aci_tenant"):
        self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
            aci_fabric__name=data["aci_fabric"]
        )
        self.fields["aci_app_profile"].queryset = ACIAppProfile.objects.filter(
            aci_tenant__aci_fabric__name=data["aci_fabric"],
            aci_tenant__name=data["aci_tenant"],
        )
```

Pattern:

1. `super().__init__(data, ...)` first; the parent form sets up the
   declared fields.
2. Early-out on `if not data: return` (the bind-with-no-data case).
3. Narrow each `CSVModelChoiceField`'s `queryset` by traversing the
   chain of parent name fields present in `data`.

This isn't the same as the runtime-queryset-swap pattern above; CSV
narrowing operates on the *binding* data, not on the form's own field
values. Keep the two patterns separate.

## Form field kwarg ordering

Pass kwargs to a Django form field in this order. Skip any that
aren't needed:

```text
required
widget
label
initial
help_text
error_messages
show_hidden_initial
validators
localize
disabled
label_suffix
```

For NetBox's `DynamicModelChoiceField`, the order is:

```text
queryset
query_params
initial_params
null_option
disabled_indicator
context
selector
**kwargs
```
