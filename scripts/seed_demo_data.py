# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Idempotent ACI demo data for local development.

Seeds two ACI Fabrics so cross-fabric behaviour is testable: Fabric1 is
fully built out with two Pods, SFP and RJ45 leaves, spines, APICs, vPC
pairs, access policies and two Tenants, while Fabric2 stays deliberately
thin. Every plugin model gets at least one row.

Names encode their scope. Fabric-scoped objects carry a fused fabric
prefix (F1Pod1, F1Leaf2101, F1AAEP1) and tenant-scoped objects carry a
fused fabric and tenant prefix followed by a hyphen (F1T1-BD1).

Node IDs follow the abcd scheme: a is the type (1 RJ45 leaf, 2 SFP leaf,
3 spine), b is the Pod ID and cd counts up from 01. APIC Nodes sit
outside that scheme because the model caps their Node ID at 100.

Run with: python netbox/manage.py shell < scripts/seed_demo_data.py
"""

from collections import Counter
from decimal import Decimal

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Model

from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    InterfaceTemplate,
    MACAddress,
    Manufacturer,
    Site,
)
from ipam.models import VLAN, VRF, IPAddress, Prefix, VLANGroup
from netbox_aci_plugin.models import (
    ACIVRF,
    ACIAAEPDomainBinding,
    ACIAppProfile,
    ACIAttachableAccessEntityProfile,
    ACIBridgeDomain,
    ACIBridgeDomainL3OutBinding,
    ACIBridgeDomainSubnet,
    ACIContract,
    ACIContractFilter,
    ACIContractFilterEntry,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
    ACIEndpointGroup,
    ACIEndpointGroupAAEPBinding,
    ACIEndpointGroupDomainBinding,
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIFabric,
    ACIL3Out,
    ACILeafInterfaceOverride,
    ACILeafInterfacePolicyGroup,
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafNodeBlock,
    ACILeafPortBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
    ACINode,
    ACINodeInterface,
    ACIPhysicalDomain,
    ACIPod,
    ACIRoutedDomain,
    ACITenant,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
    ACIVLANPool,
    ACIVLANPoolRange,
    ACIVPCProtectionGroup,
)
from tenancy.models import Tenant
from users.models import Owner

# Per-run tallies, keyed by model in the order the models are first touched.
SEED_STATS: dict[type, Counter] = {}

EXEMPT_MODELS: frozenset = frozenset()


def _differs(current, desired) -> bool:
    """Report whether a stored field value deviates from the declared one."""
    if current == desired:
        return False
    # Related objects compare by primary key. Two rows can share a label,
    # as two IP addresses in different VRFs do.
    if isinstance(current, Model) or isinstance(desired, Model):
        return True
    # IPNetworkField and friends hand back netaddr objects, never the plain
    # strings the specs declare.
    return str(current) != str(desired)


def ensure(model, defaults=None, **lookup):
    """Fetch or build one row, then converge it on the defaults.

    The lookup is the row's identity, the defaults its desired state. An
    adopted row is validated and reconciled, not left alone.
    """
    try:
        obj = model.objects.get(**lookup)
        created = False
    except model.DoesNotExist:
        obj = model(**lookup)
        created = True
    except model.MultipleObjectsReturned as error:
        raise RuntimeError(
            f"Ambiguous seed lookup for {model._meta.label}: {lookup}"
        ) from error

    changed = created
    for field_name, value in (defaults or {}).items():
        # getattr() on a freshly built row raises for a non-nullable FK.
        if created or _differs(getattr(obj, field_name), value):
            setattr(obj, field_name, value)
            changed = True

    obj.full_clean()
    if changed:
        obj.save()

    tally = SEED_STATS.setdefault(model, Counter())
    tally["created" if created else "updated" if changed else "unchanged"] += 1
    return obj


def check_model_coverage() -> None:
    """Fail the run when a plugin model never received a seed row."""
    plugin_models = set(apps.get_app_config("netbox_aci_plugin").get_models())
    missing = plugin_models - set(SEED_STATS) - EXEMPT_MODELS
    if missing:
        names = ", ".join(sorted(model.__name__ for model in missing))
        raise RuntimeError(f"Plugin models missing from the demo seed: {names}")


def gfk(field, obj):
    """Expand a generic foreign key into its content type and id pair."""
    return {
        f"{field}_type": ContentType.objects.get_for_model(obj),
        f"{field}_id": obj.pk,
    }


def ethernet_ports(first, last, iface_type):
    """Expand a contiguous front-panel port range into template specs."""
    return tuple(
        (f"Ethernet1/{index}", iface_type, False) for index in range(first, last + 1)
    )


def interface_templates(device_type, specs):
    """Create a device type's interface templates from its port layout."""
    for name, iface_type, mgmt_only in specs:
        ensure(
            InterfaceTemplate,
            {"type": iface_type, "mgmt_only": mgmt_only},
            device_type=device_type,
            name=name,
        )


def device_interfaces(device):
    """Create a device's interfaces from its device type templates."""
    return {
        template.name: ensure(
            Interface,
            {"type": template.type, "mgmt_only": template.mgmt_only},
            device=device,
            name=template.name,
        )
        for template in device.device_type.interfacetemplates.all()
    }


