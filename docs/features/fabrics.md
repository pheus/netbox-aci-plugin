# Fabrics

An ACI Fabric represents the physical and logical underlay that hosts
one or more tenants and their policies.
It encompasses pods, nodes, interfaces, domains, and VLAN resources
that collectively provide the infrastructure on which tenant
constructs operate.

```mermaid
flowchart TB
  FAB[Fabric]
  POD[Pod]

  %% Fabric topology
  subgraph graphFAB [Fabric]
        FAB -->|1:n| POD
  end
```

## Fabric

A **Fabric** represents a single ACI deployment containing Pods, Nodes,
and fabric-level policy objects.
A Fabric can host multiple Tenants.

The **ACIFabric** model has the following fields:

*Required fields*:

- **Name**: the ACI Fabric name.
- **Fabric ID**: numeric identifier configured during APIC fabric setup.
    - Values: `1`–`128`
- **Infrastructure VLAN ID**: fabric-wide infrastructure VLAN used for
  APIC-to-switch communication.
    - Values: `1`–`4094`

*Optional fields*:

- **Description**: a description of the Fabric.
- **Infrastructure VLAN**: reference to a NetBox VLAN documenting the
  same VLAN ID.
- **GiPo pool**: reference to a NetBox Prefix representing the
  Bridge Domain multicast (GiPo) pool used for fabric multicast
  (for example, `225.0.0.0/15`).
- **NetBox tenant**: association to a NetBox Tenant.
- **Comments**: a text field for notes (Markdown supported).
- **Tags**: a list of NetBox tags.

## Pod

An **ACI Pod** groups a set of leaf and spine nodes within a Fabric.
Pods provide a way to scale the fabric by grouping nodes into separate
domains while maintaining a unified management plane.
Each Pod within a Fabric must have a unique identifier and is assigned
a TEP pool for internal addressing.

The **ACIPod** model has the following fields:

*Required fields*:

- **Name**: the Pod name.
- **ACI Fabric**: reference to the related ACIFabric.
- **Pod ID**: unique numeric identifier within the Fabric.
    - Values: `1`–`255`

*Optional fields*:

- **Name alias**: an optional alias for the Pod name.
- **Description**: a description of the Pod.
- **TEP Pool**: reference to a NetBox Prefix representing the
  pod-wide IPv4 Tunnel Endpoint (TEP) pool.
    - Recommended: a dedicated unicast IPv4 prefix sized appropriately
      for the expected scale
      (commonly `/16`; smaller pools may be supported depending on
      APIC release and fabric scale).
- **NetBox tenant**: association to a NetBox Tenant.
- **Comments**: a text field for notes (Markdown supported).
- **Tags**: a list of NetBox tags.
