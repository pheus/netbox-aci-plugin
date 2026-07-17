# Access Policies

An ACI Fabric contains access policies that define how tenant policies can be
attached to the fabric infrastructure. Access policy objects are scoped to an
ACI Fabric and can be referenced by tenant policy objects such as L3Outs.

```mermaid
flowchart TD
    FAB[Fabric]
    AAEP(AAEP)
    PD(Physical Domain)
    RD(Routed Domain)
    L3O(L3Out)
    EPG(Endpoint Group)
    VP(VLAN Pool)
    VPR(VLAN Pool Range)
    NBVG[NetBox VLAN Group]

    subgraph graphAP [Access Policies]
        FAB -->|1:n| AAEP
        FAB -->|1:n| PD
        FAB -->|1:n| RD
        FAB -->|1:n| VP
        VP -->|1:n| VPR
        AAEP -.->|n:n| PD
        AAEP -.->|n:n| RD
        PD -.->|n:1| VP
        RD -.->|n:1| VP
    end
    L3O -.->|n:1| RD
    EPG -.->|n:n| AAEP
    VP -.->|1:1| NBVG
```

## Physical Domain

A *Physical Domain* represents an ACI physical domain (`physDomP`) used for
bare-metal and hypervisor connectivity. Physical Domains are defined under
the ACI Fabric access policies and can be referenced by EPG domain bindings.

The *ACIPhysicalDomain* model has the following fields:

*Required fields*:

- **Name**: represents the Physical Domain name in the ACI.
- **ACI Fabric**: a reference to the `ACIFabric` model.

*Optional fields*:

- **Name alias**: a name alias in the ACI for the Physical Domain.
- **Description**: a description of the Physical Domain.
- **Security domains**: a comma-separated list of ACI security domains.
- **ACI VLAN Pool**: an optional reference to an `ACIVLANPool` that defines
  the VLANs available to this domain. The pool must belong to the same
  ACI Fabric as the Physical Domain.
- **NetBox Tenant**: a reference to the NetBox tenant model.
- **Comments**: a text field for additional notes.
- **Tags**: a list of NetBox tags.

*Validation rules*:

- Each domain name in **Security domains** must be unique within the list
  (duplicates are rejected).
- The `(aci_fabric, name)` combination must be unique per fabric.

AAEP bindings for a Physical Domain are managed on the domain's detail
page via the **AAEPs** tab.

## Routed Domain

A *Routed Domain* represents an ACI L3 domain used for routed external
connectivity. Routed Domains are defined under the ACI Fabric access policies
and can be referenced by L3Out policy.

The *ACIRoutedDomain* model has the following fields:

*Required fields*:

- **Name**: represents the Routed Domain name in the ACI.
- **ACI Fabric**: a reference to the `ACIFabric` model.

*Optional fields*:

- **Name alias**: a name alias in the ACI for the Routed Domain.
- **Description**: a description of the Routed Domain.
- **Security domains**: a comma-separated list of ACI security domains.
- **ACI VLAN Pool**: an optional reference to an `ACIVLANPool` that defines
  the VLANs available to this domain. The pool must belong to the same
  ACI Fabric as the Routed Domain.
- **NetBox Tenant**: a reference to the NetBox tenant model.
- **Comments**: a text field for additional notes.
- **Tags**: a list of NetBox tags.

*Validation rules*:

- Each domain name in **Security domains** must be unique within the list
  (duplicates are rejected).
- The `(aci_fabric, name)` combination must be unique per fabric.

AAEP bindings for a Routed Domain are managed on the domain's detail
page via the **AAEPs** tab.

## VLAN Pool

A *VLAN Pool* represents an ACI VLAN instance profile (`fvnsVlanInstP`),
a fabric-scoped collection of VLAN encapsulation ranges with a common
allocation mode. VLAN Pools group one or more VLAN ranges and are consumed
by ACI domains to define which VLANs those
domains may use.

The *ACIVLANPool* model has the following fields:

*Required fields*:

- **Name**: the VLAN Pool name in the ACI.
- **ACI Fabric**: a reference to the `ACIFabric` model.
- **Allocation mode**: controls how VLANs in the pool are assigned.
    - Values: `static` (static), `dynamic` (dynamic)
    - Default: `static`
    - Static pools use manually defined ranges. Dynamic pools allow
      the APIC to assign VLANs automatically (typically for VMM domains).

