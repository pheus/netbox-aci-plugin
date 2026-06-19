# GraphQL API

The plugin registers a GraphQL type and a `<model>` / `<model>_list`
query pair for every ACI object, following NetBox's GraphQL
conventions. Refer to NetBox's GraphQL API documentation for the
general query syntax, authentication, and pagination.

## Filtering lists by ID

Every `<model>_list` query accepts a `filters` argument. To match a
single object by primary key, use the `id` lookup; to match several at
once, use `in_list`:

```graphql
query {
  aci_tenant_list(filters: {id: {in_list: ["12", "34"]}}) {
    id
    name
  }
}
```

## Filtering by a related object's ID

To filter by a **related** object's ID, traverse the relation filter
and use its `id` lookup. For example, to list every tenant that belongs
to a set of fabrics:

```graphql
query {
  aci_tenant_list(filters: {aci_fabric: {id: {in_list: ["1", "2"]}}}) {
    id
    name
  }
}
```

The same pattern applies to any foreign-key relation (`aci_tenant`,
`aci_vrf`, `aci_bridge_domain`, and so on): filter on the relation and
use its inherited `id` lookup. This mirrors NetBox core, which keeps the
flat `<relation>_id` inputs as single-value matches.
