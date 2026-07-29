# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from netbox.graphql.types import NetBoxObjectType
from users.graphql.mixins import OwnerMixin

from .. import models
from .filters import (
    ACIAAEPDomainBindingFilter,
    ACIAppProfileFilter,
    ACIAttachableAccessEntityProfileFilter,
    ACIBridgeDomainFilter,
    ACIBridgeDomainL3OutBindingFilter,
    ACIBridgeDomainSubnetFilter,
    ACIContractFilter,
    ACIContractFilterEntryFilter,
    ACIContractFilterFilter,
    ACIContractRelationFilter,
    ACIContractSubjectFilter,
    ACIContractSubjectFilterFilter,
    ACIEndpointGroupAAEPBindingFilter,
    ACIEndpointGroupDomainBindingFilter,
    ACIEndpointGroupFilter,
    ACIEndpointSecurityGroupFilter,
    ACIEsgEndpointGroupSelectorFilter,
    ACIEsgEndpointSelectorFilter,
    ACIExternalEndpointGroupFilter,
    ACIExternalSubnetFilter,
    ACIFabricFilter,
    ACIL3OutFilter,
    ACILeafInterfacePolicyGroupFilter,
    ACINodeFilter,
    ACINodeInterfaceFilter,
    ACIPhysicalDomainFilter,
    ACIPodFilter,
    ACIRoutedDomainFilter,
    ACITenantFilter,
    ACIUSegEndpointGroupFilter,
    ACIUSegNetworkAttributeFilter,
    ACIVLANPoolFilter,
    ACIVLANPoolRangeFilter,
    ACIVPCProtectionGroupFilter,
    ACIVRFFilter,
)

if TYPE_CHECKING:
    from dcim.graphql.types import (
        DeviceType,
        InterfaceType,
        LocationType,
        MACAddressType,
        RegionType,
        SiteGroupType,
        SiteType,
    )
    from ipam.graphql.types import (
        IPAddressType,
        PrefixType,
        VLANGroupType,
        VLANType,
        VRFType,
    )
    from tenancy.graphql.types import TenantType
    from virtualization.graphql.types import VirtualMachineType


