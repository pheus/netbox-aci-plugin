# Search

Every primary ACI model registers a `SearchIndex` subclass in
`netbox_aci_plugin/search.py`. The file is a flat list of
`@register_search`-decorated classes; one class per model, ordered by
the model's place in the ACI policy tree (fabric inventory first, then
access policies, then tenant).

## Index contract

```python
@register_search
class ACIBridgeDomainIndex(SearchIndex):
    """NetBox search definition for the ACI Bridge Domain model."""

    model = ACIBridgeDomain

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
        ("comments", 5000),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
    )
```

## Weight tuple

Standard weights for primary-model text fields (lower number = higher
priority):

| Field         | Weight |
|---------------|--------|
| `name`        | 100    |
| `name_alias`  | 300    |
| `description` | 500    |
| `comments`    | 5000   |

Use this table verbatim for every primary model that has these fields.
Don't invent new weights for standard fields; consistency matters more
than fine-tuning per model.

## `display_attrs`

For a model that has these fields, the primary-model index includes
`name`, `name_alias`, `description`, and `nb_tenant` in `display_attrs`.
Models that lack some of these fields (e.g. `ACIFabric` has no
`name_alias`) omit those fields from `display_attrs`. Add `aci_tenant`
(and other parent-scope FKs like `aci_vrf`, `aci_fabric`) when they help
users disambiguate results at a glance.

## Field-lookup naming

Use **internal field names** in both `fields` and `display_attrs`, not
`__name` traversals.

```python
# Good: internal field
fields: tuple = (
    ("aci_bridge_domain", 100),
    ("aci_l3out", 300),
)

# Bad: traversal
fields: tuple = (
    ("aci_bridge_domain__name", 100),
)
```

## Denormalized FK fields in weight tuples

When a GFK target should be searchable, register the denormalized
`_`-prefixed FK cache fields in the weight tuple so search can filter
without traversing the GFK (see [Models - Denormalized FK
caching](models.md#denormalized-fk-caching)). Examples include
`ACIContractRelation`, `ACIUSegNetworkAttribute`,
`ACIEsgEndpointGroupSelector`, and `ACIEsgEndpointSelector`:

```python
@register_search
class ACIContractRelationIndex(SearchIndex):
    model = ACIContractRelation
    fields: tuple = (
        ("aci_contract", 100),
        ("_aci_endpoint_group", 300),
        ("_aci_useg_endpoint_group", 300),
        ("_aci_endpoint_security_group", 300),
        ("_aci_external_endpoint_group", 300),
        ("_aci_vrf", 400),
    )
```

## Relation-model exception

Relation and binding models have no `name`/`name_alias`/`description`/
`comments` of their own; they're pure joins. Their indexes register
only the FK fields they relate, with weights starting at 100 for the
primary FK and rising for secondary FKs:

```python
@register_search
class ACIBridgeDomainL3OutBindingIndex(SearchIndex):
    model = ACIBridgeDomainL3OutBinding
    fields: tuple = (
        ("aci_bridge_domain", 100),
        ("aci_l3out", 300),
    )
    display_attrs: tuple = ("aci_bridge_domain", "aci_l3out")
```

!!! tip "Future adoption"
    NetBox's `SearchIndex` accepts a `category` attribute that groups
    results in the global search UI. Adopting it would let us group
    ACI hits by sub-domain ("Policies", "Contracts", "Domains",
    "Fabric") instead of flattening every model into one ACI bucket.
