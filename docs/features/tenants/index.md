# Tenants

ACI fabric manages one or more *Tenants* based on the tenant portion of the
hierarchical management information tree (MIT).

```mermaid
flowchart TD
    TN([Tenant])
    AP(Application Profile)
    EPG(Endpoint Group)
    USEGEPG(uSeg Endpoint Group)
    USEGATTR(uSeg Attribute)
    ESG(Endpoint Security Group)
    ESGEPGSEL(ESG EPG Selector)
    ESGEPSEL(ESG EP Selector)
    VRF(VRF)
    BD(Bridge Domain)
    SN(Subnet)
    CT(Contract)
    CTR(Relation)
    SJ(Subject)
    SJF(Subject Filter)
    FT(Filter)
    FTE(Filter Entry)
    L3O(L3Out)
    EXTEPG(External Endpoint Group)
    EXTSN(External Subnet)
    subgraph graphTN [Tenant]
        TN
    end
    subgraph graphAP [Application Profile]
        AP
        TN -->|1:n| AP
        AP -->|1:n| EPG
        AP -->|1:n| USEGEPG
        subgraph graphEPG [Endpoint Group]
            EPG
            USEGEPG -->|1:n| USEGATTR
        end
        AP -->|1:n| ESG
        subgraph graphESG [Endpoint Security Group]
            ESG
            ESG -->|1:n| ESGEPGSEL
            ESG -->|1:n| ESGEPSEL
        end
    end
    subgraph graphNW [Network]
        TN -->|1:n| VRF
        subgraph graphVRF [VRF]
            VRF
        end
        BD -.->|n:1| VRF
        subgraph graphBD [Bridge Domain]
            TN -->|1:n| BD
            BD -->|1:n| SN
        end
        subgraph graphL3O [L3Out]
            TN -->|1:n| L3O
            L3O -->|1:n| EXTEPG
            EXTEPG -->|1:n| EXTSN
        end
        L3O -.->|n:1| VRF
    end
    subgraph graphCT [Contract]
        subgraph graphCTS [Contract]
            TN -->|1:n| CT
            CT -->|1:n| SJ
            CT -->|1:n| CTR
            SJ -->|1:n| SJF
        end
        subgraph graphFT [Filter]
            TN -->|1:n| FT
            FT -->|1:n| FTE
        end
        SJF -.->|n:1| FT
        CTR -.->|n:1| EPG
        CTR -.->|n:1| USEGEPG
        CTR -.->|n:1| ESG
        CTR -.->|n:1| VRF
        CTR -.->|n:1| EXTEPG
    end
    EPG -.->|n:1| BD
    USEGEPG -.->|n:1| BD
    ESG -.->|n:1| VRF
    ESGEPGSEL -.->|n:1| EPG
```

## Tenant

A *Tenant* in the ACI policy model represents a container for application
policies with domain-based access control.
Tenants can be modeled after customers, organizations, domains, or used to
group policies.

The *ACITenant* model has the following fields:

*Required fields*:

- **Name**: represent the Tenant name in the ACI.
- **ACI Fabric**: a reference to the `ACIFabric` model.

*Optional fields*:

- **Name alias**: a name alias in the ACI.
- **Description**: a description of the ACI Tenant.
- **NetBox Tenant**: an assignment to the NetBox tenant model.
- **Comments**: a text field for additional notes.
- **Tags**: a list of NetBox tags.
