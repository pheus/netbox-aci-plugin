# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for tenant Endpoint Group models."""

from django.contrib.contenttypes.models import ContentType

from ipam.models import IPAddress
from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.tenant.contracts import ACIContractRelation
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ..base import ACIModelViewTestCase


class ACIEndpointGroupViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIEndpointGroup."""

    model = ACIEndpointGroup

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointGroup view tests."""
        super().setUpTestData()

        # 3 ACIEndpointGroup instances under the shared base app profile + BD.
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPG1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        ACIEndpointGroup.objects.create(
            name="ACIViewTestEPG2",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        ACIEndpointGroup.objects.create(
            name="ACIViewTestEPG3",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestEPGX",
            "name_alias": "EPGXAlias",
            "description": "Form-data Endpoint Group",
            "aci_app_profile": cls.aci_app_profile.pk,
            "aci_bridge_domain": cls.aci_bd.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        app = cls.aci_app_profile.name
        bd = cls.aci_bd.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,aci_app_profile,"
                "aci_bridge_domain,is_aci_bd_in_common,qos_class"
            ),
            f"ACIViewTestEPG4,{fabric},{tenant},{app},{bd},,unspecified",
            f"ACIViewTestEPG5,{fabric},{tenant},{app},{bd},,unspecified",
            f"ACIViewTestEPG6,{fabric},{tenant},{app},{bd},,unspecified",
        )

        epgs = list(ACIEndpointGroup.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{epgs[0].pk},Updated EPG 1",
            f"{epgs[1].pk},Updated EPG 2",
            f"{epgs[2].pk},Updated EPG 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Endpoint Group"}

    def test_aciendpointgroup_contract_relations_tab(self) -> None:
        """Contract Relations tab renders the registered Assign button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciendpointgroup",
            "netbox_aci_plugin.view_acicontractrelation",
            "netbox_aci_plugin.add_acicontractrelation",
        )
        url = get_action_url(
            self.aci_epg,
            action="contractrelations",
            kwargs={"pk": self.aci_epg.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractRelation, action="add")
        content_type = ContentType.objects.get_for_model(ACIEndpointGroup)
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_epg.aci_tenant.pk}&amp;'
            f"aci_object={self.aci_epg.pk}&amp;"
            f"aci_object_type={content_type.pk}",
        )


class ACIUSegEndpointGroupViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIUSegEndpointGroup."""

    model = ACIUSegEndpointGroup

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegEndpointGroup view tests."""
        super().setUpTestData()

        # 3 uSeg EPG instances under the shared base app profile + BD.
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIViewTestUSegEPG1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        ACIUSegEndpointGroup.objects.create(
            name="ACIViewTestUSegEPG2",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        ACIUSegEndpointGroup.objects.create(
            name="ACIViewTestUSegEPG3",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestUSegEPGX",
            "name_alias": "USegEPGXAlias",
            "description": "Form-data uSeg Endpoint Group",
            "aci_app_profile": cls.aci_app_profile.pk,
            "aci_bridge_domain": cls.aci_bd.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        app = cls.aci_app_profile.name
        bd = cls.aci_bd.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,aci_app_profile,"
                "aci_bridge_domain,is_aci_bd_in_common,qos_class"
            ),
            f"ACIViewTestUSegEPG4,{fabric},{tenant},{app},{bd},,unspecified",
            f"ACIViewTestUSegEPG5,{fabric},{tenant},{app},{bd},,unspecified",
            f"ACIViewTestUSegEPG6,{fabric},{tenant},{app},{bd},,unspecified",
        )

        epgs = list(ACIUSegEndpointGroup.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{epgs[0].pk},Updated uSeg EPG 1",
            f"{epgs[1].pk},Updated uSeg EPG 2",
            f"{epgs[2].pk},Updated uSeg EPG 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited uSeg Endpoint Group"}

    def test_aciusegendpointgroup_contract_relations_tab(self) -> None:
        """uSeg Contract Relations tab renders the registered Assign button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciusegendpointgroup",
            "netbox_aci_plugin.view_acicontractrelation",
            "netbox_aci_plugin.add_acicontractrelation",
        )
        url = get_action_url(
            self.aci_useg_epg,
            action="contractrelations",
            kwargs={"pk": self.aci_useg_epg.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractRelation, action="add")
        content_type = ContentType.objects.get_for_model(ACIUSegEndpointGroup)
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_useg_epg.aci_tenant.pk}&amp;'
            f"aci_object={self.aci_useg_epg.pk}&amp;"
            f"aci_object_type={content_type.pk}",
        )

    def test_aciusegendpointgroup_network_attributes_tab(self) -> None:
        """Network Attributes tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciusegendpointgroup",
            "netbox_aci_plugin.view_aciusegnetworkattribute",
            "netbox_aci_plugin.add_aciusegnetworkattribute",
        )
        url = get_action_url(
            self.aci_useg_epg,
            action="usegnetworkattributes",
            kwargs={"pk": self.aci_useg_epg.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIUSegNetworkAttribute, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_useg_epg.aci_tenant.pk}&amp;'
            f"aci_app_profile={self.aci_useg_epg.aci_app_profile_id}&amp;"
            f"aci_useg_endpoint_group={self.aci_useg_epg.pk}",
        )


class ACIUSegNetworkAttributeViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIUSegNetworkAttribute.

    The generic-FK attribute target is a NetBox IP address.
    """

    model = ACIUSegNetworkAttribute

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegNetworkAttribute view tests."""
        super().setUpTestData()

        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIViewTestNetAttrUSegEPG",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        # Each attribute targets a distinct IP address (CSV import looks the
        # target up by primary key).
        ips = [IPAddress.objects.create(address=f"10.70.{i}.1/24") for i in range(1, 8)]
        cls.ip_ct = ContentType.objects.get_for_model(IPAddress)

        ACIUSegNetworkAttribute.objects.create(
            name="ACIViewTestNetAttr1",
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=ips[0],
            use_epg_subnet=False,
        )
        ACIUSegNetworkAttribute.objects.create(
            name="ACIViewTestNetAttr2",
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=ips[1],
            use_epg_subnet=False,
        )
        ACIUSegNetworkAttribute.objects.create(
            name="ACIViewTestNetAttr3",
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=ips[2],
            use_epg_subnet=False,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestNetAttrX",
            "name_alias": "NetAttrXAlias",
            "description": "Form-data Network Attribute",
            "aci_useg_endpoint_group": cls.aci_useg_epg.pk,
            "attr_object_type": cls.ip_ct.pk,
            "attr_object": ips[3].pk,
            "use_epg_subnet": False,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        app = cls.aci_app_profile.name
        useg = cls.aci_useg_epg.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,aci_app_profile,"
                "aci_useg_endpoint_group,attr_object_id,attr_object_type,"
                "use_epg_subnet"
            ),
            (
                f"ACIViewTestNetAttr4,{fabric},{tenant},{app},{useg},"
                f"{ips[4].pk},ipam.ipaddress,false"
            ),
            (
                f"ACIViewTestNetAttr5,{fabric},{tenant},{app},{useg},"
                f"{ips[5].pk},ipam.ipaddress,false"
            ),
            (
                f"ACIViewTestNetAttr6,{fabric},{tenant},{app},{useg},"
                f"{ips[6].pk},ipam.ipaddress,false"
            ),
        )

        attrs = list(ACIUSegNetworkAttribute.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{attrs[0].pk},Updated Network Attribute 1",
            f"{attrs[1].pk},Updated Network Attribute 2",
            f"{attrs[2].pk},Updated Network Attribute 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Network Attribute"}
