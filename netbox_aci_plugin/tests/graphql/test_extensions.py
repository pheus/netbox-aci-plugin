# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from netbox.graphql.schema import schema
from tenancy.models import Tenant

from ...models.fabric.node_interfaces import ACINodeInterface
from .base import ACIBaseGraphQLTestCase


class ACIGraphQLExtensionTestCase(ACIBaseGraphQLTestCase):
    """Test the ACI additions spliced into NetBox's own GraphQL types."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up the NetBox objects the ACI extensions hang from."""
        super().setUpTestData()

        cls.nb_tenant = Tenant.objects.create(
            name="ACIGraphQLTestNBTenant", slug="acigraphqltestnbtenant"
        )
        cls.aci_tenant1.nb_tenant = cls.nb_tenant
        cls.aci_tenant1.save()

        site = Site.objects.create(name="ACIGraphQLTestSite", slug="acigraphqltestsite")
        manufacturer = Manufacturer.objects.create(
            name="ACIGraphQLTestManufacturer", slug="acigraphqltestmanufacturer"
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="ACIGraphQLTestModel", slug="acitestmodel"
        )
        role = DeviceRole.objects.create(
            name="ACIGraphQLTestRole", slug="acigraphqltestrole"
        )
        cls.device = Device.objects.create(
            name="ACIGraphQLTestDevice",
            site=site,
            device_type=device_type,
            role=role,
        )
        cls.nb_interface = Interface.objects.create(
            device=cls.device, name="Ethernet1/1", type="1000base-t"
        )
        cls.nb_interface_unused = Interface.objects.create(
            device=cls.device, name="Ethernet1/2", type="1000base-t"
        )

        # The Node's assigned device must match the interface's device.
        cls.aci_node1.node_object = cls.device
        cls.aci_node1.save()
        cls.aci_node_interface1.nb_interface = cls.nb_interface
        cls.aci_node_interface1.save()

    def test_schema_exposes_the_extension_fields(self) -> None:
        """The core types carry the ACI fields the plugin contributes."""
        self.assertIsNotNone(
            schema.get_field_for_type("aci_node_interface", "InterfaceType")
        )
        self.assertIsNotNone(schema.get_field_for_type("aci_tenants", "TenantType"))

    def test_interface_resolves_its_aci_node_interface(self) -> None:
        """An interface backing an ACI Node Interface returns it."""
        self.add_permissions(
            "dcim.view_interface", "netbox_aci_plugin.view_acinodeinterface"
        )

        result = self.query(
            "query { interface(id: "
            f'"{self.nb_interface.pk}"'
            ") { id aci_node_interface { id } } }"
        )

        self.assertNotIn("errors", result, result)
        self.assertEqual(
            result["data"]["interface"]["aci_node_interface"]["id"],
            str(self.aci_node_interface1.pk),
        )

    def test_interface_without_an_aci_node_interface_resolves_null(self) -> None:
        """An unused interface returns null rather than raising."""
        self.add_permissions(
            "dcim.view_interface", "netbox_aci_plugin.view_acinodeinterface"
        )

        result = self.query(
            "query { interface(id: "
            f'"{self.nb_interface_unused.pk}"'
            ") { id aci_node_interface { id } } }"
        )

        self.assertNotIn("errors", result, result)
        self.assertIsNone(result["data"]["interface"]["aci_node_interface"])

    def test_aci_node_interface_hidden_without_permission(self) -> None:
        """The field returns null when the user may not view ACI objects."""
        self.add_permissions("dcim.view_interface")

        result = self.query(
            "query { interface(id: "
            f'"{self.nb_interface.pk}"'
            ") { id aci_node_interface { id } } }"
        )

        self.assertNotIn("errors", result, result)
        self.assertIsNone(result["data"]["interface"]["aci_node_interface"])

    def test_tenant_resolves_its_aci_tenants(self) -> None:
        """A NetBox tenant lists the ACI Tenants assigned to it."""
        self.add_permissions("tenancy.view_tenant", "netbox_aci_plugin.view_acitenant")

        result = self.query(
            "query { tenant(id: "
            f'"{self.nb_tenant.pk}"'
            ") { id aci_tenants { id } } }"
        )

        self.assertNotIn("errors", result, result)
        returned = {row["id"] for row in result["data"]["tenant"]["aci_tenants"]}
        self.assertEqual(returned, {str(self.aci_tenant1.pk)})

    def test_tenant_without_aci_tenants_resolves_empty(self) -> None:
        """A tenant with no ACI Tenants returns an empty list."""
        self.add_permissions("tenancy.view_tenant", "netbox_aci_plugin.view_acitenant")
        other = Tenant.objects.create(
            name="ACIGraphQLTestNBTenant2", slug="acigraphqltestnbtenant2"
        )

        result = self.query(
            f'query {{ tenant(id: "{other.pk}") {{ id aci_tenants {{ id }} }} }}'
        )

        self.assertNotIn("errors", result, result)
        self.assertEqual(result["data"]["tenant"]["aci_tenants"], [])

    def test_aci_tenants_hidden_without_permission(self) -> None:
        """The list is empty when the user may not view ACI Tenants."""
        self.add_permissions("tenancy.view_tenant")

        result = self.query(
            "query { tenant(id: "
            f'"{self.nb_tenant.pk}"'
            ") { id aci_tenants { id } } }"
        )

        self.assertNotIn("errors", result, result)
        self.assertEqual(result["data"]["tenant"]["aci_tenants"], [])

    def test_extension_relations_are_not_n_plus_one(self) -> None:
        """Listing interfaces prefetches the ACI side in one extra query."""
        self.add_permissions(
            "dcim.view_interface", "netbox_aci_plugin.view_acinodeinterface"
        )
        for index in range(3, 6):
            interface = Interface.objects.create(
                device=self.device, name=f"Ethernet1/{index}", type="1000base-t"
            )
            ACINodeInterface.objects.create(
                aci_node=self.aci_node1,
                module=1,
                port=index,
                nb_interface=interface,
            )

        with self.assertNumQueries(9):
            result = self.query(
                "query { interface_list { id aci_node_interface { id } } }"
            )

        self.assertNotIn("errors", result, result)
