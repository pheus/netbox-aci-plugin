# Seeding Demo Data

`scripts/seed_demo_data.py` builds a full ACI dataset for local
development: Fabrics, Pods, Nodes, Node Interfaces, VPC Protection
Groups, access policies, Leaf Switch Profiles, Tenants, VRFs, Bridge
Domains, L3Outs, Endpoint Groups, Endpoint Security Groups and
Contracts, plus the NetBox core objects (Sites, Devices, VRFs,
Prefixes, VLANs) they reference. Every plugin model gets at least one
row, so it doubles as a manual smoke test for the full object graph.

Run it with:

```bash
make seed
```

which pipes the script through NetBox's management shell against the
`NETBOX_ROOT` checkout (`/opt/netbox` by default, override with `make
seed NETBOX_ROOT=/path/to/netbox`). If the virtualenv is not active in
the current shell, spell out the interpreter explicitly:

```bash
cd /opt/netbox && /opt/netbox/venv/bin/python netbox/manage.py shell < /path/to/netbox-aci-plugin/scripts/seed_demo_data.py
```

Note that this is one of the few places that deliberately uses `shell`
rather than `nbshell`. Only `shell` reads piped stdin and runs it
through `exec()`. `nbshell` drops straight into `code.interact()`, which
compiles the input line by line and silently truncates every function
body at its first blank line.

## Additive and convergent

The seeder never deletes anything. Every object goes through an
`ensure()` helper that splits its arguments in two. The keyword
arguments are the row's identity, chosen to match the model's real
uniqueness constraint, falling back to its natural key for the few
core models with no constraint at all. The `defaults` dictionary is
the row's desired state. A row that already exists is brought to that
state rather than left alone, so editing a spec in the script takes
effect on the next run. Every row is validated with `full_clean()`,
whether it was just built or already existed, and written only when
something actually changed. Running the script twice is a no-op the
second time.

The whole run happens inside one `transaction.atomic()` block, so a
validation failure partway through leaves the database exactly as it
was before the run started.

The script writes to whichever database the active NetBox
configuration points at. It has no database flag of its own, so check
which configuration is active first.

## What a run reports

The closing summary counts only the rows this run touched, split into
created, updated and unchanged, and covers the NetBox core objects
alongside the plugin ones. A second run in a row should report every
model as unchanged. A run also fails outright when a plugin model
never received a row, which keeps the seeder honest as new models
arrive.

## Naming scheme

Object names encode where they live in the Fabric and Tenant
hierarchy, so a name usually tells you its scope without following any
foreign keys. A few object types don't fit as cleanly: `ACIContractFilterEntry`
rows (`tcp-app-syn-ack`, `arp-request`) carry no scope prefix at all
and rely on their parent Contract Filter instead, and a fabric-scoped
name can still contain a hyphen of its own, as in the VPC Protection
Group `F1VPC2101-2102`.

| Scope | Pattern | Example |
|---|---|---|
| Fabric-scoped | fused fabric prefix, no separator | `F1Pod1`, `F1Leaf2101`, `F1AAEP1` |
| Tenant-scoped | fused fabric and tenant prefix, then a hyphen, then the object token | `F1T1-VRF1`, `F1T1-BD1-Sub1` |
| Reserved ACI Tenants | the Tenant keeps its exact APIC name, children take a capitalised short token | Tenant `common`, child `F1Cmn-VRF1` |

Unlike the tenant-scoped children above, the Leaf Switch Profile tree
does not build a child's name from its parent's. A Leaf Switch Profile,
its Leaf Selectors and their Leaf Node Blocks are each named after the
Node IDs they cover, the same way a VPC Protection Group is, so
`F1SwProf2101-2104` holds `F1SwSel2101-2102` and `F1SwSel2103-2104`,
and the first of those holds `F1NodeBlk2101-2102`. A Leaf Node Block
covering a single Node drops the range, as in `F2NodeBlk2101`.

Fabrics themselves stay `Fabric1` and `Fabric2`. Fabric1 carries all
three reserved Tenants, matching what the plugin's default data
migrations create. Fabric2 gets only `common`.

## Node ID scheme

Node IDs follow a four-digit `abcd` pattern: `a` is the switch type (`1`
for an RJ45 leaf, `2` for an SFP leaf, `3` for a spine), `b` is the Pod
ID, and `cd` counts up from `01` within that type and Pod. vPC pairs
always take an odd Node immediately followed by the next even Node,
for example `2101` paired with `2102`, or `2103` paired with `2104`.

APIC Nodes fall outside this scheme entirely. `ACINode` caps the Node
ID at 100 for the `apic` role, so APICs are simply numbered `1`, `2`,
`3` and take no Pod or type digits.

## The Fabrics

