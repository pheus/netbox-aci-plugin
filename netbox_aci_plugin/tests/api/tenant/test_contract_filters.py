# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ....models.tenant.tenants import ACITenant


class ACIContractFilterAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract Filter."""

    model = ACIContractFilter
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acitenant",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Filter for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")

        aci_contract_filters = (
            ACIContractFilter(
                name="ACIContractFilterTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant1,
            ),
            ACIContractFilter(
                name="ACIContractFilterTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
            ),
            ACIContractFilter(
                name="ACIContractFilterTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant2,
            ),
        )
        ACIContractFilter.objects.bulk_create(aci_contract_filters)

        cls.create_data: list[dict] = [
            {
                "name": "ACIContractFilterTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "nb_tenant": nb_tenant1.id,
            },
            {
                "name": "ACIContractFilterTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "nb_tenant": nb_tenant2.id,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIContractFilterEntryAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract Filter."""

    model = ACIContractFilterEntry
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_contract_filter",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_acicontractfilter",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Filter for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_contract_filter1 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
        )
        aci_contract_filter2 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
        )

        aci_contract_filter_entries = (
            ACIContractFilterEntry(
                name="ACIContractFilterEntryTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_contract_filter=aci_contract_filter1,
                ether_type="ip",
                arp_opc="unspecified",
                ip_protocol="tcp",
                match_dscp="unspecified",
                match_only_fragments_enabled=True,
                icmp_v4_type="unspecified",
                icmp_v6_type="unspecified",
                source_from_port="1024",
                source_to_port="65535",
                destination_from_port="http",
                destination_to_port="https",
                stateful_enabled=True,
                tcp_rules=["rst", "fin"],
            ),
            ACIContractFilterEntry(
                name="ACIContractFilterEntryTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_contract_filter=aci_contract_filter2,
            ),
            ACIContractFilterEntry(
                name="ACIContractFilterEntryTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_contract_filter=aci_contract_filter1,
                ether_type="arp",
                arp_opc="reply",
                ip_protocol="unspecified",
                match_dscp="unspecified",
                match_only_fragments_enabled=False,
                icmp_v4_type="unspecified",
                icmp_v6_type="unspecified",
                source_from_port="unspecified",
                source_to_port="unspecified",
                destination_from_port="unspecified",
                destination_to_port="unspecified",
                stateful_enabled=False,
                tcp_rules=["unspecified"],
            ),
        )
        ACIContractFilterEntry.objects.bulk_create(aci_contract_filter_entries)

        cls.create_data: list[dict] = [
            {
                "name": "ACIContractFilterEntryTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_contract_filter": aci_contract_filter2.id,
                "ether_type": "ip",
                "arp_opc": "unspecified",
                "ip_protocol": "tcp",
                "match_dscp": "unspecified",
                "match_only_fragments_enabled": True,
                "icmp_v4_type": "unspecified",
                "icmp_v6_type": "unspecified",
                "source_from_port": "1024",
                "source_to_port": "65535",
                "destination_from_port": "http",
                "destination_to_port": "https",
                "stateful_enabled": True,
                "tcp_rules": ["rst", "fin"],
            },
            {
                "name": "ACIContractFilterEntryTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_contract_filter": aci_contract_filter1.id,
                "ether_type": "ip",
                "arp_opc": "unspecified",
                "ip_protocol": "5",
                "match_dscp": "unspecified",
                "match_only_fragments_enabled": False,
                "icmp_v4_type": "unspecified",
                "icmp_v6_type": "unspecified",
                "source_from_port": "unspecified",
                "source_to_port": "unspecified",
                "destination_from_port": "unspecified",
                "destination_to_port": "unspecified",
                "stateful_enabled": False,
                "tcp_rules": ["unspecified"],
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
