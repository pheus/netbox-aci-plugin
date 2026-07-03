# GraphQL API

The plugin's GraphQL schema is built on
[strawberry](https://strawberry.rocks/) +
[strawberry-django](https://strawberry-django.readthedocs.io/), via
NetBox's `NetBoxObjectType` / `NetBoxModelFilter` base classes.

File layout under `netbox_aci_plugin/graphql/`:

| File                          | Content                                     |
|-------------------------------|---------------------------------------------|
| `types.py`                    | One `<Model>Type` class per model           |
| `schema.py`                   | The `Query` type composing all model fields |
| `enums.py`                    | `ChoiceSet` to `strawberry.enum` re-exports |
| `filter_lookups.py`           | Project-specific lookup overrides           |
| `filters/<domain>/<model>.py` | Per-model `Filter` dataclasses              |
| `filters/mixins.py`           | Shared `ACIBaseFilterMixin`                 |

## Types

All `<Model>Type` classes live in a single `graphql/types.py`. Each
type is registered with the model's filter via
`@strawberry_django.type`:

```python
@strawberry_django.type(
    models.ACIBridgeDomain,
    fields="__all__",
    filters=ACIBridgeDomainFilter,
    pagination=True,
)
class ACIBridgeDomainType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIBridgeDomain model."""

    # Model fields
    aci_tenant: Annotated["ACITenantType", strawberry.lazy("...")] | None
    aci_vrf: Annotated["ACIVRFType", strawberry.lazy("...")] | None
    nb_tenant: (
        Annotated[
            "TenantType",
            strawberry.lazy("tenancy.graphql.types"),
        ]
        | None
    )

    # Related models
    aci_bridge_domain_subnets: list[
        Annotated["ACIBridgeDomainSubnetType", strawberry.lazy("...")]
    ]
```

Rules:

- **Primary models**: `class <Model>Type(OwnerMixin, NetBoxObjectType)`.
- **Relation / binding models**: `class <Model>Type(NetBoxObjectType)`,
  with no `OwnerMixin` (see [Models - OwnerMixin
  coverage](models.md#ownermixin-coverage)).
- `pagination=True` is required on every type decorator.
- `fields="__all__"` is the default. Use `exclude=[...]` for both
  GenericForeignKey component fields (e.g. `scope_type`, `scope_id`,
  `aci_object_id`, `aci_object_type`) and denormalized cache fields
  that should not surface in the API (e.g. `_aci_endpoint_group`,
  `_ip_address`).
- Sections marked with `# Model fields` and `# Related models`
  comments.
- Cross-type refs use the lazy pattern
  `Annotated["TypeName", strawberry.lazy("module.path")] | None` to
  avoid circular imports.

### Custom `@strawberry_django.field` resolvers

For computed fields (e.g. a GFK's `scope` polymorphic resolver),
declare a `@strawberry_django.field`:

```python
@strawberry_django.field(description="Scope Object")
def scope(self) -> (
    Annotated[
        Annotated["LocationType", strawberry.lazy("dcim.graphql.types")]
        | Annotated["RegionType", strawberry.lazy("dcim.graphql.types")]
        # ...
    ]
):
    return self.scope
```

## Filters

Per-domain filters live under `graphql/filters/<domain>/<model>.py`.
Every primary ACI filter subclasses `ACIBaseFilterMixin`. Exceptions:
child/Binding filters for models that have no `name`, `name_alias`, or
`description` fields (e.g. `ACIBridgeDomainL3OutBindingFilter`) use the
plain `NetBoxModelFilter` base instead; and primary models that lack
`name_alias` (currently only `ACIFabric`) declare their fields manually
and extend `ScopedFilterMixin, NetBoxModelFilter` rather than
`ACIBaseFilterMixin` (`graphql/filters/fabric/fabrics.py`).

```python
@dataclass
class ACIBaseFilterMixin(NetBoxModelFilter):
    """Base GraphQL filter mixin for ACI models."""

    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    name_alias: StrFilterLookup[str] | None = strawberry_django.filter_field()
    description: StrFilterLookup[str] | None = strawberry_django.filter_field()

    nb_tenant: (
        Annotated[
            "TenantFilter",
            strawberry.lazy("tenancy.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    nb_tenant_id: ID | None = strawberry_django.filter_field()
    nb_tenant_group: (
        Annotated["TenantGroupFilter", strawberry.lazy("tenancy.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    nb_tenant_group_id: (
        Annotated["TreeNodeFilter", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
```

It provides the universal text fields (`name`, `name_alias`,
`description`) and the NetBox-tenant scope pair (`nb_tenant` /
`nb_tenant_id` / `nb_tenant_group` / `nb_tenant_group_id`).

### Filter inheritance layering

Some domains define an intermediate `@dataclass` mixin that still
subclasses `ACIBaseFilterMixin`, adding domain-specific shared fields
before concrete filter classes specialise further:

- `ACIEndpointGroupBaseFilterMixin` (`filters/tenant/endpoint_groups.py`)
  - shared by `ACIEndpointGroupFilter` and `ACIUSegEndpointGroupFilter`
- `ACIUSegAttributeBaseFilterMixin` (`filters/tenant/endpoint_groups.py`)
  - shared by `ACIUSegNetworkAttributeFilter`
- `ACIEsgSelectorBaseFilterMixin` (`filters/tenant/endpoint_security_groups.py`)
  - shared by `ACIEsgEndpointGroupSelectorFilter` and `ACIEsgEndpointSelectorFilter`

Scoped models (e.g. `ACIPod`) also mix in NetBox core's
`ScopedFilterMixin` from `dcim.graphql.filter_mixins` alongside
`ACIBaseFilterMixin`.

### String field coverage

ALL model string fields must be exposed as GraphQL filter fields with
`StrFilterLookup[str]` lookup type. This includes `_policy_name` and
`_route_map_name` fields, not just FK and boolean fields. If a model
has a `CharField` or `TextField` that isn't covered by the base mixin,
add it explicitly in the model's filter class.

### ArrayField filters via `StringArrayLookup`

Model fields backed by `ArrayField` (e.g. `security_domains`,
`dhcp_labels`) must be exposed as GraphQL filters using
`StringArrayLookup` from `netbox.graphql.filter_lookups`:

```python
from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import StringArrayLookup

@strawberry_django.filter_type(models.ACIRoutedDomain, lookups=True)
class ACIRoutedDomainFilter(ACIBaseFilterMixin):
    security_domains: (
        Annotated[
            "StringArrayLookup",
            strawberry.lazy("netbox.graphql.filter_lookups"),
        ]
        | None
    ) = strawberry_django.filter_field()
```

Import `StringArrayLookup` inside `TYPE_CHECKING` to satisfy ruff's
F821 check. The runtime uses `strawberry.lazy(...)` for the actual
resolution.

### `StrFilterLookup` compat shim

The filter mixin imports `StrFilterLookup` with a fallback:

```python
try:
    from strawberry_django import StrFilterLookup
except ImportError:
    from strawberry_django import FilterLookup as StrFilterLookup
```

!!! note "Remove once NetBox floor is 4.6.0+"
    `StrFilterLookup` was introduced in `strawberry-django` shipped
    with NetBox 4.6. While the plugin supports NetBox 4.5.0 through
    4.5.10, the fallback to `FilterLookup` is required. Once the
    `PluginConfig.min_version` is raised to `4.6.0`, drop the
    `try/except` and import `StrFilterLookup` directly.

## Enums

`graphql/enums.py` re-exports every `ChoiceSet` from `choices.py` as a
strawberry enum:

```python
import strawberry

from ..choices import (
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
    # ...
)

__all__ = (
    "BDMultiDestinationFloodingEnum",
    "BDUnknownMulticastEnum",
    "BDUnknownUnicastEnum",
    # ...
)

# Bridge Domain

BDMultiDestinationFloodingEnum = strawberry.enum(
    BDMultiDestinationFloodingChoices.as_enum()
)
BDUnknownMulticastEnum = strawberry.enum(BDUnknownMulticastChoices.as_enum())
BDUnknownUnicastEnum = strawberry.enum(BDUnknownUnicastChoices.as_enum())


# Contract Filter

ContractFilterARPOpenPeripheralCodesEnum = strawberry.enum(
    ContractFilterARPOpenPeripheralCodesChoices.as_enum()
)
# ...
```

Rules:

- One enum per `ChoiceSet`. Name pattern: replace the `Choices` suffix
  on the source class with `Enum`.
- Group by ACI sub-domain with `# <Domain>` section comments
  (Bridge Domain, Contract Filter, Contract, Contract Relation, ...).
- Maintain the `__all__` tuple in sorted order. New entries get
  inserted alphabetically.

## `filter_lookups.py`

Project-specific lookup type overrides. Currently houses one
specialization for TCP rule array filtering:

```python
import strawberry
from netbox.graphql.filter_lookups import ArrayLookup
from .enums import ContractFilterTCPRulesEnum


@strawberry.input(
    one_of=True,
    description="Lookup for Array fields. Only one of the lookup fields can be set.",
)
class TCPRulesArrayLookup(ArrayLookup[ContractFilterTCPRulesEnum]):
    """Specialized lookup for TCP rules in an array field."""
    pass
```

New project-specific lookups go in this file. Don't reach into
`netbox.graphql.filter_lookups` from arbitrary filter modules; funnel
them through `filter_lookups.py` so the surface is greppable.

## Schema composition

`graphql/schema.py` declares a single `Query` type. For each
`<Model>Type`, it exposes **both** singular and list fields via
`strawberry_django.field()`:

```python
@strawberry.type(name="Query")
class NetBoxACIQuery:
    """GraphQL query definition for the NetBox ACI Plugin."""

    aci_fabric: ACIFabricType = strawberry_django.field()
    aci_fabric_list: list[ACIFabricType] = strawberry_django.field()

    aci_pod: ACIPodType = strawberry_django.field()
    aci_pod_list: list[ACIPodType] = strawberry_django.field()

    aci_node: ACINodeType = strawberry_django.field()
    aci_node_list: list[ACINodeType] = strawberry_django.field()
    # ...
```

Naming convention:

- Singular: `aci_<snake_case_model>` (e.g. `aci_fabric`,
  `aci_bridge_domain`, `aci_contract_relation`).
- List: `aci_<snake_case_model>_list`.

Both registered via `strawberry_django.field()`; no extra arguments
needed. The type's `filters=` declaration on `@strawberry_django.type`
wires up the query parameters automatically.