*Optional fields*:

- **Name alias**: a name alias in the ACI for the VLAN Pool.
- **Description**: a description of the VLAN Pool.
- **NetBox VLAN group**: an optional one-to-one reference to a NetBox
  `VLANGroup` that documents the same set of VLAN resources. When set, every
  VLAN Pool range must fall within the group's VID ranges.
- **NetBox tenant**: association to a NetBox tenant.
- **Comments**: a text field for notes (Markdown supported).
- **Tags**: a list of NetBox tags.

VLAN ranges belonging to a pool are managed on the pool's detail page
via the **VLAN Pool Ranges** tab.

## VLAN Pool Range

A *VLAN Pool Range* represents an ACI encapsulation block (`fvnsEncapBlk`),
a contiguous block of VLAN IDs within a VLAN Pool. Each range defines a
start VLAN, an end VLAN, an allocation mode override, and a role.

The *ACIVLANPoolRange* model has the following fields:

*Required fields*:

- **ACI VLAN Pool**: a reference to the parent `ACIVLANPool`.
- **VLAN ID (from)**: the first VLAN ID in the block.
    - Values: `1-4094`
- **VLAN ID (to)**: the last VLAN ID in the block.
    - Values: `1-4094`

*Optional fields*:

- **Allocation mode**: per-range override of the pool allocation mode.
    - Values: `inherit` (inherit), `static` (static), `dynamic` (dynamic)
    - Default: `inherit`
    - When set to `inherit`, the range uses the parent pool's allocation
      mode.
- **Role**: the intended use of VLANs in this block.
    - Values: `external` (external), `internal` (internal)
    - Default: `external`
- **Comments**: a text field for notes (Markdown supported).
- **Tags**: a list of NetBox tags.

*Validation rules*:

- The starting VLAN ID must not be greater than the ending VLAN ID.
- A range must not overlap any existing range within the same pool.

## Attachable Access Entity Profile

An *Attachable Access Entity Profile* (AAEP) represents an ACI attachable
access entity profile (`infraAttEntityP`) that ties interface policy groups to
physical and routed domains, and optionally enables the infrastructure VLAN on
the associated ports.

The *ACIAttachableAccessEntityProfile* model has the following fields:

*Required fields*:

- **Name**: represents the AAEP name in the ACI.
- **ACI Fabric**: a reference to the `ACIFabric` model.

*Optional fields*:

- **Name alias**: a name alias in the ACI for the AAEP.
- **Description**: a description of the AAEP.
- **Infrastructure VLAN**: a boolean field, whether the infrastructure VLAN is
  enabled on ports associated with this AAEP.
    - Default: `false`
- **NetBox Tenant**: a reference to the NetBox tenant model.
- **Comments**: a text field for additional notes.
- **Tags**: a list of NetBox tags.

*Validation rules*:

- The `(aci_fabric, name)` combination must be unique per fabric.

Domain bindings for an AAEP are managed on the profile's detail page via
the **Domain Bindings** tab, and Endpoint Group bindings via the
**EPG Bindings** tab.

## AAEP Domain Binding

An *AAEP Domain Binding* represents an ACI domain-to-AAEP association
(`infraRsDomP`) that links an AAEP to a Physical Domain or a Routed Domain.
Each binding associates exactly one AAEP with exactly one domain, and the
domain must belong to the same ACI Fabric as the AAEP.

The *ACIAAEPDomainBinding* model has the following fields:

*Required fields*:

- **ACI AAEP**: a reference to the parent `ACIAttachableAccessEntityProfile`.
- **ACI domain object**: the Physical Domain or Routed Domain to associate with
  the AAEP.

*Optional fields*:

- **Comments**: a text field for additional notes.
- **Tags**: a list of NetBox tags.

*Validation rules*:

- The assigned domain must belong to the same ACI Fabric as the parent AAEP.
- Each `(aci_aaep, domain)` combination must be unique (an AAEP cannot be
  bound to the same domain twice).

## Endpoint Group AAEP Binding

