# Models

Models live under `netbox_aci_plugin/models/<domain>/<model>.py`. The
plugin layers concrete models on top of intermediate abstract bases,
almost all rooted at `ACIBaseModel(OwnerMixin, NetBoxModel)` in
`models/base.py`. The exception is `ACIFabric`, which extends
`NetBoxModel` directly (bypassing `ACIBaseModel`) and omits the
`name_alias` field. Shared model behavior, primarily the GFK uniqueness
helper, lives in `models/mixins.py`.

This is the longest layer doc. Use the table of contents to jump:

- [ACI source-of-truth validation](#aci-source-of-truth-validation)
- [Class hierarchy](#class-hierarchy)
- [Member ordering](#member-ordering)
- [Field ordering](#field-ordering)
- [`class Meta`](#class-meta)
- [`UniqueConstraint` naming template](#uniqueconstraint-naming-template)
- [Conditional `UniqueConstraint`](#conditional-uniqueconstraint)
- [`clone_fields` and `prerequisite_models`](#clone_fields-and-prerequisite_models)
- [Hierarchy navigation](#hierarchy-navigation)
- [Choice color helpers](#choice-color-helpers)
- [`clean()`](#clean)
- [`to_objectchange()`](#to_objectchange)
- [`save()` and `alters_data`](#save-and-alters_data)
- [Foreign key `on_delete`](#foreign-key-on_delete)
- [Denormalized FK caching](#denormalized-fk-caching)
- [Generic Foreign Key pattern](#generic-foreign-key-pattern)
- [`OwnerMixin` coverage](#ownermixin-coverage)
- [Relation / Binding models](#relation--binding-models)
- [`CachedScopeMixin`](#cachedscopemixin)
- [Choices](#choices)
- [ACI concept casing in prose](#aci-concept-casing-in-prose)
- [Model field kwarg ordering](#model-field-kwarg-ordering)

## ACI source-of-truth validation

Before writing or modifying any model field, validate the field set
against both authoritative ACI sources. This is a per-model,
every-time requirement - not a one-off review.

### Cisco NaC APIC data model (coverage)

The Cisco Network as Code (NaC) APIC data model documents the curated
field set for each ACI MO as used in NaC-based automation. Use it to
confirm that the plugin model covers every field an operator would
configure and that no relevant attribute is omitted without reason.

Source: <https://netascode.cisco.com/docs/data_models/apic/>

Find the matching NaC object (e.g. `aaep` for
`ACIAttachableAccessEntityProfile`, `bridge_domain` for
`ACIBridgeDomain`) and walk through its attributes. Every NaC attribute
should map to a plugin field or carry a documented reason for omission.

### Cisco APIC MIM reference (attribute detail)

The APIC Managed Information Model (MIM) reference specifies the exact
attribute constraints for each APIC MO class. Use it to set
`max_length`, `validators`, `default`, `choices`, and `blank`/`null`
correctly for each field.

Source pattern:
`https://pubhub.devnetcloud.com/media/apic-mim-ref-<version>/docs/MO-<moClass>.html`

Replace `<version>` with the APIC release being targeted and
`<moClass>` with the MO class name. Examples:

- `ACIAttachableAccessEntityProfile` (`infraAttEntityP`):
  `https://pubhub.devnetcloud.com/media/apic-mim-ref-421e/docs/MO-infraAttEntityP.html`
- `ACIBridgeDomain` (`fvBD`):
  `https://pubhub.devnetcloud.com/media/apic-mim-ref-421e/docs/MO-fvBD.html`

For each MO attribute, check:

- **Name and alias constraints:** max length and allowed characters set
  `max_length` and `validators` on the corresponding model field.
- **Enumerated values:** map each to a constant in a `ChoiceSet` in
  `choices.py` (see [Choices](#choices)) and add `# default "<value>"`
  above the default member.
- **Default value:** use as the field `default` kwarg.
- **Optionality:** attributes the MIM marks as optional map to
  `blank=True, null=True`; mandatory attributes map to a required field
  with no `blank=True`.

## Class hierarchy

```text
NetBoxModel  (upstream)
  ├─ ACIFabric  (models/fabric/fabrics.py, no ACIBaseModel)
  └─ ACIBaseModel(OwnerMixin, NetBoxModel)  (models/base.py)
      ├─ ACIFabricBaseModel  (models/base.py)
      │   ├─ ACIPod  (concrete)
      │   ├─ ACINode  (concrete)
      │   └─ ACIDomainBaseModel  (models/access_policies/domains.py)
      │       ├─ ACIRoutedDomain  (concrete)
      │       └─ ACIPhysicalDomain  (concrete)
      └─ ACITenantBaseModel  (models/base.py)
          ├─ ACIEndpointGroupBaseModel  (models/tenant/endpoint_groups.py)
          │   ├─ ACIEndpointGroup  (concrete)
          │   └─ ACIUSegEndpointGroup  (concrete)
          ├─ ACIUSegAttributeBaseModel  (models/tenant/endpoint_groups.py)
          │   └─ ACIUSegNetworkAttribute  (concrete)
          └─ <many other concrete tenant-scoped models>
```

Pick the **closest** abstract ancestor when defining a new model:

- A fabric-scoped policy (Routed Domain, Pod, Node): subclass
  `ACIFabricBaseModel`.
- A tenant-scoped policy (VRF, BD, App Profile, Contract): subclass
  `ACITenantBaseModel`.
- An EPG-like model: subclass `ACIEndpointGroupBaseModel`.
- A join or relation model with no `name` of its own: extend
  `NetBoxModel` directly (see [Relation / Binding
  models](#relation--binding-models)).

`ACIBaseModel` contributes the universal text fields (`name`,
`name_alias`, `description`), `nb_tenant`, `comments`, the
`OwnerMixin` fields, and a base `clone_fields` tuple.

## Member ordering

Inside a model class, order members like this:

```text
database fields
custom manager attributes
class Meta
__str__()
clean_fields()
clean()
save()
delete()
get_absolute_url()
to_objectchange()
@property definitions
custom methods
```

`clean_fields()` precedes `clean()` because Django calls them in that
order during full validation (`clean_fields` -> `clean` ->
`validate_unique`). Only override `clean_fields()` when you need to
mutate field values before Django's built-in required/type checks run
(e.g. `ACIExternalSubnet.clean_fields()` syncs `matched_prefix` from
`nb_prefix` before the required-field check fires).

`__str__()` is display-only. Several ACI models carry a `name` that is
unique only within a narrower scope than the string alone suggests, for
example `ACILeafInterfacePolicyGroup`, whose name is namespaced by group
type in APIC (an access group and a bundle group may share a name). Never
resolve a relation, an import row, or a form lookup by parsing or matching
`__str__()`'s output. Use the model's actual scoped fields instead.

## Field ordering

Place these fields **last** in every model, in this order, after any
domain-specific fields:

```text
nb_tenant
tags
comments
```

`nb_tenant`, `comments`, and the `OwnerMixin` fields are inherited
from `ACIBaseModel`; don't redeclare them in subclasses unless you
need to override behavior.

## `class Meta`

Annotate types and wrap user-facing strings with `_()`:

```python
class Meta:
    constraints: list[models.UniqueConstraint] = [...]
    ordering: tuple = ("aci_fabric", "name")
    verbose_name: str = _("ACI Tenant")
```

## `UniqueConstraint` naming template

Use the `%(app_label)s_%(class)s_...` template for portability: the
template renders to a stable name and inherits cleanly into
subclasses:

```python
models.UniqueConstraint(
    fields=("aci_fabric", "name"),
    name="%(app_label)s_%(class)s_unique_name_per_aci_fabric",
)
```

Migrations referencing constraints by name use the rendered form
(e.g. `netbox_aci_plugin_acitenant_unique_name`).

PostgreSQL truncates identifiers past 63 bytes rather than rejecting
them, on creation and on every later lookup alike, so a long rendered
name stays valid. Django checks name length only for auto-generated
column names and for `Index`, never for `UniqueConstraint`. Many shipped
constraint names already run past the limit. Treat it as a readability
concern rather than a validity one: prefer a name that survives
untruncated, so the rendered form in a migration still reads as the
constraint it names.

Two traps when measuring rendered lengths. Grepping for a rendered name
finds nothing, because what the source stores is the template. And
slicing a model module with a `^class` regex silently drops constraints,
while walking every `ClassDef` double counts them, since the nested
`Meta` is a class too. Only an AST walk restricted to the outer class's
`Meta` gives the right answer.

## Conditional `UniqueConstraint`

When the constraint should only apply under a condition, use
`condition=models.Q(...)` paired with `violation_error_message=_("...")`
for user-readable validation feedback at the database level:

```python
models.UniqueConstraint(
    fields=(
        "aci_useg_endpoint_group",
        "use_epg_subnet",
    ),
    name=(
        "%(app_label)s_%(class)s_unique_use_epg_subnet_"
        "per_useg_endpoint_group"
    ),
    condition=models.Q(use_epg_subnet=True),
    violation_error_message=_(
        "ACI uSeg Endpoint Group with a 'use EPG Subnet' "
        "attribute already exists."
    ),
),
```

Good examples: `ACIBridgeDomainSubnet` (`bridge_domains.py`) and
`ACINode` (`nodes.py`).

## `clone_fields` and `prerequisite_models`

Every concrete model carries both - declared directly or inherited from
its abstract base (for example, `ACIEndpointGroupBaseModel` in
`endpoint_groups.py` declares `prerequisite_models` for all its
subclasses, and `ACIDomainBaseModel` in `access_policies/domains.py`
declares `clone_fields`). The one exception is `ACIFabric`: as the
root of the fabric hierarchy it has no `prerequisite_models`.

```python
clone_fields: tuple = ACITenantBaseModel.clone_fields + (
    "aci_tenant",
    "qos_class",
)
prerequisite_models: tuple = ("netbox_aci_plugin.ACITenant",)
```

Inherit from the parent's `clone_fields` rather than restating its
entries; drift accumulates fast when bases evolve.

## Hierarchy navigation

Every concrete model exposes a `parent_object` `@property` and any
useful cross-tier shortcuts:

```python
@property
def aci_fabric(self) -> ACIFabric:
    return self.aci_tenant.aci_fabric

@property
def parent_object(self) -> ACITenant:
    return self.aci_tenant
```

`parent_object` is what `to_objectchange()` and the URL/breadcrumb
machinery consult for the "what owns this?" relationship.
`ACITenantBaseModel` already provides `aci_fabric` via
`self.aci_tenant.aci_fabric`, so tenant-scoped models inherit it for free.

Which owner shortcuts a model exposes follows its place in the ACI hierarchy. A
tenant-scoped object can reach both its tenant and its fabric, so it exposes
`aci_tenant` and `aci_fabric`. A fabric-scoped or access-policy object sits
outside any tenant, so it exposes only `aci_fabric`.

An association model reaches its owners through the objects it links, and names
each shortcut after the owner it actually reaches. Reaching a single tenant, it
exposes `aci_tenant`. Able to reach two different tenants, it names each one, as
`ACIContractRelation` does with `aci_contract_tenant` and `aci_object_tenant`.
The fabric follows the same idea, and an association whose sides are both
access-policy objects has no tenant to expose.

Keep the declaration order stable: the owner and cross-tier shortcuts come
first, `parent_object` after them, and any computed value property last. An
association model lists its owner shortcuts in hierarchy order, outermost owner
first. A computed property, such as an `effective_*` encapsulation resolver or
`ACIExternalSubnet`'s `prefix_source`, returns a derived value rather than a
related object, so it belongs after the owner shortcuts and `parent_object`,
never interleaved among them.

## Choice color helpers

For every `ChoiceSet`-backed field, declare a
`get_<field>_color()` method that proxies to the ChoiceSet's color
map:

```python
def get_qos_class_color(self) -> str:
    """Return the associated color of choice from the ChoiceSet."""
    return QualityOfServiceClassChoices.colors.get(self.qos_class)
```

Tables and templates consume `get_<field>_color()` to render colored
badges (see [Tables - `ChoiceFieldColumn`](tables.md#column-type-catalog)
and [Templates - Cell helpers](templates.md#cell-helpers)).

## `clean()`

Default rule: call `super().clean()` first and accumulate **all**
field-keyed errors into a dict before raising once. Never raise on the
first error:

```python
def clean(self) -> None:
    super().clean()
    errors = {}
    if condition1:
        errors.setdefault("field1", []).append(_("message"))
    if condition2:
        errors.setdefault("field2", []).append(_("message"))
    if errors:
        raise ValidationError(errors)
```

This lets the form layer show every error at once, rather than
surfacing one error, then another only after the user resubmits.

**GFK early-guard exception:** GFK-bearing models may raise a field-keyed
`ValidationError` before `super().clean()` when a `*_type` FK is set but
its companion object ID is absent. This prevents Django's built-in
validation from choking on a partially populated GFK pair. After that
guard, still call `super().clean()` and accumulate the remaining
validation errors as above. See `ACIContractRelation.clean()`
(`contracts.py`), `ACIUSegNetworkAttribute.clean()`
(`endpoint_groups.py`), `ACINode.clean()` (`nodes.py`), the two
`ACIEsgEndpoint*Selector.clean()` methods (`endpoint_security_groups.py`),
and `ACIAAEPDomainBinding.clean()` (`aaep.py`) for examples.

**Parent-FK `_id` guard:** before dereferencing any parent relation inside
`clean()` (e.g. `self.aci_tenant.aci_fabric_id`), guard on the FK's `_id`
attname rather than the relation attribute itself (`if self.aci_vrf_id and
self.aci_tenant_id:`). A partial form submit can leave a required FK
unset, and dereferencing it directly raises `RelatedObjectDoesNotExist`,
surfacing as an HTTP 500 during `full_clean()` instead of a validation
error. See `ACIL3Out.clean()` (`l3outs.py`),
`ACIEndpointGroupBaseModel.clean()` (`endpoint_groups.py`), and
`ACIEndpointSecurityGroup.clean()` (`endpoint_security_groups.py`) for
examples.

## `to_objectchange()`

Set `related_object` so the audit log links the change to the
parent's history page:

```python
def to_objectchange(self, action) -> ObjectChange:
    objectchange = super().to_objectchange(action)
    objectchange.related_object = self.aci_contract
    return objectchange
```

Pick the parent that makes the most sense for an audit reader (often
the same object as `parent_object`).

## `save()` and `alters_data`

When the save path runs side-effecting helpers (e.g. denormalized FK
caching), mark each helper with `alters_data` so Django's template
engine refuses to call them implicitly:

```python
def save(self, *args, **kwargs) -> None:
    self.cache_related_objects()
    super().save(*args, **kwargs)

def cache_related_objects(self) -> None:
    ...

cache_related_objects.alters_data = True
```

## Foreign key `on_delete`

What a foreign key passes to `on_delete` follows from what it points
at, not from whatever a nearby field happens to use. Four patterns cover
every public foreign key in the plugin:

- **Anchoring ACI parent:** `PROTECT`. An ACI Fabric, ACI Tenant, ACI
  Pod, ACI Node, ACI Application Profile, ACI VRF, ACI Bridge Domain,
  ACI Domain or ACI VLAN Pool anchors everything beneath it, so
  deleting one must never silently take its children with it.
- **Child, join or binding row:** `CASCADE`. A child that is pure
  configuration of its parent has no meaning without that parent, and
  neither has either side of a join, relation or binding row.
- **Optional NetBox object:** `SET_NULL`. This covers `nb_tenant`,
  `nb_vrf`, `nb_vlan`, `nb_interface`, `tep_ip_address` and
  `infra_vlan`.
- **`ContentType` or generic foreign key plumbing:** `PROTECT`.

The `SET_NULL` pattern exists so the plugin never blocks deletion of an
object it does not own. That reasoning does not carry across to an
ACI-to-ACI reference, where both sides are plugin-owned, so `SET_NULL`
is the wrong default there.

This section covers public foreign keys. The `_`-prefixed fields in
[Denormalized FK caching](#denormalized-fk-caching) are a different
mechanism and are uniformly `CASCADE`, and the `_region` and
`_site_group` fields contributed by
[`CachedScopeMixin`](#cachedscopemixin) are `SET_NULL` by NetBox's own
design. Both stay consistent with the four patterns once cache fields
are read as sitting outside them.

### Nullability is a separate decision

`null=True` answers whether the relation may be absent. `on_delete`
answers what happens to this row when the target is deleted. Decide the
two independently.

Nullable plus `PROTECT` is the established pairing for an optional
pointer whose silent removal would be a destructive change. `SET_NULL`
on such a field strips the reference from every row that used it, and
leaves no record that anything was ever configured. The `OwnerMixin`
`owner` field uses the same nullable `PROTECT` pairing (see
[Migrations](migrations.md)).

### Read the whole tree, not one nearby field

Two declarations mislead anyone who samples instead of enumerating:

- `aci_vlan_pool` is declared twice with different semantics.
  `ACIDomainBaseModel` declares it optional on `SET_NULL`, and
  `ACIPhysicalDomain` overrides it as required on `PROTECT`. Only
  `ACIRoutedDomain` inherits the optional form, which makes the field a
  `PROTECT` precedent rather than a `SET_NULL` one.
- `ACILeafInterfacePolicyGroup.aci_aaep` is the only genuine optional
  ACI-to-ACI reference on `SET_NULL`, and it was chosen for nullability
  reasons rather than for delete semantics. One case is not a
  convention.

One field sits outside the four patterns.
`ACIBridgeDomainSubnet.gateway_ip_address` is a required one-to-one link
to a NetBox IP Address on `CASCADE`. It does not contradict the
`SET_NULL` pattern, which covers optional links only.

## Denormalized FK caching

GFK-bearing models (`ACIContractRelation`, `ACIUSegNetworkAttribute`,
`ACINode`, `ACIEsgEndpointGroupSelector`, `ACIEsgEndpointSelector`,
`ACIAAEPDomainBinding`) cache each possible concrete target in an
`_`-prefixed FK field. The cache lets search, filter ordering, and table
querysets use concrete FK fields instead of traversing the GFK at query
time:

```python
# Cached related objects by association name for faster access
_aci_endpoint_group = models.ForeignKey(
    to="netbox_aci_plugin.ACIEndpointGroup",
    on_delete=models.CASCADE,
    related_name="_aci_contract_relations",
    verbose_name=_("ACI Endpoint Group"),
    blank=True,
    null=True,
)
_aci_endpoint_security_group = models.ForeignKey(
    to="netbox_aci_plugin.ACIEndpointSecurityGroup",
    # ...
)
_aci_useg_endpoint_group = models.ForeignKey(...)
_aci_external_endpoint_group = models.ForeignKey(...)
_aci_vrf = models.ForeignKey(...)
```

Rules:

- One `_`-prefixed FK per possible target type.
- `on_delete=models.CASCADE`, `blank=True, null=True`.
- `related_name` uses the same `_<relation_name>` shape on each
  target (`_aci_contract_relations`).
- Populated from `save()` via a `cache_related_objects()` helper
  marked with `alters_data` (see [`save()` and
  `alters_data`](#save-and-alters_data)).
- Excluded from GraphQL types via `exclude=[...]` (see [GraphQL -
  Types](graphql-api.md#types)).
- Referenced by name in `search.py` weight tuples when the related
  object should be searchable (see [Search - Denormalized FK
  fields](search.md#denormalized-fk-fields-in-weight-tuples)).

## Generic Foreign Key pattern

Three parts, in this order:

### 1. Content-type filter in `constants.py`

```python
CONTRACT_RELATION_OBJECT_TYPES = Q(
    app_label="netbox_aci_plugin",
    model__in=(
        "aciendpointgroup",
        "aciendpointsecuritygroup",
        "aciexternalendpointgroup",
        "aciusegendpointgroup",
        "acivrf",
    ),
)
```

See [Validators & Constants - Q-object content-type
filters](validators.md#q-object-content-type-filters) for naming.

### 2. GFK trio on the model

The mandatory suffix is `<name>_type` (Django's content-type FK),
plus the companion `<name>_id` and the `<name> = GenericForeignKey(...)`.
NetBox-style (`scope_type`/`scope_id`/`scope`) and ACI-style
(`aci_object_type`/`aci_object_id`/`aci_object`) are both acceptable;
the hard requirement is the `_type` suffix:

```python
aci_object_type = models.ForeignKey(
    to="contenttypes.ContentType",
    on_delete=models.PROTECT,
    related_name="+",
    limit_choices_to=CONTRACT_RELATION_OBJECT_TYPES,
)
aci_object_id = models.PositiveBigIntegerField()
aci_object = GenericForeignKey(
    ct_field="aci_object_type",
    fk_field="aci_object_id",
)
```

### 3. `UniqueGenericForeignKeyMixin`

Apply `UniqueGenericForeignKeyMixin` from `models/mixins.py` and
declare `generic_fk_field` + `generic_unique_fields`. Call
`self._validate_generic_uniqueness()` from `clean()`:

```python
class ACIContractRelation(NetBoxModel, UniqueGenericForeignKeyMixin):
    generic_fk_field: str = "aci_object"
    generic_unique_fields: tuple[str] = ("aci_contract", "role")

    def clean(self) -> None:
        super().clean()
        self._validate_generic_uniqueness()
        # ...
```

The mixin raises a `ValidationError` with the verbose names of the
conflicting target model + the additional unique fields.

## `OwnerMixin` coverage

`OwnerMixin` is the user-attribution mixin from `users.models`. It's
applied at **three layers** for primary models:

- Model: `class ACIBaseModel(OwnerMixin, NetBoxModel)` (inherited).
- Serializer: `class <Model>Serializer(OwnerMixin, NetBoxModelSerializer)`
  (see [REST API - Inheritance](rest-api.md#inheritance)).
- GraphQL type: `class <Model>Type(OwnerMixin, NetBoxObjectType)`
  (see [GraphQL - Types](graphql-api.md#types)).

Relation / binding models (`ACIBridgeDomainL3OutBinding`,
`ACIContractRelation`) **skip** `OwnerMixin` at every layer; they
extend `NetBoxModel` / `NetBoxModelSerializer` / `NetBoxObjectType`
directly. Relations have no independent identity worth attributing to
an owner.

A primary model without a `name` cannot inherit `ACIBaseModel`, and so
loses the whole tail that base provides. It must hand-declare the parts
it needs rather than doing without them. `ACIFabric` and
`ACINodeInterface` both do this: they apply `OwnerMixin` themselves and
declare `nb_tenant`, `description` and `comments` as their own fields.
`description` always carries `max_length=ACI_DESC_MAX_LEN` and
`validators=[ACIPolicyDescriptionValidator]`, matching what
`ACIBaseModel` would have given it.

NetBox's own `PrimaryModel` looks like a shortcut here, since it is
`OwnerMixin` plus `description` and `comments`, but it is deliberately
not used. Its `description` is 200 characters with no validator, which
would let a user save a value the APIC rejects, and it carries no
`nb_tenant` regardless.

## Relation / Binding models

Use `Binding` for explicit ACI attachment/deployment associations where one
policy object is bound to another operational target, such as a domain, path,
L3Out, or AAEP domain. Binding models may carry configuration attributes such
as deployment immediacy, resolution immediacy, VLAN encapsulation, mode, or
VMM-specific settings. These attributes parameterize the binding and do not
make the model a `Relation`.

Use `Relation` for semantic policy relationships where a role, direction, or
type discriminator changes the meaning of the relationship itself. For example,
`ACIContractRelation.role` distinguishes provider and consumer semantics.

Use more specific ACI/domain nouns such as `Selector`, `Attribute`, or `Filter`
when those names better describe the modeled concept.

### Parent placement

Relation / Binding classes live in the **parent's** model file (the
side that owns `parent_object`). Example:
`ACIBridgeDomainL3OutBinding` lives in `bridge_domains.py` because
`parent_object = aci_bridge_domain`. Rationale:

- Cisco's MIT containment nests `<fvRsBDToOut>` inside `<fvBD>`.
- Network as Code models `l3outs` as a field of `bridge_domains`.
- The codebase rule is **policy containment**, not "every model that
  references X lives in X's file", as proven by
  `ACIEndpointGroupBaseModel` (FK to BD, lives in `endpoint_groups.py`).

The relation's **table, filterset, form, serializer, and GraphQL
filter** also live in the parent's layer file.

### `related_name` prefix

Use the `aci_` prefix on `related_name` to reduce overlap with
NetBox-side reverse relations and to keep the namespace
self-documenting at the call site:

```python
aci_bridge_domain = models.ForeignKey(
    to="netbox_aci_plugin.ACIBridgeDomain",
    on_delete=models.CASCADE,
    related_name="aci_l3out_bindings",
    verbose_name=_("ACI Bridge Domain"),
)
```

### Inheritance

Relation/Binding models extend `NetBoxModel` directly, **not**
`ACIBaseModel`. They have no `name` field and no DN-like identity, so
the ACI-policy text fields don't apply. See [`OwnerMixin`
coverage](#ownermixin-coverage) for the matching skip at serializer +
GraphQL-type layers.

## `CachedScopeMixin`

Fabric-scoped models (`ACIFabric`, `ACIPod`) inherit NetBox's
`dcim.models.mixins.CachedScopeMixin`, which adds
`scope_type` / `scope_id` / `scope` for assignment to a Site / Region /
SiteGroup / Location. Its `_region` and `_site_group` cache fields are
`on_delete=SET_NULL`: both may cache an ancestor of the actual scope,
so deleting that ancestor must not delete the scoped object. Include
the scope fields in `clone_fields`:

```python
from dcim.models.mixins import CachedScopeMixin


class ACIFabric(CachedScopeMixin, OwnerMixin, NetBoxModel):
    # ...
    clone_fields: tuple = (
        "description",
        "infra_vlan_vid",
        "infra_vlan",
        "gipo_pool",
        "scope_type",
        "scope_id",
        "nb_tenant",
    )
```

`CachedScopeMixin` ships its own denormalized cache fields (`_region`,
`_site_group`, `_site`, `_location`); exclude these from GraphQL
output via `exclude=[...]` on `@strawberry_django.type`.

## Choices

All `ChoiceSet` subclasses live in `netbox_aci_plugin/choices.py`,
grouped by domain with section comments:

```python
# Bridge Domain

class BDMultiDestinationFloodingChoices(ChoiceSet):
    """Choice set of Bridge Domain multi destination flooding."""

    # default "bd-flood"
    FLOOD_BD = "bd-flood"
    FLOOD_ENCAP = "encap-flood"
    FLOOD_DROP = "drop"

    CHOICES = (
        (FLOOD_BD, _("bd-flood"), "blue"),
        (FLOOD_ENCAP, _("encap-flood"), "yellow"),
        (FLOOD_DROP, _("drop"), "red"),
    )
```

Conventions:

- Name pattern: `<Domain><Field>Choices`.
- Constants are class attributes in UPPER_SNAKE_CASE with a domain prefix
  (`FLOOD_BD`, `UNKNOWN_MULTI_FLOOD`).
- Add a `# default "<value>"` comment so contributors see the model's
  field default at a glance.
- The third tuple element is the badge color (NetBox table/template
  helpers consume it via `get_<field>_color()`, see [Choice color
  helpers](#choice-color-helpers)).

### `add_custom_choice()`

For ChoiceSets that allow a free-text value alongside the enumerated
choices, append `(None, _("custom"))` via the helper:

```python
def add_custom_choice(choices) -> tuple:
    """Add a custom choice to the end of a ChoiceSet."""
    return tuple(choices) + ((None, _("custom")),)
```

Use it where a field accepts both a named choice and an arbitrary
string (e.g. some Contract Filter port fields).

### Cross-cutting choice sets

Choice sets used by multiple domains (e.g. `QualityOfServiceClassChoices`,
`QualityOfServiceDSCPChoices`) get their own conceptual section in
`choices.py`. Put them after the domain sections that reference them.

## ACI concept casing in prose

When prose names the ACI concept that a model or field represents, in
a class docstring, a `Notes:` block, a validation or error message, or
a help_text sentence, Title-Case the concept noun: "a Bridge Domain",
"the Endpoint Group", "a Contract Filter". This matches how the same
noun is already capitalized inside that model's
`verbose_name=_("ACI <X>")` value. A generic English use of the same
word, one that isn't naming the ACI concept, stays lowercase:

```python
_("A Bridge Domain must have at least one gateway subnet.")
```

This rule is scoped to prose casing only; casing inside `verbose_name`
values and code comments follows a separate, already-settled
convention.

## Model field kwarg ordering

Pass kwargs to model fields in this order. Skip any that aren't
needed; don't reorder:

### Base (every field)

```text
verbose_name
name
primary_key
max_length
unique
blank
null
db_index
rel
default
editable
serialize
unique_for_date
unique_for_month
unique_for_year
choices
help_text
db_column
db_tablespace
auto_created
validators
error_messages
```

### `DateField` / `TimeField` (append after base)

```text
auto_now
auto_now_add
```

### `DecimalField` (append after base)

```text
max_digits
decimal_places
```

### `GenericIPAddressField` (append after base)

```text
protocol
unpack_ipv4
```

### `ForeignKey`

For `ForeignKey` fields, use this standalone order, with `to` first,
before the base kwargs:

```text
to
on_delete
related_name
verbose_name
blank
null
related_query_name
limit_choices_to
parent_link
to_field
db_constraint
```

**GFK content-type FK exception:** the `<name>_type` FKs that pair with a
`GenericForeignKey` (e.g. `aci_object_type` in `contracts.py`,
`aci_domain_object_type` in `aaep.py`) place `limit_choices_to` right
after `related_name`, ahead of `verbose_name`/`blank`/`null`, so the
`Q`-object content-type filter sits next to the relation it constrains.

### `ManyToManyField` (append after base)

```text
symmetrical
through
through_fields
db_table
swappable
```

### `FileField` (append after base)

```text
upload_to
storage
```
