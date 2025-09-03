# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.contract_filters import ACIContractFilter
from ....models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
)
from ....models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIContractAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract."""

    model = ACIContract
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "scope",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acitenant",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")

        aci_contracts = (
            ACIContract(
                name="ACIContractTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant1,
                qos_class="unspecified",
                scope="global",
                target_dscp="unspecified",
            ),
            ACIContract(
                name="ACIContractTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
                qos_class="level3",
                scope="tenant",
                target_dscp="EF",
            ),
            ACIContract(
                name="ACIContractTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant2,
                qos_class="level6",
                scope="context",
                target_dscp="CS3",
            ),
        )
        ACIContract.objects.bulk_create(aci_contracts)

        cls.create_data: list[dict] = [
            {
                "name": "ACIContractTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "nb_tenant": nb_tenant1.id,
                "qos_class": "level1",
                "scope": "global",
                "target_dscp": "unspecified",
            },
            {
                "name": "ACIContractTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "nb_tenant": nb_tenant2.id,
                "qos_class": "level2",
                "scope": "context",
                "target_dscp": "VA",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIContractRelationAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract Relation."""

    model = ACIContractRelation
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_contract",
        "aci_object",
        "aci_object_id",
        "aci_object_type",
        "display",
        "id",
        "role",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acicontract",
        "netbox_aci_plugin.view_aciendpointgroup",
        "netbox_aci_plugin.view_aciusegendpointgroup",
        "netbox_aci_plugin.view_acivrf",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Relation for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_app_profile1 = ACIAppProfile.objects.create(
            name="ACITestAppProfileAPI1",
            aci_tenant=aci_tenant1,
        )
        aci_app_profile2 = ACIAppProfile.objects.create(
            name="ACITestAppProfileAPI2",
            aci_tenant=aci_tenant2,
        )
        aci_vrf1 = ACIVRF.objects.create(
            name="ACI-VRF-API-1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
        )
        aci_vrf2 = ACIVRF.objects.create(
            name="ACI-VRF-API-2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
        )
        aci_bd1 = ACIBridgeDomain.objects.create(
            name="ACI-BD-API-1",
            aci_tenant=aci_tenant1,
            aci_vrf=aci_vrf1,
            nb_tenant=nb_tenant1,
        )
        aci_bd2 = ACIBridgeDomain.objects.create(
            name="ACI-BD-API-2",
            aci_tenant=aci_tenant2,
            aci_vrf=aci_vrf2,
            nb_tenant=nb_tenant2,
        )
        aci_epg1 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupTestAPI1",
            aci_app_profile=aci_app_profile1,
            aci_bridge_domain=aci_bd1,
            nb_tenant=nb_tenant1,
        )
        aci_epg2 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupTestAPI2",
            aci_app_profile=aci_app_profile1,
            aci_bridge_domain=aci_bd1,
            nb_tenant=nb_tenant2,
        )
        aci_epg3 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupTestAPI3",
            aci_app_profile=aci_app_profile2,
            aci_bridge_domain=aci_bd2,
            nb_tenant=nb_tenant1,
        )
        aci_epg4 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupTestAPI4",
            aci_app_profile=aci_app_profile2,
            aci_bridge_domain=aci_bd2,
            nb_tenant=nb_tenant2,
        )
        aci_useg_epg1 = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI1",
            aci_app_profile=aci_app_profile1,
            aci_bridge_domain=aci_bd1,
            nb_tenant=nb_tenant1,
        )
        aci_useg_epg2 = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI2",
            aci_app_profile=aci_app_profile1,
            aci_bridge_domain=aci_bd1,
            nb_tenant=nb_tenant2,
        )
        aci_useg_epg3 = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI3",
            aci_app_profile=aci_app_profile2,
            aci_bridge_domain=aci_bd2,
            nb_tenant=nb_tenant1,
        )
        aci_useg_epg4 = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI4",
            aci_app_profile=aci_app_profile2,
            aci_bridge_domain=aci_bd2,
            nb_tenant=nb_tenant2,
        )
        aci_esg1 = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroupTestAPI1",
            aci_app_profile=aci_app_profile1,
            aci_vrf=aci_vrf1,
            nb_tenant=nb_tenant1,
        )
        aci_esg2 = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroupTestAPI2",
            aci_app_profile=aci_app_profile1,
            aci_vrf=aci_vrf1,
            nb_tenant=nb_tenant2,
        )
        aci_esg3 = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroupTestAPI3",
            aci_app_profile=aci_app_profile2,
            aci_vrf=aci_vrf2,
            nb_tenant=nb_tenant1,
        )
        aci_esg4 = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroupTestAPI4",
            aci_app_profile=aci_app_profile2,
            aci_vrf=aci_vrf2,
            nb_tenant=nb_tenant2,
        )
        aci_contract_epg1 = ACIContract.objects.create(
            name="ACIContractTestAPI1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
            qos_class="unspecified",
            scope="context",
            target_dscp="unspecified",
        )
        aci_contract_epg2 = ACIContract.objects.create(
            name="ACIContractTestAPI2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
            qos_class="level1",
            scope="tenant",
            target_dscp="unspecified",
        )
        aci_contract_esg1 = ACIContract.objects.create(
            name="ACIContractTestAPI3",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
            qos_class="unspecified",
            scope="context",
            target_dscp="unspecified",
        )
        aci_contract_esg2 = ACIContract.objects.create(
            name="ACIContractTestAPI4",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
            qos_class="level1",
            scope="tenant",
            target_dscp="unspecified",
        )

        aci_contract_relations = (
            ACIContractRelation(
                aci_contract=aci_contract_epg1,
                aci_object=aci_epg1,
                role="prov",
                comments="# ACI Test 1",
            ),
            ACIContractRelation(
                aci_contract=aci_contract_epg1,
                aci_object=aci_epg2,
                role="cons",
                comments="# ACI Test 2",
            ),
            ACIContractRelation(
                aci_contract=aci_contract_epg1,
                aci_object=aci_useg_epg1,
                role="prov",
                comments="# ACI Test 3",
            ),
            ACIContractRelation(
                aci_contract=aci_contract_epg1,
                aci_object=aci_useg_epg2,
                role="cons",
                comments="# ACI Test 4",
            ),
            ACIContractRelation(
                aci_contract=aci_contract_epg1,
                aci_object=aci_vrf1,
                role="prov",
                comments="# ACI Test 5",
            ),
            ACIContractRelation(
                aci_contract=aci_contract_epg1,
                aci_object=aci_vrf1,
                role="cons",
                comments="# ACI Test 6",
            ),
            ACIContractRelation(
                aci_contract=aci_contract_esg1,
                aci_object=aci_esg1,
                role="prov",
                comments="# ACI Test 7",
            ),
            ACIContractRelation(
                aci_contract=aci_contract_esg1,
                aci_object=aci_esg2,
                role="cons",
                comments="# ACI Test 8",
            ),
            ACIContractRelation(
                aci_contract=aci_contract_esg1,
                aci_object=aci_vrf1,
                role="cons",
                comments="# ACI Test 9",
            ),
        )
        ACIContractRelation.objects.bulk_create(aci_contract_relations)

        cls.create_data: list[dict] = [
            {
                "aci_contract": aci_contract_epg2.id,
                "aci_object_id": aci_epg3.id,
                "aci_object_type": f"{app_name}.aciendpointgroup",
                "role": "cons",
                "comments": "# ACI Test 10",
            },
            {
                "aci_contract": aci_contract_epg2.id,
                "aci_object_id": aci_epg4.id,
                "aci_object_type": f"{app_name}.aciendpointgroup",
                "role": "prov",
                "comments": "# ACI Test 11",
            },
            {
                "aci_contract": aci_contract_epg2.id,
                "aci_object_id": aci_useg_epg3.id,
                "aci_object_type": f"{app_name}.aciusegendpointgroup",
                "role": "cons",
                "comments": "# ACI Test 12",
            },
            {
                "aci_contract": aci_contract_epg2.id,
                "aci_object_id": aci_useg_epg4.id,
                "aci_object_type": f"{app_name}.aciusegendpointgroup",
                "role": "prov",
                "comments": "# ACI Test 13",
            },
            {
                "aci_contract": aci_contract_epg2.id,
                "aci_object_id": aci_vrf2.id,
                "aci_object_type": f"{app_name}.acivrf",
                "role": "cons",
                "comments": "# ACI Test 14",
            },
            {
                "aci_contract": aci_contract_esg2.id,
                "aci_object_id": aci_esg3.id,
                "aci_object_type": f"{app_name}.aciendpointsecuritygroup",
                "role": "cons",
                "comments": "# ACI Test 15",
            },
            {
                "aci_contract": aci_contract_esg2.id,
                "aci_object_id": aci_esg4.id,
                "aci_object_type": f"{app_name}.aciendpointsecuritygroup",
                "role": "prov",
                "comments": "# ACI Test 16",
            },
            {
                "aci_contract": aci_contract_esg2.id,
                "aci_object_id": aci_vrf2.id,
                "aci_object_type": f"{app_name}.acivrf",
                "role": "cons",
                "comments": "# ACI Test 17",
            },
        ]
        cls.bulk_update_data = {
            "comments": "ACI comment bulk update",
        }


class ACIContractSubjectAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract Subject."""

    model = ACIContractSubject
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_contract",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acicontract",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Subject for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_contract1 = ACIContract.objects.create(
            name="ACIContractTestAPI1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
            qos_class="unspecified",
            scope="context",
            target_dscp="unspecified",
        )
        aci_contract2 = ACIContract.objects.create(
            name="ACIContractTestAPI2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
            qos_class="level1",
            scope="tenant",
            target_dscp="unspecified",
        )

        aci_contract_subjects = (
            ACIContractSubject(
                name="ACIContractSubjectTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_contract=aci_contract1,
                nb_tenant=nb_tenant1,
                apply_both_directions_enabled=True,
                qos_class="unspecified",
                reverse_filter_ports_enabled=True,
                service_graph_name="ServiceGraph1",
                target_dscp="unspecified",
            ),
            ACIContractSubject(
                name="ACIContractSubjectTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_contract=aci_contract2,
                nb_tenant=nb_tenant1,
                apply_both_directions_enabled=True,
                qos_class="level3",
                reverse_filter_ports_enabled=True,
                service_graph_name="ServiceGraph2",
                target_dscp="EF",
            ),
            ACIContractSubject(
                name="ACIContractSubjectTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_contract=aci_contract1,
                nb_tenant=nb_tenant2,
                apply_both_directions_enabled=True,
                qos_class="level6",
                reverse_filter_ports_enabled=True,
                service_graph_name="ServiceGraph3",
                target_dscp="CS3",
            ),
        )
        ACIContractSubject.objects.bulk_create(aci_contract_subjects)

        cls.create_data: list[dict] = [
            {
                "name": "ACIContractSubjectTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_contract": aci_contract1.id,
                "nb_tenant": nb_tenant1.id,
                "apply_both_directions_enabled": True,
                "qos_class": "level1",
                "reverse_filter_ports_enabled": True,
                "service_graph_name": "ServiceGraph4",
                "target_dscp": "unspecified",
            },
            {
                "name": "ACIContractSubjectTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_contract": aci_contract2.id,
                "nb_tenant": nb_tenant2.id,
                "apply_both_directions_enabled": True,
                "qos_class": "level2",
                "reverse_filter_ports_enabled": True,
                "service_graph_name": "ServiceGraph4",
                "target_dscp": "VA",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIContractSubjectFilterAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract Subject Filter."""

    model = ACIContractSubjectFilter
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_contract_filter",
        "aci_contract_subject",
        "action",
        "display",
        "id",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acicontractfilter",
        "netbox_aci_plugin.view_acicontractsubject",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Subject Filter for API view testing."""
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
        aci_contract_filter3 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI3",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant2,
        )
        aci_contract_filter4 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI4",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant1,
        )
        aci_contract1 = ACIContract.objects.create(
            name="ACIContractTestAPI1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
            qos_class="unspecified",
            scope="context",
            target_dscp="unspecified",
        )
        aci_contract2 = ACIContract.objects.create(
            name="ACIContractTestAPI2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
            qos_class="level1",
            scope="tenant",
            target_dscp="unspecified",
        )
        aci_contract_subject1 = ACIContractSubject.objects.create(
            name="ACIContractSubjectTestAPI1",
            aci_contract=aci_contract1,
            nb_tenant=nb_tenant1,
            apply_both_directions_enabled=True,
            qos_class="unspecified",
            reverse_filter_ports_enabled=True,
            target_dscp="unspecified",
        )
        aci_contract_subject2 = ACIContractSubject.objects.create(
            name="ACIContractSubjectTestAPI2",
            aci_contract=aci_contract2,
            nb_tenant=nb_tenant2,
            apply_both_directions_enabled=True,
            qos_class="unspecified",
            reverse_filter_ports_enabled=True,
            target_dscp="unspecified",
        )

        aci_contract_subject_filters = (
            ACIContractSubjectFilter(
                aci_contract_filter=aci_contract_filter1,
                aci_contract_subject=aci_contract_subject1,
                action="permit",
                apply_direction="both",
                log_enabled=True,
                policy_compression_enabled=False,
                priority="default",
            ),
            ACIContractSubjectFilter(
                aci_contract_filter=aci_contract_filter2,
                aci_contract_subject=aci_contract_subject2,
                action="permit",
                apply_direction="both",
                log_enabled=False,
                policy_compression_enabled=True,
                priority="level1",
            ),
            ACIContractSubjectFilter(
                aci_contract_filter=aci_contract_filter1,
                aci_contract_subject=aci_contract_subject2,
                action="deny",
                apply_direction="ctp",
                log_enabled=False,
                policy_compression_enabled=True,
                priority="level3",
            ),
        )
        ACIContractSubjectFilter.objects.bulk_create(aci_contract_subject_filters)

        cls.create_data: list[dict] = [
            {
                "aci_contract_filter": aci_contract_filter3.id,
                "aci_contract_subject": aci_contract_subject1.id,
                "action": "permit",
                "apply_direction": "both",
                "log_enabled": True,
                "policy_compression_enabled": False,
                "priority": "default",
            },
            {
                "aci_contract_filter": aci_contract_filter4.id,
                "aci_contract_subject": aci_contract_subject2.id,
                "action": "permit",
                "apply_direction": "both",
                "log_enabled": True,
                "policy_compression_enabled": False,
                "priority": "default",
            },
        ]
        cls.bulk_update_data = {"priority": "level2"}