def seed_core():
    """Create the NetBox objects the ACI models reference."""
    owner = ensure(Owner, name="ACI Demo Owner")
    nb_tenant = ensure(Tenant, {"name": "ACI Demo"}, group=None, slug="aci-demo")
    cisco = ensure(Manufacturer, {"name": "Cisco"}, slug="cisco")

    sites = {
        key: ensure(Site, {"name": name}, slug=slug)
        for key, name, slug in (
            ("dc1", "ACI-Demo-DC1", "aci-demo-dc1"),
            ("dc2", "ACI-Demo-DC2", "aci-demo-dc2"),
            ("dc3", "ACI-Demo-DC3", "aci-demo-dc3"),
        )
    }
    roles = {
        key: ensure(DeviceRole, {"name": name}, parent=None, slug=slug)
        for key, name, slug in (
            ("leaf", "ACI Leaf", "aci-leaf"),
            ("spine", "ACI Spine", "aci-spine"),
            ("apic", "ACI Controller", "aci-controller"),
        )
    }
    # Device types mirror the NetBox Device Type Library, whose slug is the
    # part number lowercased and prefixed with the manufacturer.
    device_types = {
        key: ensure(
            DeviceType,
            {
                "model": model,
                "part_number": part_number,
                "u_height": u_height,
                "is_full_depth": True,
                "weight": weight,
                "weight_unit": "kg" if weight else "",
            },
            manufacturer=cisco,
            slug=f"cisco-{part_number.lower()}",
        )
        for key, model, part_number, u_height, weight in (
            ("rj45_leaf", "Nexus 9348GC-FXP", "N9K-C9348GC-FXP", 1, Decimal("6.44")),
            ("sfp_leaf", "Nexus 93180YC-FX3", "N9K-C93180YC-FX3", 1, Decimal("9.52")),
            ("spine", "Nexus 9364C", "N9K-C9364C", 2, Decimal("16.74")),
            ("apic", "APIC-L3", "APIC-L3", 1, None),
        )
    }
    for key, port_specs in (
        (
            "rj45_leaf",
            (
                *ethernet_ports(1, 48, "1000base-t"),
                *ethernet_ports(49, 52, "25gbase-x-sfp28"),
                *ethernet_ports(53, 54, "100gbase-x-qsfp28"),
                ("mgmt0", "1000base-t", True),
            ),
        ),
        (
            "sfp_leaf",
            (
                *ethernet_ports(1, 48, "25gbase-x-sfp28"),
                *ethernet_ports(49, 54, "100gbase-x-qsfp28"),
                ("mgmt0", "1000base-t", True),
            ),
        ),
        (
            "spine",
            (
                *ethernet_ports(1, 64, "100gbase-x-qsfp28"),
                *ethernet_ports(65, 66, "10gbase-x-sfpp"),
                ("mgmt0", "1000base-t", True),
            ),
        ),
        (
            # The APIC is a UCS appliance, so it carries no Ethernet1/N ports
            # and its management interface is the CIMC, not an mgmt0.
            "apic",
            (
                ("eth1-1", "10gbase-t", False),
                ("eth1-2", "10gbase-t", False),
                ("eth2-1", "25gbase-x-sfp28", False),
                ("eth2-2", "25gbase-x-sfp28", False),
                ("eth2-3", "25gbase-x-sfp28", False),
                ("eth2-4", "25gbase-x-sfp28", False),
                ("CIMC", "1000base-t", True),
            ),
        ),
    ):
        interface_templates(device_types[key], port_specs)

    vrf_underlay = ensure(VRF, {"name": "ACI-Demo-Underlay"}, rd="65010:1")
    # F1Infra-VRF1 is absent on purpose: it owns no bridge domain, so it keeps
    # an unmapped ACI VRF in the dataset.
    nb_vrfs = {
        aci_vrf_name: ensure(VRF, {"name": name}, rd=rd)
        for aci_vrf_name, name, rd in (
            ("F1Cmn-VRF1", "ACI-Demo-F1Cmn-VRF1", "65001:10"),
            ("F1Mgmt-VRF1", "ACI-Demo-F1Mgmt-VRF1", "65001:20"),
            ("F1T1-VRF1", "ACI-Demo-F1T1-VRF1", "65001:1"),
            ("F1T1-VRF2", "ACI-Demo-F1T1-VRF2", "65001:2"),
            ("F2T1-VRF1", "ACI-Demo-F2T1-VRF1", "65002:1"),
        )
    }

    vlan_groups = {
        key: ensure(
            VLANGroup, {"name": name}, scope_type=None, scope_id=None, slug=slug
        )
        for key, name, slug in (
            ("pool1", "ACI-Demo-F1-Pool1", "aci-demo-f1-pool1"),
            ("infra", "ACI-Demo-Infra", "aci-demo-infra"),
        )
    }
    infra_vlans = {
        vid: ensure(
            VLAN,
            {"name": f"ACI-Demo-Infra-{vid}"},
            group=vlan_groups["infra"],
            vid=vid,
        )
        for vid in (3900, 3000)
    }

    tep_pools = {
        key: ensure(Prefix, prefix=cidr, vrf=vrf_underlay)
        for key, cidr in (
            ("f1pod1", "10.0.0.0/16"),
            ("f1pod2", "10.1.0.0/16"),
            ("f2pod1", "10.100.0.0/16"),
        )
    }
    gipo_pools = {
        key: ensure(Prefix, prefix=cidr, vrf=None)
        for key, cidr in (("f1", "225.0.0.0/15"), ("f2", "225.2.0.0/15"))
    }

    return {
        "owner": owner,
        "nb_tenant": nb_tenant,
        "sites": sites,
        "roles": roles,
        "device_types": device_types,
        "vrf_underlay": vrf_underlay,
        "nb_vrfs": nb_vrfs,
        "vlan_groups": vlan_groups,
        "infra_vlans": infra_vlans,
        "tep_pools": tep_pools,
        "gipo_pools": gipo_pools,
    }


