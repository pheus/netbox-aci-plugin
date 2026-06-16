# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for tenant Endpoint Security Group models."""

from django.contrib.contenttypes.models import ContentType

from ipam.models import IPAddress
from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.tenant.contracts import ACIContractRelation
from ....models.tenant.endpoint_groups import ACIEndpointGroup
from ....models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ..base import ACIModelViewTestCase


class ACIEndpointSecurityGroupViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIEndpointSecurityGroup."""

    model = ACIEndpointSecurityGroup

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointSecurityGroup view tests."""
        super().setUpTestData()

        # 3 ESG instances under the shared base app profile + VRF.
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIViewTestESG1",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        ACIEndpointSecurityGroup.objects.create(
            name="ACIViewTestESG2",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        ACIEndpointSecurityGroup.objects.create(
            name="ACIViewTestESG3",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestESGX",
            "name_alias": "ESGXAlias",
            "description": "Form-data Endpoint Security Group",
            "aci_app_profile": cls.aci_app_profile.pk,
            "aci_vrf": cls.aci_vrf.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        app = cls.aci_app_profile.name
        vrf = cls.aci_vrf.name
        cls.csv_data = (
            ("name,aci_fabric,aci_tenant,aci_app_profile,aci_vrf,is_aci_vrf_in_common"),
            f"ACIViewTestESG4,{fabric},{tenant},{app},{vrf},",
            f"ACIViewTestESG5,{fabric},{tenant},{app},{vrf},",
            f"ACIViewTestESG6,{fabric},{tenant},{app},{vrf},",
        )

        esgs = list(ACIEndpointSecurityGroup.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{esgs[0].pk},Updated ESG 1",
            f"{esgs[1].pk},Updated ESG 2",
            f"{esgs[2].pk},Updated ESG 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Endpoint Security Group"}

    def test_aciendpointsecuritygroup_contract_relations_tab(self) -> None:
        """Contract Relations tab renders the registered Assign button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciendpointsecuritygroup",
            "netbox_aci_plugin.view_acicontractrelation",
            "netbox_aci_plugin.add_acicontractrelation",
        )
        url = get_action_url(
            self.aci_esg,
            action="contractrelations",
            kwargs={"pk": self.aci_esg.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractRelation, action="add")
        content_type = ContentType.objects.get_for_model(ACIEndpointSecurityGroup)
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_esg.aci_tenant.pk}&amp;'
            f"aci_object={self.aci_esg.pk}&amp;"
            f"aci_object_type={content_type.pk}",
        )

    def test_aciendpointsecuritygroup_epg_selectors_tab(self) -> None:
        """EPG Selectors tab renders the registered Assign button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciendpointsecuritygroup",
            "netbox_aci_plugin.view_aciesgendpointgroupselector",
            "netbox_aci_plugin.add_aciesgendpointgroupselector",
        )
        url = get_action_url(
            self.aci_esg,
            action="epgselectors",
            kwargs={"pk": self.aci_esg.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEsgEndpointGroupSelector, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_esg.aci_tenant.pk}&amp;'
            f"aci_app_profile={self.aci_esg.aci_app_profile_id}&amp;"
            f"aci_endpoint_security_group={self.aci_esg.pk}",
        )

    def test_aciendpointsecuritygroup_ep_selectors_tab(self) -> None:
        """Endpoint Selectors tab renders the registered Assign button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciendpointsecuritygroup",
            "netbox_aci_plugin.view_aciesgendpointselector",
            "netbox_aci_plugin.add_aciesgendpointselector",
        )
        url = get_action_url(
            self.aci_esg,
            action="epselectors",
            kwargs={"pk": self.aci_esg.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEsgEndpointSelector, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_esg.aci_tenant.pk}&amp;'
            f"aci_app_profile={self.aci_esg.aci_app_profile_id}&amp;"
            f"aci_endpoint_security_group={self.aci_esg.pk}",
        )


class ACIEsgEndpointGroupSelectorViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIEsgEndpointGroupSelector.

    The generic-FK target is an ACI Endpoint Group.
    """

    model = ACIEsgEndpointGroupSelector

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEsgEndpointGroupSelector view tests."""
        super().setUpTestData()

        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIViewTestEpgSelESG",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        # Each selector targets a distinct ACI Endpoint Group.
        epgs = [
            ACIEndpointGroup.objects.create(
                name=f"ACIViewTestEpgSelEPG{i}",
                aci_app_profile=cls.aci_app_profile,
                aci_bridge_domain=cls.aci_bd,
            )
            for i in range(1, 8)
        ]
        cls.epg_ct = ContentType.objects.get_for_model(ACIEndpointGroup)

        ACIEsgEndpointGroupSelector.objects.create(
            name="ACIViewTestEpgSel1",
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=epgs[0],
        )
        ACIEsgEndpointGroupSelector.objects.create(
            name="ACIViewTestEpgSel2",
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=epgs[1],
        )
        ACIEsgEndpointGroupSelector.objects.create(
            name="ACIViewTestEpgSel3",
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=epgs[2],
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestEpgSelX",
            "name_alias": "EpgSelXAlias",
            "description": "Form-data EPG Selector",
            "aci_endpoint_security_group": cls.aci_esg.pk,
            "aci_epg_object_type": cls.epg_ct.pk,
            "aci_epg_object": epgs[3].pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        app = cls.aci_app_profile.name
        esg = cls.aci_esg.name
        ct = "netbox_aci_plugin.aciendpointgroup"
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,aci_app_profile,"
                "aci_endpoint_security_group,aci_epg_object_id,"
                "aci_epg_object_type"
            ),
            (f"ACIViewTestEpgSel4,{fabric},{tenant},{app},{esg},{epgs[4].pk},{ct}"),
            (f"ACIViewTestEpgSel5,{fabric},{tenant},{app},{esg},{epgs[5].pk},{ct}"),
            (f"ACIViewTestEpgSel6,{fabric},{tenant},{app},{esg},{epgs[6].pk},{ct}"),
        )

        selectors = list(ACIEsgEndpointGroupSelector.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{selectors[0].pk},Updated EPG Selector 1",
            f"{selectors[1].pk},Updated EPG Selector 2",
            f"{selectors[2].pk},Updated EPG Selector 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited EPG Selector"}


class ACIEsgEndpointSelectorViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIEsgEndpointSelector.

    The generic-FK target is a NetBox IP address.
    """

    model = ACIEsgEndpointSelector

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEsgEndpointSelector view tests."""
        super().setUpTestData()

        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIViewTestEpSelESG",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        # Each selector targets a distinct IP address.
        ips = [IPAddress.objects.create(address=f"10.80.{i}.1/24") for i in range(1, 8)]
        cls.ip_ct = ContentType.objects.get_for_model(IPAddress)

        ACIEsgEndpointSelector.objects.create(
            name="ACIViewTestEpSel1",
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=ips[0],
        )
        ACIEsgEndpointSelector.objects.create(
            name="ACIViewTestEpSel2",
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=ips[1],
        )
        ACIEsgEndpointSelector.objects.create(
            name="ACIViewTestEpSel3",
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=ips[2],
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestEpSelX",
            "name_alias": "EpSelXAlias",
            "description": "Form-data Endpoint Selector",
            "aci_endpoint_security_group": cls.aci_esg.pk,
            "ep_object_type": cls.ip_ct.pk,
            "ep_object": ips[3].pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        app = cls.aci_app_profile.name
        esg = cls.aci_esg.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,aci_app_profile,"
                "aci_endpoint_security_group,ep_object_id,ep_object_type"
            ),
            (
                f"ACIViewTestEpSel4,{fabric},{tenant},{app},{esg},"
                f"{ips[4].pk},ipam.ipaddress"
            ),
            (
                f"ACIViewTestEpSel5,{fabric},{tenant},{app},{esg},"
                f"{ips[5].pk},ipam.ipaddress"
            ),
            (
                f"ACIViewTestEpSel6,{fabric},{tenant},{app},{esg},"
                f"{ips[6].pk},ipam.ipaddress"
            ),
        )

        selectors = list(ACIEsgEndpointSelector.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{selectors[0].pk},Updated Endpoint Selector 1",
            f"{selectors[1].pk},Updated Endpoint Selector 2",
            f"{selectors[2].pk},Updated Endpoint Selector 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Endpoint Selector"}