Fabric1 is built out in full: Pods, both leaf switch types, spines,
APICs, vPC pairs, a complete set of access policies and Tenants.
Fabric2 stays deliberately thin, with a Pod and a vPC pair of its own
and a much smaller slice of access policies and Tenants. A thin second
Fabric gives fabric-scoped filtering and isolation checks something
real to exclude, without duplicating the whole Fabric1 dataset.

Device Types mirror the NetBox Device Type Library, down to the port
layout of the real hardware, so a leaf carries its full complement of
downlinks and uplinks rather than a token handful. Every Device's
Interfaces are built from those Interface Templates rather than
hard-coded. NetBox only instantiates templates when a Device is first
created, so the seeder materializes them itself and a database whose
Devices predate the templates converges on the next run. The APICs are
the exception worth knowing: they are UCS appliances, so they carry no
`Ethernet1/N` ports at all and their management interface is the
`CIMC`, not an `mgmt0`.

## NetBox VRF mapping

Each ACI VRF that owns a Bridge Domain gets its own NetBox VRF, named
`ACI-Demo-` followed by the ACI VRF name and keyed on its route
distinguisher, since that is the only unique field NetBox gives a VRF.
Every gateway address, External Subnet prefix and uSeg Network
Attribute object is then created in the NetBox VRF mapped to its own
ACI VRF, derived from the object's place in the ACI hierarchy rather
than hard-coded. That keeps the demo data consistent with the rule
`ACIExternalSubnet` validates, which compares a linked prefix's NetBox
VRF against the one mapped to its ACI VRF.

`F1Infra-VRF1` owns no Bridge Domain and is deliberately left
unmapped, so an ACI VRF without an `nb_vrf` stays in the dataset.
`ACI-Demo-Underlay` is the other exception: it carries the TEP pools
and the Node TEP addresses, and maps to no ACI VRF at all.

## Extending the seeder

Each domain has its own `seed_*()` function. Most blocks declare their
objects as a tuple of field values that the function iterates over,
and extending them means adding an entry to that spec tuple. Objects
too dissimilar to tabulate, such as the L3Outs or the Endpoint Group
AAEP Bindings, are instead spelled out one `ensure()` call at a time.

Domain order is fixed by the `transaction.atomic()` block at the
bottom of the script. Within a domain, respect the same ordering the
existing entries already follow, for example a Pod before its Nodes,
or both members of a vPC pair before the VPC Protection Group that
references them. The one that catches new entries most often: an
`ACIEndpointGroupDomainBinding` and an `ACIAAEPDomainBinding` must both
already be saved before an `ACIEndpointGroupAAEPBinding` for the same
EPG validates, because that binding's clean checks intersect the
persisted domain columns of the two binding types.

Four more traps aren't visible from reading the script but will catch
the next added row. Never key `ensure()`'s lookup on a field that
`save()` overwrites afterward: `ACIEndpointGroupAAEPBinding.encap_vlan_id`
is overwritten from `nb_vlan.vid`, and `ACIExternalSubnet.matched_prefix`
is overwritten from `nb_prefix.prefix`, so key those lookups on
`(aci_endpoint_group, aci_aaep)` and `(aci_external_endpoint_group,
name)` instead. A `GenericForeignKey` also cannot appear in a lookup
at all. Django raises `FieldError` if you try. That is the entire
reason the `gfk()` helper exists: it expands the GFK into its `_type`
/ `_id` column pair so the lookup can filter on those columns instead.
Assigning the GFK attribute directly in the model constructor, rather
than through `gfk()`, is fine, since only the lookup side needs the
expanded pair.

The third trap is that a model may refuse a field change after
creation. `ACILeafInterfacePolicyGroup` rejects a new `group_type` on
a row that already exists, so editing that column in a spec raises
rather than quietly creating a second group beside the first. The
fourth is the coverage check: adding a plugin model and forgetting to
seed it fails the run by name. `EXEMPT_MODELS` is the escape hatch for
a model that genuinely should not be seeded.

!!! warning "Seeding over existing objects"
    The seeder reconciles. An object whose identity fields match one
    of its specs is adopted and then brought to the values the script
    declares, so a hand-made object that collides by name loses its
    own values, while objects the plugin's data migrations create,
    such as `Fabric1` and the reserved ACI Tenants, gain the demo
    owner, scope and relations they would otherwise never get.
    Nothing is ever deleted, and the whole run is one transaction, so
    a collision that cannot be reconciled aborts cleanly rather than
    leaving half a dataset behind.

    Re-seeding a database built by an earlier version of the script
    leaves three kinds of orphan behind, all harmless on a development
    database. The previous Bridge Domain gateway addresses stay in
    `ACI-Demo-F1T1`, unreferenced. Each APIC keeps a stale `mgmt0`,
    since it now takes a `CIMC` instead. The Device Types the leaves
    used to point at also remain, because the seeder repoints the
    Devices rather than deleting the rows they left.