def seed_fabric(core):
    """Create ACI Fabrics, Pods, Nodes, Interfaces and VPC Groups."""
    fabrics = {
        "Fabric1": ensure(
            ACIFabric,
            {
                "fabric_id": 1,
                "infra_vlan_vid": 3900,
                "infra_vlan": core["infra_vlans"][3900],
                "gipo_pool": core["gipo_pools"]["f1"],
                "scope": core["sites"]["dc1"],
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                "description": "Primary demo fabric with two pods",
            },
            name="Fabric1",
        ),
        "Fabric2": ensure(
            ACIFabric,
            {
                "fabric_id": 2,
                "infra_vlan_vid": 3000,
                "infra_vlan": core["infra_vlans"][3000],
                "gipo_pool": core["gipo_pools"]["f2"],
                "scope": core["sites"]["dc3"],
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                "description": "Secondary demo fabric for isolation tests",
            },
            name="Fabric2",
        ),
    }

    pods = {
        name: ensure(
            ACIPod,
            {
                "pod_id": pod_id,
                "tep_pool": core["tep_pools"][tep_key],
                "scope": core["sites"][site_key],
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for name, fabric, pod_id, tep_key, site_key in (
            ("F1Pod1", "Fabric1", 1, "f1pod1", "dc1"),
            ("F1Pod2", "Fabric1", 2, "f1pod2", "dc2"),
            ("F2Pod1", "Fabric2", 1, "f2pod1", "dc3"),
        )
    }

    node_specs = (
        # name, pod, node_id, role, device type key, TEP IP
        ("F1Leaf1101", "F1Pod1", 1101, "leaf", "rj45_leaf", "10.0.1.101/16"),
        ("F1Leaf1102", "F1Pod1", 1102, "leaf", "rj45_leaf", "10.0.1.102/16"),
        ("F1Leaf2101", "F1Pod1", 2101, "leaf", "sfp_leaf", "10.0.2.101/16"),
        ("F1Leaf2102", "F1Pod1", 2102, "leaf", "sfp_leaf", "10.0.2.102/16"),
        ("F1Leaf2103", "F1Pod1", 2103, "leaf", "sfp_leaf", "10.0.2.103/16"),
        ("F1Leaf2104", "F1Pod1", 2104, "leaf", "sfp_leaf", "10.0.2.104/16"),
        ("F1Spine3101", "F1Pod1", 3101, "spine", "spine", "10.0.3.101/16"),
        ("F1Spine3102", "F1Pod1", 3102, "spine", "spine", "10.0.3.102/16"),
        ("F1APIC1", "F1Pod1", 1, "apic", "apic", None),
        ("F1APIC2", "F1Pod1", 2, "apic", "apic", None),
        ("F1APIC3", "F1Pod1", 3, "apic", "apic", None),
        ("F1Leaf2201", "F1Pod2", 2201, "leaf", "sfp_leaf", "10.1.2.201/16"),
        ("F1Leaf2202", "F1Pod2", 2202, "leaf", "sfp_leaf", "10.1.2.202/16"),
        ("F1Spine3201", "F1Pod2", 3201, "spine", "spine", "10.1.3.201/16"),
        ("F1Spine3202", "F1Pod2", 3202, "spine", "spine", "10.1.3.202/16"),
        ("F2Leaf2101", "F2Pod1", 2101, "leaf", "sfp_leaf", "10.100.2.101/16"),
        ("F2Leaf2102", "F2Pod1", 2102, "leaf", "sfp_leaf", "10.100.2.102/16"),
        ("F2Spine3101", "F2Pod1", 3101, "spine", "spine", "10.100.3.101/16"),
    )
    site_by_pod = {"F1Pod1": "dc1", "F1Pod2": "dc2", "F2Pod1": "dc3"}

    devices = {}
    nodes = {}
    for name, pod_name, node_id, role, dt_key, tep_cidr in node_specs:
        device = ensure(
            Device,
            {
                "device_type": core["device_types"][dt_key],
                "role": core["roles"][role],
            },
            name=name,
            site=core["sites"][site_by_pod[pod_name]],
            tenant=core["nb_tenant"],
        )
        devices[name] = device
        tep_ip = (
            ensure(
                IPAddress,
                address=tep_cidr,
                vrf=core["vrf_underlay"],
            )
            if tep_cidr
            else None
        )
        nodes[name] = ensure(
            ACINode,
            {
                "node_id": node_id,
                "role": role,
                "node_type": "unknown",
                "tep_ip_address": tep_ip,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                **gfk("node_object", device),
            },
            aci_pod=pods[pod_name],
            name=name,
        )

    node_interfaces = {}
    for name, _pod, _nid, role, _dt_key, _tep in node_specs:
        created = device_interfaces(devices[name])
        if role != "leaf":
            continue
        for port_number in (1, 2, 3):
            iface_name = f"Ethernet1/{port_number}"
            node_interfaces[f"{name}:{port_number}"] = ensure(
                ACINodeInterface,
                {
                    "nb_interface": created[iface_name],
                    "description": f"Access port {iface_name}",
                },
                aci_node=nodes[name],
                module=1,
                port=port_number,
                sub_port=0,
            )

    vpc_groups = {
        name: ensure(
            ACIVPCProtectionGroup,
            {
                "logical_pair_id": pair_id,
                "aci_node_a": nodes[node_a],
                "aci_node_b": nodes[node_b],
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                "description": f"vPC domain for {node_a} and {node_b}",
            },
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for name, fabric, pair_id, node_a, node_b in (
            ("F1VPC2101-2102", "Fabric1", 1, "F1Leaf2101", "F1Leaf2102"),
            ("F1VPC2103-2104", "Fabric1", 2, "F1Leaf2103", "F1Leaf2104"),
            ("F1VPC2201-2202", "Fabric1", 3, "F1Leaf2201", "F1Leaf2202"),
            ("F2VPC2101-2102", "Fabric2", 1, "F2Leaf2101", "F2Leaf2102"),
        )
    }

    return {
        "fabrics": fabrics,
        "pods": pods,
        "nodes": nodes,
        "node_interfaces": node_interfaces,
        "vpc_groups": vpc_groups,
    }


def seed_access_policies(core, fabrics, node_interfaces):
    """Create VLAN Pools, Domains, AAEPs, Policy Groups and both Profiles."""
    pools = {
        "F1Pool1": ensure(
            ACIVLANPool,
            {
                "allocation_mode": "static",
                "nb_vlan_group": core["vlan_groups"]["pool1"],
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                "description": "Static pool backing the physical domain",
            },
            aci_fabric=fabrics["Fabric1"],
            name="F1Pool1",
        ),
        "F1Pool2": ensure(
            ACIVLANPool,
            {"allocation_mode": "dynamic", "owner": core["owner"]},
            aci_fabric=fabrics["Fabric1"],
            name="F1Pool2",
        ),
        "F2Pool1": ensure(
            ACIVLANPool,
            {"allocation_mode": "static", "owner": core["owner"]},
            aci_fabric=fabrics["Fabric2"],
            name="F2Pool1",
        ),
    }
    for pool_name, vid_from, vid_to, mode, role in (
        ("F1Pool1", 100, 499, "inherit", "external"),
        ("F1Pool2", 500, 999, "dynamic", "internal"),
        ("F2Pool1", 100, 299, "inherit", "external"),
    ):
        ensure(
            ACIVLANPoolRange,
            {"allocation_mode": mode, "role": role},
            aci_vlan_pool=pools[pool_name],
            vlan_id_from=vid_from,
            vlan_id_to=vid_to,
        )

    phys_domains = {
        name: ensure(
            ACIPhysicalDomain,
            {
                "aci_vlan_pool": pools[pool_name],
                "security_domains": security_domains,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for name, fabric, pool_name, security_domains in (
            ("F1PhysDom1", "Fabric1", "F1Pool1", ["F1SecDom1"]),
            ("F1PhysDom2", "Fabric1", "F1Pool2", []),
            ("F2PhysDom1", "Fabric2", "F2Pool1", []),
        )
    }
    routed_domains = {
        name: ensure(
            ACIRoutedDomain,
            {"aci_vlan_pool": pools[pool_name], "owner": core["owner"]},
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for name, fabric, pool_name in (
            ("F1RoutDom1", "Fabric1", "F1Pool1"),
            ("F2RoutDom1", "Fabric2", "F2Pool1"),
        )
    }

    aaeps = {
        name: ensure(
            ACIAttachableAccessEntityProfile,
            {
                "infra_vlan": infra_vlan,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for name, fabric, infra_vlan in (
            ("F1AAEP1", "Fabric1", False),
            ("F1AAEP2", "Fabric1", True),
            ("F1AAEP3", "Fabric1", False),
            ("F2AAEP1", "Fabric2", False),
        )
    }
    domain_by_key = {**phys_domains, **routed_domains}
    for aaep_name, domain_name in (
        ("F1AAEP1", "F1PhysDom1"),
        ("F1AAEP1", "F1RoutDom1"),
        ("F1AAEP2", "F1PhysDom1"),
        ("F1AAEP3", "F1PhysDom1"),
        ("F2AAEP1", "F2PhysDom1"),
    ):
        ensure(
            ACIAAEPDomainBinding,
            aci_aaep=aaeps[aaep_name],
            **gfk("aci_domain_object", domain_by_key[domain_name]),
        )

    policy_groups = {
        name: ensure(
            ACILeafInterfacePolicyGroup,
            {
                "group_type": group_type,
                "aci_aaep": aaeps[aaep_name],
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                "description": description,
            },
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for name, fabric, group_type, aaep_name, description in (
            ("F1AccGrp1", "Fabric1", "access", "F1AAEP1", "Bare metal access"),
            ("F1PCGrp1", "Fabric1", "pc", "F1AAEP1", "Port channel"),
            ("F1VPCGrp1", "Fabric1", "vpc", "F1AAEP1", "vPC to pair 2101/2102"),
            ("F1VPCGrp2", "Fabric1", "vpc", "F1AAEP2", "vPC to pair 2103/2104"),
            ("F2AccGrp1", "Fabric2", "access", "F2AAEP1", "Bare metal access"),
        )
    }

    switch_profiles = {
        name: ensure(
            ACILeafSwitchProfile,
            {
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                "description": description,
            },
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for name, fabric, description in (
            ("F1SwProf1101-1102", "Fabric1", "RJ45 leaves outside any vPC pair"),
            ("F1SwProf2101-2104", "Fabric1", "Both Pod1 vPC pairs"),
            ("F1SwProf2201-2202", "Fabric1", "Pod2 vPC pair"),
            ("F2SwProf2101", "Fabric2", "Node ID shared with Fabric1"),
        )
    }
    selectors = {
        name: ensure(
            ACILeafSelector,
            {"nb_tenant": core["nb_tenant"], "owner": core["owner"]},
            aci_leaf_switch_profile=switch_profiles[profile_name],
            name=name,
        )
        for name, profile_name in (
            ("F1SwSel1101-1102", "F1SwProf1101-1102"),
            ("F1SwSel2101-2102", "F1SwProf2101-2104"),
            ("F1SwSel2103-2104", "F1SwProf2101-2104"),
            ("F1SwSel2201-2202", "F1SwProf2201-2202"),
            ("F2SwSel2101", "F2SwProf2101"),
        )
    }
    for name, selector_name, node_id_from, node_id_to in (
        ("F1NodeBlk1101-1102", "F1SwSel1101-1102", 1101, 1102),
        ("F1NodeBlk2101-2102", "F1SwSel2101-2102", 2101, 2102),
        ("F1NodeBlk2103-2104", "F1SwSel2103-2104", 2103, 2104),
        ("F1NodeBlk2201-2202", "F1SwSel2201-2202", 2201, 2202),
        ("F2NodeBlk2101", "F2SwSel2101", 2101, 2101),
    ):
        ensure(
            ACILeafNodeBlock,
            {
                "node_id_from": node_id_from,
                "node_id_to": node_id_to,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_leaf_selector=selectors[selector_name],
            name=name,
        )

    interface_profiles = {
        name: ensure(
            ACILeafInterfaceProfile,
            {
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                "description": description,
            },
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for name, fabric, description in (
            ("F1IntProf1101-1102", "Fabric1", "RJ45 leaves outside any vPC pair"),
            ("F1IntProf2101-2104", "Fabric1", "Both Pod1 vPC pairs"),
            ("F1IntProf2201-2202", "Fabric1", "Pod2 vPC pair"),
            ("F2IntProf2101", "Fabric2", "Node ID shared with Fabric1"),
        )
    }
    interface_selectors = {
        name: ensure(
            ACILeafInterfaceSelector,
            {
                "aci_leaf_interface_policy_group": policy_groups[group_name],
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_leaf_interface_profile=interface_profiles[profile_name],
            name=name,
        )
        for name, profile_name, group_name in (
            ("F1IntSel1101-1102Acc", "F1IntProf1101-1102", "F1AccGrp1"),
            ("F1IntSel2101-2102VPC", "F1IntProf2101-2104", "F1VPCGrp1"),
            ("F1IntSel2103-2104VPC", "F1IntProf2101-2104", "F1VPCGrp2"),
            ("F1IntSel2201-2202PC", "F1IntProf2201-2202", "F1PCGrp1"),
            ("F2IntSel2101Acc", "F2IntProf2101", "F2AccGrp1"),
        )
    }
    for name, selector_name, port_from, port_to in (
        ("F1PortBlk1101-1102Eth1-3", "F1IntSel1101-1102Acc", 1, 3),
        ("F1PortBlk2101-2102Eth1", "F1IntSel2101-2102VPC", 1, 1),
        ("F1PortBlk2103-2104Eth2", "F1IntSel2103-2104VPC", 2, 2),
        ("F1PortBlk2201-2202Eth3", "F1IntSel2201-2202PC", 3, 3),
        ("F2PortBlk2101Eth1-2", "F2IntSel2101Acc", 1, 2),
    ):
        ensure(
            ACILeafPortBlock,
            {
                "module_from": 1,
                "module_to": 1,
                "port_from": port_from,
                "port_to": port_to,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_leaf_interface_selector=interface_selectors[selector_name],
            name=name,
        )

    # F1IntProf2201-2202 is bound twice so the M:N shape is represented.
    for switch_profile_name, interface_profile_name in (
        ("F1SwProf1101-1102", "F1IntProf1101-1102"),
        ("F1SwProf1101-1102", "F1IntProf2201-2202"),
        ("F1SwProf2101-2104", "F1IntProf2101-2104"),
        ("F1SwProf2201-2202", "F1IntProf2201-2202"),
        ("F2SwProf2101", "F2IntProf2101"),
    ):
        ensure(
            ACILeafSwitchProfileInterfaceBinding,
            aci_leaf_switch_profile=switch_profiles[switch_profile_name],
            aci_leaf_interface_profile=interface_profiles[interface_profile_name],
        )

    # The Policy Group must be an Access group in the port's own Fabric.
    for interface_key, group_name, description in (
        ("F1Leaf1101:2", "F1AccGrp1", "Bare metal port outside its profile"),
        ("F1Leaf2101:3", "F1AccGrp1", "Access port on a vPC leaf"),
        ("F2Leaf2101:1", "F2AccGrp1", "Fabric2 access override"),
    ):
        ensure(
            ACILeafInterfaceOverride,
            {
                "aci_leaf_interface_policy_group": policy_groups[group_name],
                "description": description,
            },
            aci_node_interface=node_interfaces[interface_key],
        )

    return {
        "pools": pools,
        "phys_domains": phys_domains,
        "routed_domains": routed_domains,
        "aaeps": aaeps,
        "policy_groups": policy_groups,
        "switch_profiles": switch_profiles,
        "interface_profiles": interface_profiles,
        "interface_selectors": interface_selectors,
    }


def seed_tenants(core, fabrics):
    """Create ACI Tenants, VRFs, Bridge Domains and Application Profiles."""
    tenants = {
        key: ensure(
            ACITenant,
            {"nb_tenant": core["nb_tenant"], "owner": core["owner"]},
            aci_fabric=fabrics[fabric],
            name=name,
        )
        for key, fabric, name in (
            ("F1common", "Fabric1", "common"),
            ("F1infra", "Fabric1", "infra"),
            ("F1mgmt", "Fabric1", "mgmt"),
            ("F1T1", "Fabric1", "F1T1"),
            ("F1T2", "Fabric1", "F1T2"),
            ("F2common", "Fabric2", "common"),
            ("F2T1", "Fabric2", "F2T1"),
        )
    }
    vrf_specs = (
        # name, tenant key, direction, preference, preferred group, dns labels
        ("F1Cmn-VRF1", "F1common", "ingress", "enforced", False, None),
        ("F1Infra-VRF1", "F1infra", "ingress", "unenforced", False, None),
        ("F1Mgmt-VRF1", "F1mgmt", "ingress", "enforced", False, None),
        ("F1T1-VRF1", "F1T1", "ingress", "enforced", True, ["default"]),
        ("F1T1-VRF2", "F1T1", "egress", "unenforced", False, None),
        ("F2T1-VRF1", "F2T1", "ingress", "enforced", False, None),
    )
    vrfs = {}
    for name, tenant_key, direction, preference, group, labels in vrf_specs:
        vrfs[name] = ensure(
            ACIVRF,
            {
                "nb_vrf": core["nb_vrfs"].get(name),
                "pc_enforcement_direction": direction,
                "pc_enforcement_preference": preference,
                "preferred_group_enabled": group,
                "dns_labels": labels,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_tenant=tenants[tenant_key],
            name=name,
        )

    bd_specs = (
        # name, tenant key, VRF name, unknown unicast, host routes, arp flood
        ("F1Cmn-BD1", "F1common", "F1Cmn-VRF1", "proxy", False, False),
        ("F1Mgmt-BD1", "F1mgmt", "F1Mgmt-VRF1", "proxy", False, False),
        ("F1T1-BD1", "F1T1", "F1T1-VRF1", "proxy", True, False),
        ("F1T1-BD2", "F1T1", "F1T1-VRF1", "flood", False, True),
        ("F1T1-BD3", "F1T1", "F1T1-VRF2", "proxy", False, False),
        ("F2T1-BD1", "F2T1", "F2T1-VRF1", "proxy", False, False),
    )
    bds = {}
    for name, tenant_key, vrf_name, unicast, host_routes, arp_flood in bd_specs:
        bds[name] = ensure(
            ACIBridgeDomain,
            {
                "aci_vrf": vrfs[vrf_name],
                "unknown_unicast": unicast,
                "unknown_ipv4_multicast": "flood",
                "advertise_host_routes_enabled": host_routes,
                "arp_flooding_enabled": arp_flood,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_tenant=tenants[tenant_key],
            name=name,
        )

    for name, bd_name, gateway, preferred, advertised, shared in (
        ("F1T1-BD1-Sub1", "F1T1-BD1", "10.10.1.1/24", True, True, False),
        ("F1T1-BD1-Sub2", "F1T1-BD1", "10.10.2.1/24", False, False, False),
        ("F1T1-BD2-Sub1", "F1T1-BD2", "10.10.3.1/24", True, True, True),
        ("F1T1-BD3-Sub1", "F1T1-BD3", "10.10.4.1/24", True, False, False),
        ("F1Cmn-BD1-Sub1", "F1Cmn-BD1", "10.20.1.1/24", True, True, True),
        ("F2T1-BD1-Sub1", "F2T1-BD1", "10.30.1.1/24", True, False, False),
    ):
        ensure(
            ACIBridgeDomainSubnet,
            {
                "gateway_ip_address": ensure(
                    IPAddress,
                    address=gateway,
                    vrf=bds[bd_name].aci_vrf.nb_vrf,
                ),
                "preferred_ip_address_enabled": preferred,
                "advertised_externally_enabled": advertised,
                "shared_enabled": shared,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_bridge_domain=bds[bd_name],
            name=name,
        )

    aps = {
        name: ensure(
            ACIAppProfile,
            {"nb_tenant": core["nb_tenant"], "owner": core["owner"]},
            aci_tenant=tenants[tenant_key],
            name=name,
        )
        for name, tenant_key in (
            ("F1T1-AP1", "F1T1"),
            ("F1T1-AP2", "F1T1"),
            ("F1T2-AP1", "F1T2"),
            ("F2T1-AP1", "F2T1"),
        )
    }

    return {"tenants": tenants, "vrfs": vrfs, "bds": bds, "aps": aps}


def seed_l3outs(core, tenant, access):
    """Create L3Outs, External EPGs, External Subnets and BD Bindings."""
    l3outs = {
        "F1T1-L3Out1": ensure(
            ACIL3Out,
            {
                "aci_vrf": tenant["vrfs"]["F1T1-VRF1"],
                "aci_routed_domain": access["routed_domains"]["F1RoutDom1"],
                "bgp_enabled": True,
                "ospf_enabled": True,
                "eigrp_enabled": False,
                "import_route_control_enforcement_enabled": True,
                "export_route_control_enforcement_enabled": True,
                "ospf_external_policy_name": "F1T1-OSPFExt1",
                "target_dscp": "AF31",
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_tenant=tenant["tenants"]["F1T1"],
            name="F1T1-L3Out1",
        ),
        "F1Infra-L3Out1": ensure(
            ACIL3Out,
            {
                "aci_vrf": tenant["vrfs"]["F1Infra-VRF1"],
                "aci_routed_domain": access["routed_domains"]["F1RoutDom1"],
                "multipod_enabled": True,
                "export_route_control_enforcement_enabled": True,
                "owner": core["owner"],
                "description": "Inter-pod L3Out, only valid in tenant infra",
            },
            aci_tenant=tenant["tenants"]["F1infra"],
            name="F1Infra-L3Out1",
        ),
    }
    ext_epgs = {
        "F1T1-ExtEPG1": ensure(
            ACIExternalEndpointGroup,
            {
                "qos_class": "level1",
                "target_dscp": "unspecified",
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_l3out=l3outs["F1T1-L3Out1"],
            name="F1T1-ExtEPG1",
        ),
    }

    l3out_nb_vrf = l3outs["F1T1-L3Out1"].aci_vrf.nb_vrf

    # Order matters: Sub2 relies on the 0.0.0.0/0 default route (Sub1) already
    # being persisted, which ACIExternalSubnet.clean() checks via a DB query.
    ext_subnet_specs = (
        (
            "F1T1-ExtEPG1-Sub1",
            "0.0.0.0/0",
            None,
            {
                "import_route_control_enabled": True,
                "export_route_control_enabled": True,
                "shared_route_control_enabled": True,
                "import_security_enabled": True,
                "shared_security_enabled": True,
                "aggregate_import_route_control_enabled": True,
                "aggregate_export_route_control_enabled": True,
                "aggregate_shared_route_control_enabled": True,
            },
        ),
        (
            "F1T1-ExtEPG1-Sub2",
            "10.100.0.0/16",
            None,
            {
                "import_route_control_enabled": True,
                "export_route_control_enabled": True,
                "import_security_enabled": True,
                "shared_security_enabled": True,
                "bgp_route_summarization_enabled": True,
                "bgp_route_summarization_policy_name": "F1T1-BGPSum1",
            },
        ),
        (
            "F1T1-ExtEPG1-Sub3",
            "10.200.0.0/16",
            "10.200.0.0/16",
            {
                "export_route_control_enabled": True,
                "shared_route_control_enabled": True,
                "import_security_enabled": True,
                "shared_security_enabled": True,
                "aggregate_shared_route_control_enabled": True,
                "ospf_route_summarization_enabled": True,
                "ospf_route_summarization_policy_name": "F1T1-OSPFSum1",
            },
        ),
    )
    for name, matched, nb_prefix_cidr, flags in ext_subnet_specs:
        ensure(
            ACIExternalSubnet,
            {
                "matched_prefix": matched,
                "nb_prefix": (
                    ensure(Prefix, prefix=nb_prefix_cidr, vrf=l3out_nb_vrf)
                    if nb_prefix_cidr
                    else None
                ),
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
                **flags,
            },
            aci_external_endpoint_group=ext_epgs["F1T1-ExtEPG1"],
            name=name,
        )

    ensure(
        ACIBridgeDomainL3OutBinding,
        aci_bridge_domain=tenant["bds"]["F1T1-BD1"],
        aci_l3out=l3outs["F1T1-L3Out1"],
    )

    return {"l3outs": l3outs, "ext_epgs": ext_epgs}


def seed_endpoint_groups(core, tenant, access):
    """Create EPGs, uSeg EPGs, ESGs, Selectors and their Bindings."""
    epg_specs = (
        # name, app profile, bridge domain, QoS class, pref group, isolation
        ("F1T1-EPG1", "F1T1-AP1", "F1T1-BD1", "level1", True, False),
        ("F1T1-EPG2", "F1T1-AP1", "F1T1-BD1", "level2", False, False),
        ("F1T1-EPG3", "F1T1-AP1", "F1T1-BD1", "unspecified", False, True),
        ("F1T1-EPG4", "F1T1-AP1", "F1T1-BD1", "unspecified", False, False),
        ("F1T1-EPG5", "F1T1-AP2", "F1T1-BD3", "unspecified", False, False),
        ("F1T2-EPG1", "F1T2-AP1", "F1Cmn-BD1", "unspecified", False, False),
        ("F2T1-EPG1", "F2T1-AP1", "F2T1-BD1", "unspecified", False, False),
    )
    epgs = {}
    for name, ap_name, bd_name, qos_class, group, isolation in epg_specs:
        epgs[name] = ensure(
            ACIEndpointGroup,
            {
                "aci_bridge_domain": tenant["bds"][bd_name],
                "qos_class": qos_class,
                "preferred_group_member_enabled": group,
                "intra_epg_isolation_enabled": isolation,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_app_profile=tenant["aps"][ap_name],
            name=name,
        )
    useg_epgs = {
        "F1T1-uSeg1": ensure(
            ACIUSegEndpointGroup,
            {
                "aci_bridge_domain": tenant["bds"]["F1T1-BD2"],
                "match_operator": "any",
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_app_profile=tenant["aps"]["F1T1-AP1"],
            name="F1T1-uSeg1",
        ),
    }

    useg_nb_vrf = useg_epgs["F1T1-uSeg1"].aci_bridge_domain.aci_vrf.nb_vrf
    useg_ip = ensure(IPAddress, address="10.10.3.50/32", vrf=useg_nb_vrf)
    useg_prefix = ensure(Prefix, prefix="10.10.3.0/24", vrf=useg_nb_vrf)
    useg_mac = ensure(MACAddress, mac_address="00:50:56:AA:BB:CC")

    for attr_name, attr_object in (
        ("F1T1-uSeg1-Ip1", useg_ip),
        ("F1T1-uSeg1-Prefix1", useg_prefix),
        ("F1T1-uSeg1-Mac1", useg_mac),
    ):
        ensure(
            ACIUSegNetworkAttribute,
            {"owner": core["owner"], **gfk("attr_object", attr_object)},
            aci_useg_endpoint_group=useg_epgs["F1T1-uSeg1"],
            name=attr_name,
        )
    ensure(
        ACIUSegNetworkAttribute,
        {"use_epg_subnet": True, "owner": core["owner"]},
        aci_useg_endpoint_group=useg_epgs["F1T1-uSeg1"],
        name="F1T1-uSeg1-BdSubnet",
    )

    esgs = {
        name: ensure(
            ACIEndpointSecurityGroup,
            {
                "aci_vrf": tenant["vrfs"][vrf_name],
                "preferred_group_member_enabled": preferred_group,
                "intra_esg_isolation_enabled": intra_isolation,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_app_profile=tenant["aps"][ap_name],
            name=name,
        )
        for name, ap_name, vrf_name, preferred_group, intra_isolation in (
            ("F1T1-ESG1", "F1T1-AP1", "F1T1-VRF1", True, False),
            ("F1T1-ESG2", "F1T1-AP2", "F1T1-VRF2", False, True),
        )
    }
    for selector_name, epg_object in (
        ("F1T1-ESG1-EpgSel1", epgs["F1T1-EPG1"]),
        ("F1T1-ESG1-EpgSel2", useg_epgs["F1T1-uSeg1"]),
    ):
        ensure(
            ACIEsgEndpointGroupSelector,
            {"owner": core["owner"], **gfk("aci_epg_object", epg_object)},
            aci_endpoint_security_group=esgs["F1T1-ESG1"],
            name=selector_name,
        )
    for selector_name, ep_object in (
        ("F1T1-ESG1-EpSel1", useg_ip),
        ("F1T1-ESG1-EpSel2", useg_prefix),
    ):
        ensure(
            ACIEsgEndpointSelector,
            {"owner": core["owner"], **gfk("ep_object", ep_object)},
            aci_endpoint_security_group=esgs["F1T1-ESG1"],
            name=selector_name,
        )

    for epg_object, domain_name, deployment, resolution in (
        (epgs["F1T1-EPG1"], "F1PhysDom1", "lazy", "pre-provision"),
        (epgs["F1T1-EPG2"], "F1PhysDom1", "immediate", "immediate"),
        (epgs["F1T1-EPG3"], "F1PhysDom1", "lazy", "lazy"),
        (epgs["F1T1-EPG4"], "F1PhysDom1", "lazy", "lazy"),
        (useg_epgs["F1T1-uSeg1"], "F1PhysDom1", "lazy", "lazy"),
        (epgs["F2T1-EPG1"], "F2PhysDom1", "lazy", "lazy"),
    ):
        ensure(
            ACIEndpointGroupDomainBinding,
            {
                "deployment_immediacy": deployment,
                "resolution_immediacy": resolution,
            },
            **gfk("aci_epg_object", epg_object),
            **gfk("aci_domain_object", access["phys_domains"][domain_name]),
        )

    vlan_110 = ensure(
        VLAN,
        {"name": "ACI-Demo-F1T1-EPG1"},
        group=core["vlan_groups"]["pool1"],
        vid=110,
    )
    ensure(
        ACIEndpointGroupAAEPBinding,
        {"nb_vlan": vlan_110, "mode": "regular", "deployment_immediacy": "lazy"},
        aci_endpoint_group=epgs["F1T1-EPG1"],
        aci_aaep=access["aaeps"]["F1AAEP1"],
    )
    ensure(
        ACIEndpointGroupAAEPBinding,
        {
            "encap_vlan_id": 121,
            "primary_encap_vlan_id": 120,
            "mode": "regular",
            "deployment_immediacy": "immediate",
        },
        aci_endpoint_group=epgs["F1T1-EPG2"],
        aci_aaep=access["aaeps"]["F1AAEP1"],
    )
    ensure(
        ACIEndpointGroupAAEPBinding,
        {"encap_vlan_id": 130, "mode": "native", "deployment_immediacy": "lazy"},
        aci_endpoint_group=epgs["F1T1-EPG3"],
        aci_aaep=access["aaeps"]["F1AAEP2"],
    )
    ensure(
        ACIEndpointGroupAAEPBinding,
        {
            "encap_vlan_id": 140,
            "mode": "untagged",
            "deployment_immediacy": "immediate",
        },
        aci_endpoint_group=epgs["F1T1-EPG4"],
        aci_aaep=access["aaeps"]["F1AAEP3"],
    )

    return {"epgs": epgs, "useg_epgs": useg_epgs, "esgs": esgs}


def seed_contracts(core, tenant, endpoint, l3out):
    """Create Contract Filters, Contracts, Subjects and Relations."""
    filters = {
        "F1T1-Flt1": ensure(
            ACIContractFilter,
            {"nb_tenant": core["nb_tenant"], "owner": core["owner"]},
            aci_tenant=tenant["tenants"]["F1T1"],
            name="F1T1-Flt1",
        ),
        # Same name and entry the default-filter migration uses, so this
        # adopts that row when the migration created it.
        "F1Cmn-arp": ensure(
            ACIContractFilter,
            {"nb_tenant": core["nb_tenant"], "owner": core["owner"]},
            aci_tenant=tenant["tenants"]["F1common"],
            name="arp",
        ),
    }
    entry_specs = (
        (
            "tcp-app-syn-ack",
            {
                "ether_type": "ip",
                "ip_protocol": "tcp",
                "destination_from_port": "8080",
                "destination_to_port": "8090",
                "tcp_rules": ["syn", "ack"],
                "stateful_enabled": True,
            },
        ),
        (
            "tcp-ssh-established",
            {
                "ether_type": "ip",
                "ip_protocol": "tcp",
                "destination_from_port": "ssh",
                "destination_to_port": "ssh",
                "tcp_rules": ["est"],
            },
        ),
        (
            "udp-dns",
            {
                "ether_type": "ip",
                "ip_protocol": "udp",
                "destination_from_port": "dns",
                "destination_to_port": "dns",
            },
        ),
        (
            "icmpv4-echo",
            {"ether_type": "ipv4", "ip_protocol": "icmp", "icmp_v4_type": "echo"},
        ),
        (
            "icmpv6-nbr-solicit",
            {
                "ether_type": "ipv6",
                "ip_protocol": "icmpv6",
                "icmp_v6_type": "nbr-solicit",
            },
        ),
        ("arp-request", {"ether_type": "arp", "arp_opc": "req"}),
        (
            "ip-af31-fragments",
            {
                "ether_type": "ip",
                "match_dscp": "AF31",
                "match_only_fragments_enabled": True,
            },
        ),
    )
    for entry_name, entry_fields in entry_specs:
        ensure(
            ACIContractFilterEntry,
            {"owner": core["owner"], **entry_fields},
            aci_contract_filter=filters["F1T1-Flt1"],
            name=entry_name,
        )
    ensure(
        ACIContractFilterEntry,
        {"ether_type": "arp", "owner": core["owner"]},
        aci_contract_filter=filters["F1Cmn-arp"],
        name="arp",
    )

    contracts = {
        name: ensure(
            ACIContract,
            {
                "scope": scope,
                "qos_class": qos_class,
                "nb_tenant": core["nb_tenant"],
                "owner": core["owner"],
            },
            aci_tenant=tenant["tenants"][tenant_key],
            name=name,
        )
        for name, tenant_key, scope, qos_class in (
            ("F1T1-Ct1", "F1T1", "context", "level1"),
            ("F1T1-Ct2", "F1T1", "tenant", "unspecified"),
            ("F1Cmn-Ct1", "F1common", "global", "unspecified"),
        )
    }
    subject = ensure(
        ACIContractSubject,
        {
            "apply_both_directions_enabled": True,
            "reverse_filter_ports_enabled": True,
            "qos_class": "level1",
            "nb_tenant": core["nb_tenant"],
            "owner": core["owner"],
        },
        aci_contract=contracts["F1T1-Ct1"],
        name="F1T1-Ct1-Subj1",
    )
    for contract_filter, action, direction, priority in (
        (filters["F1T1-Flt1"], "permit", "both", "level1"),
        (filters["F1Cmn-arp"], "permit", "ctp", "default"),
    ):
        ensure(
            ACIContractSubjectFilter,
            {
                "action": action,
                "apply_direction": direction,
                "priority": priority,
                "log_enabled": True,
            },
            aci_contract_subject=subject,
            aci_contract_filter=contract_filter,
        )

    relation_specs = (
        ("F1T1-Ct1", endpoint["epgs"]["F1T1-EPG1"], "cons"),
        ("F1T1-Ct1", endpoint["epgs"]["F1T1-EPG2"], "prov"),
        ("F1T1-Ct1", endpoint["useg_epgs"]["F1T1-uSeg1"], "cons"),
        ("F1T1-Ct1", l3out["ext_epgs"]["F1T1-ExtEPG1"], "cons"),
        ("F1T1-Ct1", tenant["vrfs"]["F1T1-VRF1"], "prov"),
        ("F1T1-Ct2", endpoint["esgs"]["F1T1-ESG1"], "prov"),
        ("F1T1-Ct2", tenant["vrfs"]["F1T1-VRF2"], "cons"),
        ("F1Cmn-Ct1", endpoint["epgs"]["F1T2-EPG1"], "cons"),
    )
    for contract_name, aci_object, role in relation_specs:
        ensure(
            ACIContractRelation,
            aci_contract=contracts[contract_name],
            role=role,
            **gfk("aci_object", aci_object),
        )

    return {"contracts": contracts, "filters": filters}


with transaction.atomic():
    core = seed_core()
    fabric = seed_fabric(core)
    access = seed_access_policies(core, fabric["fabrics"], fabric["node_interfaces"])
    tenant = seed_tenants(core, fabric["fabrics"])
    l3out = seed_l3outs(core, tenant, access)
    endpoint = seed_endpoint_groups(core, tenant, access)
    seed_contracts(core, tenant, endpoint, l3out)
    check_model_coverage()

print("ACI demo data ready.")
print(f"  {'':<38}{'created':>9}{'updated':>9}{'unchanged':>11}")
for model, tally in SEED_STATS.items():
    print(
        f"  {model._meta.verbose_name_plural:.<38}"
        f"{tally['created']:>9}{tally['updated']:>9}{tally['unchanged']:>11}"
    )
