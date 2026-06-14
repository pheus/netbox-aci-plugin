# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for tenant Bridge Domain binding models."""

from ipam.models import IPAddress
from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainL3OutBinding,
    ACIBridgeDomainSubnet,
)
from ....models.tenant.l3outs import ACIL3Out
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIModelViewTestCase


class ACIBridgeDomainL3OutBindingViewTestCase(
    ACIModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """Standard view tests for ACIBridgeDomainL3OutBinding.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    binding has no ``name`` field.
    """

    model = ACIBridgeDomainL3OutBinding

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        # ACIRoutedDomain is required for every ACIL3Out
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIViewTestBindingRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )

        # 5 additional Bridge Domains (base class already provides cls.aci_bd
        # as the 1st). All share the same fabric / tenant / VRF so the
        # binding clean() passes when paired with any matching L3Out.
        extra_bds = [
            ACIBridgeDomain.objects.create(
                name=f"ACIViewTestBindingBD{i}",
                aci_tenant=cls.aci_tenant,
                aci_vrf=cls.aci_vrf,
            )
            for i in range(2, 7)
        ]
        cls.bds = [cls.aci_bd, *extra_bds]

        # 6 L3Outs in the same tenant + VRF
        cls.l3outs = [
            ACIL3Out.objects.create(
                name=f"ACIViewTestBindingL3Out{i}",
                aci_tenant=cls.aci_tenant,
                aci_vrf=cls.aci_vrf,
                aci_routed_domain=cls.aci_routed_domain,
            )
            for i in range(1, 7)
        ]

        # Common-tenant L3Out - exercises the ImportForm's
        # `is_aci_l3out_in_common` branch which narrows the L3Out queryset
        # to ACI Tenant 'common'. The binding's clean() requires
        # BD.aci_vrf == L3Out.aci_vrf, so the matched BD must reference
        # the common-tenant VRF (the BD model permits a VRF in 'common').
        cls.aci_common_tenant = ACITenant.objects.create(
            name="common",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_common_vrf = ACIVRF.objects.create(
            name="ACIViewTestBindingCommonVRF",
            aci_tenant=cls.aci_common_tenant,
        )
        cls.aci_common_l3out = ACIL3Out.objects.create(
            name="ACIViewTestBindingCommonL3Out",
            aci_tenant=cls.aci_common_tenant,
            aci_vrf=cls.aci_common_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.bd_common_vrf = ACIBridgeDomain.objects.create(
            name="ACIViewTestBindingCommonBD",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_common_vrf,
        )

        # 3 existing binding instances for GET / edit / delete / list / bulk
        ACIBridgeDomainL3OutBinding.objects.create(
            aci_bridge_domain=cls.bds[0], aci_l3out=cls.l3outs[0]
        )
        ACIBridgeDomainL3OutBinding.objects.create(
            aci_bridge_domain=cls.bds[1], aci_l3out=cls.l3outs[1]
        )
        ACIBridgeDomainL3OutBinding.objects.create(
            aci_bridge_domain=cls.bds[2], aci_l3out=cls.l3outs[2]
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # form_data targets BD #4 + L3Out #4 - a pair not used by any
        # existing binding, so create / edit tests can satisfy the unique
        # constraint.
        cls.form_data = {
            "aci_bridge_domain": cls.bds[3].pk,
            "aci_l3out": cls.l3outs[3].pk,
            "comments": "Form-data binding",
            "tags": [t.pk for t in tags],
        }

        # csv_data: 3 new bindings using BD/L3Out pairs 4–6 + one binding
        # whose L3Out lives in 'common'. Import form looks up FKs by name.
        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        cls.csv_data = (
            "aci_fabric,aci_tenant,aci_bridge_domain,aci_l3out,is_aci_l3out_in_common",
            f"{fabric},{tenant},{cls.bds[3].name},{cls.l3outs[3].name},",
            f"{fabric},{tenant},{cls.bds[4].name},{cls.l3outs[4].name},",
            f"{fabric},{tenant},{cls.bds[5].name},{cls.l3outs[5].name},",
            (
                f"{fabric},{tenant},{cls.bd_common_vrf.name},"
                f"{cls.aci_common_l3out.name},true"
            ),
        )

        # csv_update_data: update comments on the 3 existing bindings
        bindings = list(ACIBridgeDomainL3OutBinding.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,comments",
            f"{bindings[0].pk},Updated binding 1",
            f"{bindings[1].pk},Updated binding 2",
            f"{bindings[2].pk},Updated binding 3",
        )

        # bulk_edit_data: only `comments` is bulk-editable per the
        # ACIBridgeDomainL3OutBindingBulkEditForm fieldset
        cls.bulk_edit_data = {"comments": "Bulk-edited comment"}

    def test_acibridgedomain_l3outbindings_tab(self) -> None:
        """L3Out-bindings tab on the BD detail page returns 200."""
        self.add_permissions(
            "netbox_aci_plugin.view_acibridgedomain",
            "netbox_aci_plugin.view_acibridgedomainl3outbinding",
        )
        url = get_action_url(
            self.aci_bd,
            action="l3outbindings",
            kwargs={"pk": self.aci_bd.pk},
        )
        self.assertHttpStatus(self.client.get(url), 200)

    def test_acil3out_bridgedomainbindings_tab(self) -> None:
        """BD-bindings tab on the L3Out detail page returns 200."""
        self.add_permissions(
            "netbox_aci_plugin.view_acil3out",
            "netbox_aci_plugin.view_acibridgedomainl3outbinding",
        )
        url = get_action_url(
            self.l3outs[0],
            action="bridgedomainbindings",
            kwargs={"pk": self.l3outs[0].pk},
        )
        self.assertHttpStatus(self.client.get(url), 200)


class ACIBridgeDomainViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIBridgeDomain."""

    model = ACIBridgeDomain

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomain view tests."""
        super().setUpTestData()

        # 3 ACIBridgeDomain instances under the shared base tenant + VRF
        # (the base class already provides cls.aci_bd as a 4th).
        ACIBridgeDomain.objects.create(
            name="ACIViewTestBridgeDomain1",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        ACIBridgeDomain.objects.create(
            name="ACIViewTestBridgeDomain2",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        ACIBridgeDomain.objects.create(
            name="ACIViewTestBridgeDomain3",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestBridgeDomainX",
            "name_alias": "BridgeDomainXAlias",
            "description": "Form-data Bridge Domain",
            "aci_tenant": cls.aci_tenant.pk,
            "aci_vrf": cls.aci_vrf.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        vrf = cls.aci_vrf.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,aci_vrf,is_aci_vrf_in_common,"
                "multi_destination_flooding,unknown_ipv4_multicast,"
                "unknown_ipv6_multicast,unknown_unicast"
            ),
            (
                f"ACIViewTestBridgeDomain4,{fabric},{tenant},{vrf},,"
                "bd-flood,flood,flood,proxy"
            ),
            (
                f"ACIViewTestBridgeDomain5,{fabric},{tenant},{vrf},,"
                "bd-flood,flood,flood,proxy"
            ),
            (
                f"ACIViewTestBridgeDomain6,{fabric},{tenant},{vrf},,"
                "bd-flood,flood,flood,proxy"
            ),
        )

        bds = list(ACIBridgeDomain.objects.exclude(pk=cls.aci_bd.pk).order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{bds[0].pk},Updated Bridge Domain 1",
            f"{bds[1].pk},Updated Bridge Domain 2",
            f"{bds[2].pk},Updated Bridge Domain 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Bridge Domain"}


class ACIBridgeDomainSubnetViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIBridgeDomainSubnet."""

    model = ACIBridgeDomainSubnet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomainSubnet view tests."""
        super().setUpTestData()

        cls.aci_subnet_bd = ACIBridgeDomain.objects.create(
            name="ACIViewTestSubnetBD",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        # Each subnet needs a distinct gateway IPAddress (CSV import looks
        # the gateway up by its unique address string).
        gateways = [
            IPAddress.objects.create(address=f"10.60.{i}.1/24") for i in range(1, 8)
        ]

        ACIBridgeDomainSubnet.objects.create(
            name="ACIViewTestSubnet1",
            aci_bridge_domain=cls.aci_subnet_bd,
            gateway_ip_address=gateways[0],
        )
        ACIBridgeDomainSubnet.objects.create(
            name="ACIViewTestSubnet2",
            aci_bridge_domain=cls.aci_subnet_bd,
            gateway_ip_address=gateways[1],
        )
        ACIBridgeDomainSubnet.objects.create(
            name="ACIViewTestSubnet3",
            aci_bridge_domain=cls.aci_subnet_bd,
            gateway_ip_address=gateways[2],
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestSubnetX",
            "name_alias": "SubnetXAlias",
            "description": "Form-data Subnet",
            "aci_bridge_domain": cls.aci_subnet_bd.pk,
            "gateway_ip_address": gateways[3].pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        vrf = cls.aci_vrf.name
        bd = cls.aci_subnet_bd.name
        cls.csv_data = (
            ("name,aci_fabric,aci_tenant,aci_vrf,aci_bridge_domain,gateway_ip_address"),
            (f"ACIViewTestSubnet4,{fabric},{tenant},{vrf},{bd},{gateways[4].address}"),
            (f"ACIViewTestSubnet5,{fabric},{tenant},{vrf},{bd},{gateways[5].address}"),
            (f"ACIViewTestSubnet6,{fabric},{tenant},{vrf},{bd},{gateways[6].address}"),
        )

        subnets = list(ACIBridgeDomainSubnet.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{subnets[0].pk},Updated Subnet 1",
            f"{subnets[1].pk},Updated Subnet 2",
            f"{subnets[2].pk},Updated Subnet 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Subnet"}