A VLAN Pool supplies the fabric's encapsulation ranges, a domain consumes
one of those pools, and an AAEP binds interface policy groups to that
domain. An *Endpoint Group AAEP Binding* is the last link: it represents
an ACI EPG-to-AAEP deployment association (`infraRsFuncToEpg`) that
statically deploys an Endpoint Group's VLAN encapsulation on every
interface the AAEP covers.

The binding references the Endpoint Group directly, but deploying it
still depends on the Endpoint Group already being bound to a domain: the
Endpoint Group needs its own domain binding to a Physical Domain, and the
AAEP needs its own binding to that same domain, or to at least one
domain the two have in common if either side is bound to more than one.
An Endpoint Group attached to a Physical Domain, for instance, can only
be deployed through AAEPs that are themselves bound to that same domain.
When none of the Endpoint Group's domains match one of the AAEP's, the
fabric raises fault F0467.

This binding models the deployment's AAEP-originated relation,
`infraRsFuncToEpg`. It does not model `fvRsAepAtt`, the EPG-originated
variant APIC introduced in 6.1(3f).

The *ACIEndpointGroupAAEPBinding* model has the following fields:

*Required fields*:

- **ACI Endpoint Group**: the Endpoint Group to deploy through the AAEP.
- **ACI AAEP**: the Attachable Access Entity Profile to deploy the
  Endpoint Group through.
- **Encap VLAN ID**: the VLAN encapsulation of the deployment. Required
  when no NetBox VLAN is selected.
    - Values: `1-4094`

*Optional fields*:

- **NetBox VLAN**: an optional reference to a NetBox VLAN.
    - When set, its VID is used as the effective encap VLAN ID ahead of
      the snapshotted value, and is what the snapshot falls back to if
      the NetBox VLAN is later deleted.
    - Re-pointing an existing binding to a different NetBox VLAN
      requires clearing the Encap VLAN ID in the same edit, so the
      snapshot re-syncs to the new VLAN deliberately rather than
      silently keeping the stale value.
- **Primary NetBox VLAN**: an optional reference to a NetBox VLAN used
  as the primary VLAN when the deployment requires a paired
  encapsulation, for example for intra-EPG isolation. It follows the
  same snapshot and re-point rules as the main NetBox VLAN.
- **Primary encap VLAN ID**: the primary VLAN encapsulation, snapshotted
  the same way as the Encap VLAN ID.
    - Values: `1-4094`
- **Mode**: the VLAN tagging mode of the deployment.
    - Values: `regular` (Trunk), `native` (Access (802.1P)),
      `untagged` (Access (untagged))
    - Default: `regular`
- **Deployment immediacy**: when the policy is pushed into the leaf
  hardware (default *On Demand*).
- **Comments**: a text field for additional notes.
- **Tags**: a list of NetBox tags.

*Validation rules*:

- The assigned ACI AAEP must belong to the same ACI Fabric as the ACI
  Endpoint Group.
- The AAEP and the Endpoint Group must share at least one bound
  Physical Domain, or the fabric raises fault F0467.
- Either a NetBox VLAN or an Encap VLAN ID is required, and a NetBox
  VLAN paired with an Encap VLAN ID must agree with its VID.
- A single shared Physical Domain's ACI VLAN Pool must satisfy the
  whole encapsulation together: it has to cover both the encap VLAN ID
  and the primary encap VLAN ID, and its NetBox VLAN group, if set,
  has to admit both the main and the primary NetBox VLAN. These
  requirements cannot be split across different domains. One shared
  domain has to satisfy all of them.
- Each `(aci_endpoint_group, aci_aaep)` combination must be unique (an
  Endpoint Group cannot be deployed through the same AAEP twice).

The shared-domain requirement is only checked when the binding is
created or edited, not continuously afterwards. If a shared Physical
Domain is later unbound from either the Endpoint Group or the AAEP,
the binding is left in place rather than removed. It now reflects
fault F0467, the same fault APIC itself would raise, until a shared
domain exists again.

The binding is managed from both sides: the AAEP's detail page carries
the canonical **EPG Bindings** tab, and the Endpoint Group's detail
page shows the same bindings in reverse under the **AAEP Bindings**
tab.
