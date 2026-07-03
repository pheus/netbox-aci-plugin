# FilterSets

FilterSets live under `netbox_aci_plugin/filtersets/<domain>/<model>.py`.
Each primary model has a `<Model>FilterSet` registered via
`@register_filterset`. Shared FK filter pairs come from
`filtersets/mixins.py`.

## Field ordering

Inside a FilterSet, lead with the identifier fields:

```text
id
name / slug
```

Then declare domain-specific filters in roughly the order they appear
on the model.

## Dual name / ID filter pair

Every FK relationship gets **two** filters: one by `name` (or `slug`,
where applicable) and one by ID. The Django REST API and the UI both
consume them; expose both to keep the search experience consistent.

```python
aci_contract = django_filters.ModelMultipleChoiceFilter(
    field_name="aci_contract__name",
    queryset=ACIContract.objects.all(),
    to_field_name="name",
    label=_("ACI Contract (name)"),
)
aci_contract_id = django_filters.ModelMultipleChoiceFilter(
    queryset=ACIContract.objects.all(),
    to_field_name="id",
    label=_("ACI Contract (ID)"),
)
```

Common dual-filter groups are factored into mixins so individual
filtersets don't redeclare them.

## Mixins catalog

Defined in `filtersets/mixins.py`:

- `ACIFabricFilterSetMixin` exposes `aci_fabric` by name and
  `aci_fabric_id`.
- `ACITenantFilterSetMixin` exposes `aci_fabric` and `aci_tenant`, both
  as name/ID variants. Fabric traversal goes through the tenant.
- `ACITenantOrCommonFilterSetMixin` exposes the custom
  `present_in_aci_tenant_or_common_id` filter described below.
- `NBTenantFilterSetMixin` exposes `nb_tenant`, `nb_tenant_id`,
  `nb_tenant_group`, and `nb_tenant_group_id`. Name filters use slugs
  where the related NetBox model does.
- `ACICachedNetworkObjectFilterMixin` is a method-provider mixin (no
  FK name/ID pair). It supplies `filter_ip_address` and
  `filter_prefix` for FilterSets whose model caches an IP address or
  prefix object. Used by `filtersets/tenant/endpoint_groups.py` and
  `filtersets/tenant/endpoint_security_groups.py`.

`NBTenantFilterSetMixin` is universal: apply it to every primary-model
FilterSet that has an `nb_tenant` FK (i.e. all of them).

## Combined inheritance order

MRO matters. Stack mixins in this order so the resulting filter set
exposes everything cleanly without name collisions:

```python
@register_filterset
class ACIContractFilterSet(
    ACITenantFilterSetMixin,
    ACITenantOrCommonFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Contract model."""
```

Rules:

1. ACI scope mixins first (`ACIFabricFilterSetMixin`,
   `ACITenantFilterSetMixin`, `ACITenantOrCommonFilterSetMixin`),
   broadest scope first.
2. Then the NetBox-tenant mixin (`NBTenantFilterSetMixin`).
3. Then NetBox feature mixins from upstream (`OwnerFilterMixin`).
4. Then the base class `NetBoxModelFilterSet` last.

## `present_in_aci_tenant_or_common_id`

Use this filter (from `ACITenantOrCommonFilterSetMixin`) on FilterSets
whose model can reference resources in either the selected tenant or
the special `common` tenant in the same fabric (VRF, BD, Contract,
ContractFilter, L3Out). It expands the single-value tenant filter into
an OR across both tenants:

```python
@extend_schema_field(OpenApiTypes.INT)
def filter_present_in_aci_tenant_or_common_id(self, queryset, name, aci_tenant):
    """Return a QuerySet filtered by given ACI Tenant or 'common'."""
    if aci_tenant is None:
        return queryset.none()
    return queryset.filter(
        Q(aci_tenant=aci_tenant)
        | Q(
            aci_tenant__name="common",
            aci_tenant__aci_fabric_id=aci_tenant.aci_fabric_id,
        )
    )
```

Forms pair this with `query_params={"present_in_aci_tenant_or_common_id":
"$aci_tenant"}` (see [Forms - Cascading
dropdowns](forms.md#cascading-dropdowns)) to get the OR behavior in
cascading FK pickers.

## `search()`

Every FilterSet declares a `search(self, queryset, name, value)`
method. There are two patterns:

### Primary-model search

Searches the standard text fields on the model itself:

```python
def search(self, queryset, name, value):
    """Return a QuerySet filtered by the model's description."""
    if not value.strip():
        return queryset
    queryset_filter: Q = (
        Q(name__icontains=value)
        | Q(name_alias__icontains=value)
        | Q(description__icontains=value)
    )
    return queryset.filter(queryset_filter)
```

### Relation-model search

For relation/binding filtersets (no name/description of their own),
search the **related parent names** instead. FK traversal in the `Q`
is fine, and often essential, since the relation has no fields of its
own to search:

```python
def search(self, queryset, name, value):
    """Return a QuerySet filtered by the model's related object names."""
    if not value.strip():
        return queryset
    queryset_filter: Q = (
        Q(aci_contract__name__icontains=value)
        | Q(aci_endpoint_group__name__icontains=value)
        | Q(aci_vrf__name__icontains=value)
    )
    return queryset.filter(queryset_filter)
```

### Rules

- Always guard the whitespace-only case with `if not value.strip():
  return queryset`. Otherwise `__icontains` with `""` returns every
  row, which collapses the filter to a no-op but breaks the contract
  with the test suite (see [Tests - FilterSet
  tests](tests.md#filterset-tests)).
- Combine clauses with `Q | Q`, not chained `.filter().filter()` (the
  latter is AND, not OR).
- Use `__icontains` for the text-field side; FK-traversal sides also
  use `__name__icontains`.
