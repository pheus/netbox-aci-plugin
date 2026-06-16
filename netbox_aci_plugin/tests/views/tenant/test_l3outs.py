# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for tenant L3Out models."""

from django.contrib.contenttypes.models import ContentType

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.contracts import ACIContractRelation
from ....models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIModelViewTestCase


class ACIL3OutViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIL3Out."""

    model = ACIL3Out

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIViewTestL3OutRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )

        # Common-tenant VRF - exercises the ImportForm's
        # `is_aci_vrf_in_common` branch which narrows the VRF queryset
        # to ACI Tenant 'common'.
        cls.aci_common_tenant = ACITenant.objects.create(
            name="common",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_common_vrf = ACIVRF.objects.create(
            name="ACIViewTestL3OutCommonVRF",
            aci_tenant=cls.aci_common_tenant,
        )

        # 3 ACIL3Out instances for list / bulk / get / edit / delete
        ACIL3Out.objects.create(
            name="ACIViewTestL3Out1",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        ACIL3Out.objects.create(
            name="ACIViewTestL3Out2",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        ACIL3Out.objects.create(
            name="ACIViewTestL3Out3",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestL3OutX",
            "name_alias": "L3OutXAlias",
            "description": "Form-data L3Out",
            "aci_tenant": cls.aci_tenant.pk,
            "aci_vrf": cls.aci_vrf.pk,
            "aci_routed_domain": cls.aci_routed_domain.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        vrf = cls.aci_vrf.name
        rd = cls.aci_routed_domain.name
        common_vrf = cls.aci_common_vrf.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,aci_vrf,"
                "is_aci_vrf_in_common,aci_routed_domain"
            ),
            f"ACIViewTestL3Out4,{fabric},{tenant},{vrf},,{rd}",
            f"ACIViewTestL3Out5,{fabric},{tenant},{vrf},,{rd}",
            f"ACIViewTestL3Out6,{fabric},{tenant},{vrf},,{rd}",
            # Imports an L3Out in the regular tenant that references a VRF
            # which lives in ACI Tenant 'common'.
            f"ACIViewTestL3OutCommon,{fabric},{tenant},{common_vrf},true,{rd}",
        )

        l3outs = list(ACIL3Out.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{l3outs[0].pk},Updated L3Out 1",
            f"{l3outs[1].pk},Updated L3Out 2",
            f"{l3outs[2].pk},Updated L3Out 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited L3Out"}

    def test_acil3out_external_endpoint_groups_tab(self) -> None:
        """External EPGs tab renders the registered Add button."""
        instance = ACIL3Out.objects.first()
        self.add_permissions(
            "netbox_aci_plugin.view_acil3out",
            "netbox_aci_plugin.view_aciexternalendpointgroup",
            "netbox_aci_plugin.add_aciexternalendpointgroup",
        )
        url = get_action_url(
            instance,
            action="externalendpointgroups",
            kwargs={"pk": instance.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIExternalEndpointGroup, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={instance.aci_tenant_id}&amp;'
            f"aci_l3out={instance.pk}",
        )

    def test_acirouteddomain_l3outs_tab(self) -> None:
        """Routed Domain L3Outs tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acirouteddomain",
            "netbox_aci_plugin.view_acil3out",
            "netbox_aci_plugin.add_acil3out",
        )
        url = get_action_url(
            self.aci_routed_domain,
            action="l3outs",
            kwargs={"pk": self.aci_routed_domain.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIL3Out, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_routed_domain.aci_fabric_id}&amp;'
            f"aci_routed_domain={self.aci_routed_domain.pk}",
        )


class ACIExternalEndpointGroupViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIExternalEndpointGroup."""

    model = ACIExternalEndpointGroup

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIViewTestExtEPGRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIViewTestExtEPGL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )

        # Common-tenant L3Out - exercises the ImportForm's
        # `is_aci_l3out_in_common` branch which narrows the L3Out queryset
        # to ACI Tenant 'common'.
        cls.aci_common_tenant = ACITenant.objects.create(
            name="common",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_common_vrf = ACIVRF.objects.create(
            name="ACIViewTestExtEPGCommonVRF",
            aci_tenant=cls.aci_common_tenant,
        )
        cls.aci_common_l3out = ACIL3Out.objects.create(
            name="ACIViewTestExtEPGCommonL3Out",
            aci_tenant=cls.aci_common_tenant,
            aci_vrf=cls.aci_common_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )

        ACIExternalEndpointGroup.objects.create(
            name="ACIViewTestExtEPG1", aci_l3out=cls.aci_l3out
        )
        ACIExternalEndpointGroup.objects.create(
            name="ACIViewTestExtEPG2", aci_l3out=cls.aci_l3out
        )
        ACIExternalEndpointGroup.objects.create(
            name="ACIViewTestExtEPG3", aci_l3out=cls.aci_l3out
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestExtEPGX",
            "name_alias": "ExtEPGXAlias",
            "description": "Form-data External EPG",
            "aci_l3out": cls.aci_l3out.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        l3out = cls.aci_l3out.name
        common_tenant = cls.aci_common_tenant.name
        common_l3out = cls.aci_common_l3out.name
        cls.csv_data = (
            "name,aci_fabric,aci_tenant,aci_l3out,is_aci_l3out_in_common",
            f"ACIViewTestExtEPG4,{fabric},{tenant},{l3out},",
            f"ACIViewTestExtEPG5,{fabric},{tenant},{l3out},",
            f"ACIViewTestExtEPG6,{fabric},{tenant},{l3out},",
            # Imports an External EPG whose parent L3Out lives in
            # ACI Tenant 'common'.
            f"ACIViewTestExtEPGCommon,{fabric},{common_tenant},{common_l3out},true",
        )

        epgs = list(ACIExternalEndpointGroup.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{epgs[0].pk},Updated External EPG 1",
            f"{epgs[1].pk},Updated External EPG 2",
            f"{epgs[2].pk},Updated External EPG 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited External EPG"}

    def test_aciexternalendpointgroup_subnets_tab(self) -> None:
        """External Subnets tab renders the registered Add button."""
        instance = ACIExternalEndpointGroup.objects.first()
        self.add_permissions(
            "netbox_aci_plugin.view_aciexternalendpointgroup",
            "netbox_aci_plugin.view_aciexternalsubnet",
            "netbox_aci_plugin.add_aciexternalsubnet",
        )
        url = get_action_url(instance, action="subnets", kwargs={"pk": instance.pk})
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIExternalSubnet, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={instance.aci_tenant.pk}&amp;'
            f"aci_l3out={instance.aci_l3out_id}&amp;"
            f"aci_external_endpoint_group={instance.pk}",
        )

    def test_aciexternalendpointgroup_contract_relations_tab(self) -> None:
        """Contract Relations Add button uses aci_object (not _id) + tenant."""
        instance = ACIExternalEndpointGroup.objects.first()
        self.add_permissions(
            "netbox_aci_plugin.view_aciexternalendpointgroup",
            "netbox_aci_plugin.view_acicontractrelation",
            "netbox_aci_plugin.add_acicontractrelation",
        )
        url = get_action_url(
            instance,
            action="contractrelations",
            kwargs={"pk": instance.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractRelation, action="add")
        content_type = ContentType.objects.get_for_model(ACIExternalEndpointGroup)
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={instance.aci_tenant.pk}&amp;'
            f"aci_object={instance.pk}&amp;"
            f"aci_object_type={content_type.pk}",
        )
        # The old partial used the wrong field name aci_object_id.
        self.assertNotContains(response, "aci_object_id=")


class ACIExternalSubnetViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIExternalSubnet."""

    model = ACIExternalSubnet
    # matched_prefix is stored as netaddr.IPNetwork but form_data carries
    # a string; assertInstanceEqual would fail the type-strict compare.
    validation_excluded_fields = ["matched_prefix"]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIViewTestExtSubnetRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIViewTestExtSubnetL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_epg = ACIExternalEndpointGroup.objects.create(
            name="ACIViewTestExtSubnetEPG", aci_l3out=cls.aci_l3out
        )

        # Common-tenant L3Out + ExtEPG - exercises the ImportForm's
        # `is_aci_l3out_in_common` branch which narrows the L3Out queryset
        # to ACI Tenant 'common'.
        cls.aci_common_tenant = ACITenant.objects.create(
            name="common",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_common_vrf = ACIVRF.objects.create(
            name="ACIViewTestExtSubnetCommonVRF",
            aci_tenant=cls.aci_common_tenant,
        )
        cls.aci_common_l3out = ACIL3Out.objects.create(
            name="ACIViewTestExtSubnetCommonL3Out",
            aci_tenant=cls.aci_common_tenant,
            aci_vrf=cls.aci_common_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_common_epg = ACIExternalEndpointGroup.objects.create(
            name="ACIViewTestExtSubnetCommonEPG",
            aci_l3out=cls.aci_common_l3out,
        )

        # Each ExternalSubnet must have a unique (aci_external_endpoint_group,
        # matched_prefix) pair per the model's UniqueConstraint
        ACIExternalSubnet.objects.create(
            name="ACIViewTestExtSubnet1",
            aci_external_endpoint_group=cls.aci_epg,
            matched_prefix="10.110.0.0/24",
        )
        ACIExternalSubnet.objects.create(
            name="ACIViewTestExtSubnet2",
            aci_external_endpoint_group=cls.aci_epg,
            matched_prefix="10.120.0.0/24",
        )
        ACIExternalSubnet.objects.create(
            name="ACIViewTestExtSubnet3",
            aci_external_endpoint_group=cls.aci_epg,
            matched_prefix="10.130.0.0/24",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestExtSubnetX",
            "name_alias": "ExtSubnetXAlias",
            "description": "Form-data External Subnet",
            "aci_external_endpoint_group": cls.aci_epg.pk,
            "matched_prefix": "10.200.0.0/24",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        l3out = cls.aci_l3out.name
        epg = cls.aci_epg.name
        common_tenant = cls.aci_common_tenant.name
        common_l3out = cls.aci_common_l3out.name
        common_epg = cls.aci_common_epg.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,aci_l3out,is_aci_l3out_in_common,"
                "aci_external_endpoint_group,matched_prefix"
            ),
            f"ACIViewTestExtSubnet4,{fabric},{tenant},{l3out},,{epg},10.140.0.0/24",
            f"ACIViewTestExtSubnet5,{fabric},{tenant},{l3out},,{epg},10.150.0.0/24",
            f"ACIViewTestExtSubnet6,{fabric},{tenant},{l3out},,{epg},10.160.0.0/24",
            # Imports an External Subnet whose parent L3Out lives in
            # ACI Tenant 'common'.
            (
                f"ACIViewTestExtSubnetCommon,{fabric},{common_tenant},"
                f"{common_l3out},true,{common_epg},10.170.0.0/24"
            ),
        )

        subnets = list(ACIExternalSubnet.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{subnets[0].pk},Updated External Subnet 1",
            f"{subnets[1].pk},Updated External Subnet 2",
            f"{subnets[2].pk},Updated External Subnet 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited External Subnet"}