@strawberry_django.type(
    models.ACIFabric,
    exclude=["scope_type", "scope_id", "_location", "_region", "_site", "_site_group"],
    filters=ACIFabricFilter,
    pagination=True,
)
class ACIFabricType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIFabric model."""

    # Model fields
    infra_vlan: Annotated["VLANType", strawberry.lazy("ipam.graphql.types")] | None
    gipo_pool: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry_django.field(description="Scope Object")
    def scope(
        self,
    ) -> (
        Annotated[
            Annotated["LocationType", strawberry.lazy("dcim.graphql.types")]
            | Annotated["RegionType", strawberry.lazy("dcim.graphql.types")]
            | Annotated["SiteGroupType", strawberry.lazy("dcim.graphql.types")]
            | Annotated["SiteType", strawberry.lazy("dcim.graphql.types")],
            strawberry.union("ACIFabricScopeType"),
        ]
        | None
    ):
        """Return the scope object."""
        return self.scope  # pragma: no cover

    # Related models
    aci_aaeps: list[
        Annotated[
            "ACIAttachableAccessEntityProfileType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_leaf_interface_policy_groups: list[
        Annotated[
            "ACILeafInterfacePolicyGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_physical_domains: list[
        Annotated[
            "ACIPhysicalDomainType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_pods: list[
        Annotated["ACIPodType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
    ]
    aci_routed_domains: list[
        Annotated[
            "ACIRoutedDomainType", strawberry.lazy("netbox_aci_plugin.graphql.types")
        ]
    ]
    aci_vlan_pools: list[
        Annotated["ACIVLANPoolType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
    ]
    aci_vpc_protection_groups: list[
        Annotated[
            "ACIVPCProtectionGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIPod,
    exclude=["scope_type", "scope_id", "_location", "_region", "_site", "_site_group"],
    filters=ACIPodFilter,
    pagination=True,
)
class ACIPodType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIPod model."""

    # Model fields
    aci_fabric: (
        Annotated["ACIFabricType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
        | None
    )
    tep_pool: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry_django.field(description="Scope Object")
    def scope(
        self,
    ) -> (
        Annotated[
            Annotated["LocationType", strawberry.lazy("dcim.graphql.types")]
            | Annotated["RegionType", strawberry.lazy("dcim.graphql.types")]
            | Annotated["SiteGroupType", strawberry.lazy("dcim.graphql.types")]
            | Annotated["SiteType", strawberry.lazy("dcim.graphql.types")],
            strawberry.union("ACIPodScopeType"),
        ]
        | None
    ):
        """Return the scope object."""
        return self.scope  # pragma: no cover

    # Related models
    aci_nodes: list[
        Annotated["ACINodeType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
    ]


@strawberry_django.type(
    models.ACINode,
    exclude=[
        "node_object_type",
        "node_object_id",
        "_aci_fabric",
        "_device",
        "_virtual_machine",
    ],
    filters=ACINodeFilter,
    pagination=True,
)
class ACINodeType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACINode model."""

    # Model fields
    aci_pod: (
        Annotated["ACIPodType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
        | None
    )
    tep_ip_address: (
        Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")] | None
    )
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry_django.field(description="Node Object")
    def node_object(
        self,
    ) -> (
        Annotated[
            Annotated["DeviceType", strawberry.lazy("dcim.graphql.types")]
            | Annotated[
                "VirtualMachineType", strawberry.lazy("virtualization.graphql.types")
            ],
            strawberry.union("ACINodeNodeObjectType"),
        ]
        | None
    ):
        """Return the node_object object."""
        return self.node_object  # pragma: no cover

    # Related models
    aci_node_interfaces: list[
        Annotated[
            "ACINodeInterfaceType", strawberry.lazy("netbox_aci_plugin.graphql.types")
        ]
    ]


@strawberry_django.type(
    models.ACINodeInterface,
    fields="__all__",
    filters=ACINodeInterfaceFilter,
    pagination=True,
)
class ACINodeInterfaceType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACINodeInterface model."""

    # Model fields
    aci_node: Annotated[
        "ACINodeType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_interface: (
        Annotated["InterfaceType", strawberry.lazy("dcim.graphql.types")] | None
    )
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry_django.field(description="Interface Token")
    def interface_token(self) -> str:
        """Return the normalized APIC interface token."""
        return self.interface_token  # pragma: no cover


@strawberry_django.type(
    models.ACIVPCProtectionGroup,
    fields="__all__",
    filters=ACIVPCProtectionGroupFilter,
    pagination=True,
)
class ACIVPCProtectionGroupType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIVPCProtectionGroup model."""

    # Model fields
    aci_fabric: Annotated[
        "ACIFabricType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_node_a: Annotated[
        "ACINodeType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_node_b: Annotated[
        "ACINodeType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None


@strawberry_django.type(
    models.ACIAttachableAccessEntityProfile,
    fields="__all__",
    filters=ACIAttachableAccessEntityProfileFilter,
    pagination=True,
)
class ACIAttachableAccessEntityProfileType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACI AAEP model."""

    # Model fields
    aci_fabric: Annotated[
        "ACIFabricType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_aaep_domain_bindings: list[
        Annotated[
            "ACIAAEPDomainBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_group_bindings: list[
        Annotated[
            "ACIEndpointGroupAAEPBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_leaf_interface_policy_groups: list[
        Annotated[
            "ACILeafInterfacePolicyGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIAAEPDomainBinding,
    exclude=[
        "aci_domain_object_id",
        "aci_domain_object_type",
        "_aci_physical_domain",
        "_aci_routed_domain",
    ],
    filters=ACIAAEPDomainBindingFilter,
    pagination=True,
)
class ACIAAEPDomainBindingType(NetBoxObjectType):
    """GraphQL type definition for the ACIAAEPDomainBinding model."""

    # Model fields
    aci_aaep: Annotated[
        "ACIAttachableAccessEntityProfileType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]

    @strawberry_django.field(description="ACI Domain Object")
    def aci_domain_object(
        self,
    ) -> (
        Annotated[
            Annotated[
                "ACIPhysicalDomainType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIRoutedDomainType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ],
            strawberry.union("ACIAAEPDomainBindingObjectType"),
        ]
        | None
    ):
        """Return the ACI Domain object."""
        return self.aci_domain_object  # pragma: no cover


@strawberry_django.type(
    models.ACILeafInterfacePolicyGroup,
    fields="__all__",
    filters=ACILeafInterfacePolicyGroupFilter,
    pagination=True,
)
class ACILeafInterfacePolicyGroupType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACILeafInterfacePolicyGroup model."""

    # Model fields
    aci_fabric: Annotated[
        "ACIFabricType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_aaep: (
        Annotated[
            "ACIAttachableAccessEntityProfileType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
        | None
    )
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None


@strawberry_django.type(
    models.ACIPhysicalDomain,
    fields="__all__",
    filters=ACIPhysicalDomainFilter,
    pagination=True,
)
class ACIPhysicalDomainType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIPhysicalDomain model."""

    # Model fields
    aci_fabric: Annotated[
        "ACIFabricType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    aci_vlan_pool: (
        Annotated["ACIVLANPoolType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
        | None
    )
    security_domains: list[str] | None

    # Related models
    aci_aaep_domain_bindings: list[
        Annotated[
            "ACIAAEPDomainBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_group_domain_bindings: list[
        Annotated[
            "ACIEndpointGroupDomainBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIRoutedDomain,
    fields="__all__",
    filters=ACIRoutedDomainFilter,
    pagination=True,
)
class ACIRoutedDomainType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIRoutedDomain model."""

    # Model fields
    aci_fabric: Annotated[
        "ACIFabricType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    aci_vlan_pool: (
        Annotated["ACIVLANPoolType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
        | None
    )
    security_domains: list[str] | None

    # Related models
    aci_aaep_domain_bindings: list[
        Annotated[
            "ACIAAEPDomainBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIVLANPool,
    fields="__all__",
    filters=ACIVLANPoolFilter,
    pagination=True,
)
class ACIVLANPoolType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIVLANPool model."""

    # Model fields
    aci_fabric: Annotated[
        "ACIFabricType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    nb_vlan_group: (
        Annotated["VLANGroupType", strawberry.lazy("ipam.graphql.types")] | None
    )

    # Related models
    aci_vlan_pool_ranges: list[
        Annotated[
            "ACIVLANPoolRangeType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIVLANPoolRange,
    fields="__all__",
    filters=ACIVLANPoolRangeFilter,
    pagination=True,
)
class ACIVLANPoolRangeType(NetBoxObjectType):
    """GraphQL type definition for the ACIVLANPoolRange model."""

    # Model fields
    aci_vlan_pool: Annotated[
        "ACIVLANPoolType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]


@strawberry_django.type(
    models.ACITenant, fields="__all__", filters=ACITenantFilter, pagination=True
)
class ACITenantType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACITenant model."""

    # Model fields
    aci_fabric: (
        Annotated["ACIFabricType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
        | None
    )
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_app_profiles: list[
        Annotated[
            "ACIAppProfileType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_bridge_domains: list[
        Annotated[
            "ACIBridgeDomainType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contracts: list[
        Annotated[
            "ACIContractType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_filters: list[
        Annotated[
            "ACIContractFilterType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_l3outs: list[
        Annotated["ACIL3OutType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
    ]
    aci_vrfs: list[
        Annotated["ACIVRFType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
    ]


@strawberry_django.type(
    models.ACIAppProfile, fields="__all__", filters=ACIAppProfileFilter, pagination=True
)
class ACIAppProfileType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIAppProfile model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_endpoint_groups: list[
        Annotated[
            "ACIEndpointGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_security_groups: list[
        Annotated[
            "ACIEndpointSecurityGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_useg_endpoint_groups: list[
        Annotated[
            "ACIUSegEndpointGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIVRF, fields="__all__", filters=ACIVRFFilter, pagination=True
)
class ACIVRFType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIVRF model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    nb_vrf: Annotated["VRFType", strawberry.lazy("ipam.graphql.types")] | None
    dns_labels: list[str] | None

    # Related models
    aci_bridge_domains: list[
        Annotated[
            "ACIBridgeDomainType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_security_groups: list[
        Annotated[
            "ACIEndpointSecurityGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIBridgeDomain,
    fields="__all__",
    filters=ACIBridgeDomainFilter,
    pagination=True,
)
class ACIBridgeDomainType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIBridgeDomain model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_vrf: Annotated["ACIVRFType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    dhcp_labels: list[str] | None
    mac_address: str | None
    virtual_mac_address: str | None

    # Related models
    aci_bridge_domain_subnets: list[
        Annotated[
            "ACIBridgeDomainSubnetType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_groups: list[
        Annotated[
            "ACIEndpointGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_l3out_bindings: list[
        Annotated[
            "ACIBridgeDomainL3OutBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIBridgeDomainSubnet,
    fields="__all__",
    filters=ACIBridgeDomainSubnetFilter,
    pagination=True,
)
class ACIBridgeDomainSubnetType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIBridgeDomainSubnet model."""

    # Model fields
    aci_bridge_domain: Annotated[
        "ACIBridgeDomainType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    gateway_ip_address: Annotated[
        "IPAddressType", strawberry.lazy("ipam.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None


@strawberry_django.type(
    models.ACIL3Out, fields="__all__", filters=ACIL3OutFilter, pagination=True
)
class ACIL3OutType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIL3Out model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_vrf: Annotated["ACIVRFType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
    aci_routed_domain: Annotated[
        "ACIRoutedDomainType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_external_endpoint_groups: list[
        Annotated[
            "ACIExternalEndpointGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_bridge_domain_bindings: list[
        Annotated[
            "ACIBridgeDomainL3OutBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIExternalEndpointGroup,
    fields="__all__",
    filters=ACIExternalEndpointGroupFilter,
    pagination=True,
)
class ACIExternalEndpointGroupType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIExternalEndpointGroup model."""

    # Model fields
    aci_l3out: Annotated[
        "ACIL3OutType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_external_subnets: list[
        Annotated[
            "ACIExternalSubnetType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIExternalSubnet,
    fields="__all__",
    filters=ACIExternalSubnetFilter,
    pagination=True,
)
class ACIExternalSubnetType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIExternalSubnet model."""

    # Model fields
    aci_external_endpoint_group: Annotated[
        "ACIExternalEndpointGroupType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    matched_prefix: str | None
    nb_prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None


@strawberry_django.type(
    models.ACIBridgeDomainL3OutBinding,
    fields="__all__",
    filters=ACIBridgeDomainL3OutBindingFilter,
    pagination=True,
)
class ACIBridgeDomainL3OutBindingType(NetBoxObjectType):
    """GraphQL type definition for the ACIBridgeDomainL3OutBinding model."""

    # Model fields
    aci_bridge_domain: Annotated[
        "ACIBridgeDomainType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    aci_l3out: Annotated[
        "ACIL3OutType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]


@strawberry_django.type(
    models.ACIEndpointGroup,
    fields="__all__",
    filters=ACIEndpointGroupFilter,
    pagination=True,
)
class ACIEndpointGroupType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIEndpointGroup model."""

    # Model fields
    aci_app_profile: Annotated[
        "ACIAppProfileType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_bridge_domain: Annotated[
        "ACIBridgeDomainType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_group_domain_bindings: list[
        Annotated[
            "ACIEndpointGroupDomainBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_aaep_bindings: list[
        Annotated[
            "ACIEndpointGroupAAEPBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIUSegEndpointGroup,
    fields="__all__",
    filters=ACIUSegEndpointGroupFilter,
    pagination=True,
)
class ACIUSegEndpointGroupType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIUSegEndpointGroup model."""

    # Model fields
    aci_app_profile: Annotated[
        "ACIAppProfileType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_bridge_domain: Annotated[
        "ACIBridgeDomainType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_useg_network_attributes: list[
        Annotated[
            "ACIUSegNetworkAttributeType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_group_domain_bindings: list[
        Annotated[
            "ACIEndpointGroupDomainBindingType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIUSegNetworkAttribute,
    exclude=[
        "attr_object_id",
        "attr_object_type",
        "_ip_address",
        "_mac_address",
        "_prefix",
    ],
    filters=ACIUSegNetworkAttributeFilter,
    pagination=True,
)
class ACIUSegNetworkAttributeType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIUSegNetworkAttribute model."""

    # Model fields
    aci_useg_endpoint_group: Annotated[
        "ACIUSegEndpointGroupType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry_django.field(description="Attribute Object")
    def attr_object(
        self,
    ) -> (
        Annotated[
            Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")]
            | Annotated["MACAddressType", strawberry.lazy("dcim.graphql.types")]
            | Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")],
            strawberry.union("ACIUSegNetworkAttributeObjectType"),
        ]
        | None
    ):
        """Return the attribute object."""
        return self.attr_object  # pragma: no cover


@strawberry_django.type(
    models.ACIEndpointGroupDomainBinding,
    exclude=[
        "aci_epg_object_id",
        "aci_epg_object_type",
        "aci_domain_object_id",
        "aci_domain_object_type",
        "_aci_endpoint_group",
        "_aci_useg_endpoint_group",
        "_aci_physical_domain",
    ],
    filters=ACIEndpointGroupDomainBindingFilter,
    pagination=True,
)
class ACIEndpointGroupDomainBindingType(NetBoxObjectType):
    """GraphQL type definition for the ACIEndpointGroupDomainBinding model."""

    @strawberry_django.field(description="ACI EPG Object")
    def aci_epg_object(
        self,
    ) -> (
        Annotated[
            Annotated[
                "ACIEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIUSegEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ],
            strawberry.union("ACIEndpointGroupDomainBindingEpgObjectType"),
        ]
        | None
    ):
        """Return the ACI EPG object."""
        return self.aci_epg_object  # pragma: no cover

    @strawberry_django.field(description="ACI Domain Object")
    def aci_domain_object(
        self,
    ) -> (
        Annotated[
            "ACIPhysicalDomainType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
        | None
    ):
        """Return the ACI Domain object."""
        return self.aci_domain_object  # pragma: no cover


@strawberry_django.type(
    models.ACIEndpointGroupAAEPBinding,
    fields="__all__",
    filters=ACIEndpointGroupAAEPBindingFilter,
    pagination=True,
)
class ACIEndpointGroupAAEPBindingType(NetBoxObjectType):
    """GraphQL type definition for the ACIEndpointGroupAAEPBinding model."""

    # Model fields
    aci_endpoint_group: Annotated[
        "ACIEndpointGroupType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_aaep: Annotated[
        "ACIAttachableAccessEntityProfileType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_vlan: Annotated["VLANType", strawberry.lazy("ipam.graphql.types")] | None
    primary_nb_vlan: Annotated["VLANType", strawberry.lazy("ipam.graphql.types")] | None


@strawberry_django.type(
    models.ACIEndpointSecurityGroup,
    fields="__all__",
    filters=ACIEndpointSecurityGroupFilter,
    pagination=True,
)
class ACIEndpointSecurityGroupType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIEndpointSecurityGroup model."""

    # Model fields
    aci_app_profile: Annotated[
        "ACIAppProfileType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_vrf: Annotated[
        "ACIVRFType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_esg_endpoint_group_selectors: list[
        Annotated[
            "ACIEsgEndpointGroupSelectorType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_esg_endpoint_selectors: list[
        Annotated[
            "ACIEsgEndpointSelectorType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIEsgEndpointGroupSelector,
    exclude=[
        "aci_epg_object_id",
        "aci_epg_object_type",
        "_aci_endpoint_group",
        "_aci_useg_endpoint_group",
    ],
    filters=ACIEsgEndpointGroupSelectorFilter,
    pagination=True,
)
class ACIEsgEndpointGroupSelectorType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIEsgEndpointGroupSelector model."""

    # Model fields
    aci_endpoint_security_group: Annotated[
        "ACIEndpointSecurityGroupType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry_django.field(description="Endpoint Group Object")
    def aci_epg_object(
        self,
    ) -> (
        Annotated[
            Annotated[
                "ACIEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIUSegEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ],
            strawberry.union("ACIEsgEndpointGroupSelectorObjectType"),
        ]
        | None
    ):
        """Return the Endpoint Group object."""
        return self.aci_epg_object  # pragma: no cover


@strawberry_django.type(
    models.ACIEsgEndpointSelector,
    exclude=[
        "ep_object_id",
        "ep_object_type",
        "_ip_address",
        "_prefix",
    ],
    filters=ACIEsgEndpointSelectorFilter,
    pagination=True,
)
class ACIEsgEndpointSelectorType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIEsgEndpointSelector model."""

    # Model fields
    aci_endpoint_security_group: Annotated[
        "ACIEndpointSecurityGroupType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry_django.field(description="Endpoint Object")
    def ep_object(
        self,
    ) -> (
        Annotated[
            Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")]
            | Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")],
            strawberry.union("ACIEsgEndpointSelectorObjectType"),
        ]
        | None
    ):
        """Return the Endpoint object."""
        return self.ep_object  # pragma: no cover


@strawberry_django.type(
    models.ACIContractFilter,
    fields="__all__",
    filters=ACIContractFilterFilter,
    pagination=True,
)
class ACIContractFilterType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIContractFilter model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_filter_entries: list[
        Annotated[
            "ACIContractFilterEntryType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_subject_filters: list[
        Annotated[
            "ACIContractSubjectFilterType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIContractFilterEntry,
    fields="__all__",
    filters=ACIContractFilterEntryFilter,
    pagination=True,
)
class ACIContractFilterEntryType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIContractFilterEntry model."""

    # Model fields
    aci_contract_filter: Annotated[
        "ACIContractFilterType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None


@strawberry_django.type(
    models.ACIContract,
    fields="__all__",
    filters=ACIContractFilter,
    pagination=True,
)
class ACIContractType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIContract model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_subjects: list[
        Annotated[
            "ACIContractSubjectType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIContractRelation,
    exclude=[
        "aci_object_id",
        "aci_object_type",
        "_aci_endpoint_group",
        "_aci_endpoint_security_group",
        "_aci_useg_endpoint_group",
        "_aci_external_endpoint_group",
        "_aci_vrf",
    ],
    filters=ACIContractRelationFilter,
    pagination=True,
)
class ACIContractRelationType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractRelation model."""

    # Model fields
    aci_contract: Annotated[
        "ACIContractType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]

    @strawberry_django.field(description="ACI Object")
    def aci_object(
        self,
    ) -> (
        Annotated[
            Annotated[
                "ACIEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIEndpointSecurityGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIExternalEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIUSegEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIVRFType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ],
            strawberry.union("ACIContractRelationObjectType"),
        ]
        | None
    ):
        """Return the ACI object."""
        return self.aci_object  # pragma: no cover


@strawberry_django.type(
    models.ACIContractSubject,
    fields="__all__",
    filters=ACIContractSubjectFilter,
    pagination=True,
)
class ACIContractSubjectType(OwnerMixin, NetBoxObjectType):
    """GraphQL type definition for the ACIContractSubject model."""

    # Model fields
    aci_contract: Annotated[
        "ACIContractType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_subject_filters: list[
        Annotated[
            "ACIContractSubjectFilterType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIContractSubjectFilter,
    fields="__all__",
    filters=ACIContractSubjectFilterFilter,
    pagination=True,
)
class ACIContractSubjectFilterType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractSubjectFilter model."""

    # Model fields
    aci_contract_filter: Annotated[
        "ACIContractFilterType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    aci_contract_subject: Annotated[
        "ACIContractSubjectType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
