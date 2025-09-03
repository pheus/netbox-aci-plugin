# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tenancy.models import Tenant

from ....choices import (
    ContractFilterARPOpenPeripheralCodesChoices,
    ContractFilterEtherTypeChoices,
    ContractFilterICMPv4TypesChoices,
    ContractFilterICMPv6TypesChoices,
    ContractFilterIPProtocolChoices,
    ContractFilterPortChoices,
    ContractFilterTCPRulesChoices,
    QualityOfServiceDSCPChoices,
)
from ....models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ....models.tenant.tenants import ACITenant


class ACIContractFilterTestCase(TestCase):
    """Test case for ACIContractFilter model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilter model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_filter_name = "ACITestContractFilter"
        cls.aci_contract_filter_alias = "ACITestContractFilterAlias"
        cls.aci_contract_filter_description = (
            "ACI Test Contract Filter for NetBox ACI Plugin"
        )
        cls.aci_contract_filter_comments = """
        ACI Contract Filter for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_contract_filter = ACIContractFilter.objects.create(
            name=cls.aci_contract_filter_name,
            name_alias=cls.aci_contract_filter_alias,
            description=cls.aci_contract_filter_description,
            comments=cls.aci_contract_filter_comments,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_contract_filter_instance(self) -> None:
        """Test type of created ACI Contract Filter."""
        self.assertTrue(isinstance(self.aci_contract_filter, ACIContractFilter))

    def test_aci_contract_filter_str(self) -> None:
        """Test string value of created ACI Contract Filter."""
        self.assertEqual(
            self.aci_contract_filter.__str__(), self.aci_contract_filter.name
        )

    def test_aci_contract_filter_alias(self) -> None:
        """Test alias of ACI Contract Filter."""
        self.assertEqual(
            self.aci_contract_filter.name_alias, self.aci_contract_filter_alias
        )

    def test_aci_contract_filter_description(self) -> None:
        """Test description of ACI Contract Filter."""
        self.assertEqual(
            self.aci_contract_filter.description,
            self.aci_contract_filter_description,
        )

    def test_aci_contract_filter_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI Contract Filter."""
        self.assertTrue(isinstance(self.aci_contract_filter.aci_tenant, ACITenant))

    def test_aci_contract_filter_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI Contract Filter."""
        self.assertEqual(self.aci_contract_filter.aci_tenant.name, self.aci_tenant_name)

    def test_aci_contract_filter_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with Contract Filter."""
        self.assertTrue(isinstance(self.aci_contract_filter.nb_tenant, Tenant))

    def test_aci_contract_filter_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI Contract Filter."""
        self.assertEqual(self.aci_contract_filter.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_contract_filter_name(self) -> None:
        """Test validation of ACI Contract Filter naming."""
        contract_filter = ACIContractFilter(name="ACI Contract Filter Test 1")
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_name_length(self) -> None:
        """Test validation of ACI Contract Filter name length."""
        contract_filter = ACIContractFilter(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_name_alias(self) -> None:
        """Test validation of ACI Contract Filter aliasing."""
        contract_filter = ACIContractFilter(
            name="ACIContractFilterTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_name_alias_length(self) -> None:
        """Test validation of ACI Contract Filter name alias length."""
        contract_filter = ACIContractFilter(
            name="ACIContractFilterTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_description(self) -> None:
        """Test validation of ACI Contract Filter description."""
        contract_filter = ACIContractFilter(
            name="ACIContractFilterTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_description_length(self) -> None:
        """Test validation of ACI Contract Filter description length."""
        contract_filter = ACIContractFilter(
            name="ACIContractFilterTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_constraint_unique_aci_contract_filter_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI ContractFilter name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        duplicate_contract_filter = ACIContractFilter(
            name=self.aci_contract_filter_name, aci_tenant=tenant
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract_filter.save()


class ACIContractFilterEntryTestCase(TestCase):
    """Test case for ACIContractFilterEntry model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilterEntry model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_filter_name = "ACITestContractFilter"
        cls.aci_contract_filter_entry_name = "ACITestContractFilterEntry"
        cls.aci_contract_filter_entry_alias = "ACITestContractFilterEntryAlias"
        cls.aci_contract_filter_entry_description = (
            "ACI Test Contract Filter Entry for NetBox ACI Plugin"
        )
        cls.aci_contract_filter_entry_comments = """
        ACI Contract Filter Entry for NetBox ACI Plugin testing.
        """
        cls.aci_contract_filter_entry_arp_opc = (
            ContractFilterARPOpenPeripheralCodesChoices.OPC_REQUEST
        )
        cls.aci_contract_filter_entry_dest_from_port = (
            ContractFilterPortChoices.PORT_SSH
        )
        cls.aci_contract_filter_entry_dest_to_port = ContractFilterPortChoices.PORT_DNS
        cls.aci_contract_filter_entry_ether_type = (
            ContractFilterEtherTypeChoices.TYPE_IP
        )
        cls.aci_contract_filter_entry_icmp_v4_type = (
            ContractFilterICMPv4TypesChoices.ICMP_V4_ECHO_REQUEST
        )
        cls.aci_contract_filter_entry_icmp_v6_type = (
            ContractFilterICMPv6TypesChoices.ICMP_V6_UNSPECIFIED
        )
        cls.aci_contract_filter_entry_ip_protocol = (
            ContractFilterIPProtocolChoices.PROT_TCP
        )
        cls.aci_contract_filter_entry_match_dscp = QualityOfServiceDSCPChoices.DSCP_AF42
        cls.aci_contract_filter_entry_match_only_fragments_enabled = False
        cls.aci_contract_filter_entry_src_from_port = 0
        cls.aci_contract_filter_entry_src_to_port = 65535
        cls.aci_contract_filter_entry_stateful_enabled = False
        cls.aci_contract_filter_entry_tcp_rules = [
            ContractFilterTCPRulesChoices.TCP_SYN,
            ContractFilterTCPRulesChoices.TCP_FINISH,
        ]

        # Create objects
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_contract_filter = ACIContractFilter.objects.create(
            name=cls.aci_contract_filter_name,
            aci_tenant=cls.aci_tenant,
        )
        cls.aci_contract_filter_entry = ACIContractFilterEntry.objects.create(
            name=cls.aci_contract_filter_entry_name,
            name_alias=cls.aci_contract_filter_entry_alias,
            description=cls.aci_contract_filter_entry_description,
            comments=cls.aci_contract_filter_entry_comments,
            aci_contract_filter=cls.aci_contract_filter,
            arp_opc=cls.aci_contract_filter_entry_arp_opc,
            destination_from_port=cls.aci_contract_filter_entry_dest_from_port,
            destination_to_port=cls.aci_contract_filter_entry_dest_to_port,
            ether_type=cls.aci_contract_filter_entry_ether_type,
            icmp_v4_type=cls.aci_contract_filter_entry_icmp_v4_type,
            icmp_v6_type=cls.aci_contract_filter_entry_icmp_v6_type,
            ip_protocol=cls.aci_contract_filter_entry_ip_protocol,
            match_dscp=cls.aci_contract_filter_entry_match_dscp,
            match_only_fragments_enabled=(
                cls.aci_contract_filter_entry_match_only_fragments_enabled
            ),
            source_from_port=cls.aci_contract_filter_entry_src_from_port,
            source_to_port=cls.aci_contract_filter_entry_src_to_port,
            stateful_enabled=cls.aci_contract_filter_entry_stateful_enabled,
            tcp_rules=cls.aci_contract_filter_entry_tcp_rules,
        )

    def test_aci_contract_filter_entry_instance(self) -> None:
        """Test type of created ACI Contract Filter Entry."""
        self.assertTrue(
            isinstance(self.aci_contract_filter_entry, ACIContractFilterEntry)
        )

    def test_aci_contract_filter_entry_str(self) -> None:
        """Test string value of created ACI Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.__str__(),
            f"{self.aci_contract_filter_entry_name} ({self.aci_contract_filter_name})",
        )

    def test_aci_contract_filter_entry_alias(self) -> None:
        """Test alias of ACI Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.name_alias,
            self.aci_contract_filter_entry_alias,
        )

    def test_aci_contract_filter_entry_description(self) -> None:
        """Test description of ACI Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.description,
            self.aci_contract_filter_entry_description,
        )

    def test_aci_contract_filter_entry_aci_contract_filter_instance(
        self,
    ) -> None:
        """Test the Filter instance associated with Contract Filter Entry."""
        self.assertTrue(
            isinstance(
                self.aci_contract_filter_entry.aci_contract_filter,
                ACIContractFilter,
            )
        )

    def test_aci_contract_filter_entry_aci_contract_filter_name(self) -> None:
        """Test the Filter name associated with Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.aci_contract_filter.name,
            self.aci_contract_filter_name,
        )

    def test_aci_contract_filter_entry_arp_opc(self) -> None:
        """Test the 'arp_opc' option of ACI Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.arp_opc,
            self.aci_contract_filter_entry_arp_opc,
        )

    def test_aci_contract_filter_entry_destination_from_port(self) -> None:
        """Test the 'destination_from_port' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.destination_from_port,
            self.aci_contract_filter_entry_dest_from_port,
        )

    def test_aci_contract_filter_entry_destination_to_port(self) -> None:
        """Test the 'destination_to_port' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.destination_to_port,
            self.aci_contract_filter_entry_dest_to_port,
        )

    def test_aci_contract_filter_entry_ether_type(self) -> None:
        """Test the 'ether_type' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.ether_type,
            self.aci_contract_filter_entry_ether_type,
        )

    def test_aci_contract_filter_entry_icmp_v4_type(self) -> None:
        """Test the 'icmp_v4_type' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.icmp_v4_type,
            self.aci_contract_filter_entry_icmp_v4_type,
        )

    def test_aci_contract_filter_entry_icmp_v6_type(self) -> None:
        """Test the 'icmp_v6_type' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.icmp_v6_type,
            self.aci_contract_filter_entry_icmp_v6_type,
        )

    def test_aci_contract_filter_entry_ip_protocol(self) -> None:
        """Test the 'ip_protocol' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.ip_protocol,
            self.aci_contract_filter_entry_ip_protocol,
        )

    def test_aci_contract_filter_entry_match_dscp(self) -> None:
        """Test the 'match_dscp' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.match_dscp,
            self.aci_contract_filter_entry_match_dscp,
        )

    def test_aci_contract_filter_entry_match_only_fragments_enabled(
        self,
    ) -> None:
        """Test the 'match_only_fragments_enabled' option of Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.match_only_fragments_enabled,
            self.aci_contract_filter_entry_match_only_fragments_enabled,
        )

    def test_aci_contract_filter_entry_source_from_port(self) -> None:
        """Test the 'source_from_port' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.source_from_port,
            self.aci_contract_filter_entry_src_from_port,
        )

    def test_aci_contract_filter_entry_source_to_port(self) -> None:
        """Test the 'source_to_port' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.source_to_port,
            self.aci_contract_filter_entry_src_to_port,
        )

    def test_aci_contract_filter_entry_stateful_enabled(self) -> None:
        """Test the 'stateful_enabled' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.stateful_enabled,
            self.aci_contract_filter_entry_stateful_enabled,
        )

    def test_aci_contract_filter_entry_tcp_rules(self) -> None:
        """Test the 'tcp_rules' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.tcp_rules,
            self.aci_contract_filter_entry_tcp_rules,
        )

    def test_invalid_aci_contract_filter_entry_name(self) -> None:
        """Test validation of ACI Contract Filter Entry naming."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACI Contract Filter Entry Test 1"
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_name_length(self) -> None:
        """Test validation of ACI Contract Filter Entry name length."""
        contract_filter_entry = ACIContractFilterEntry(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_name_alias(self) -> None:
        """Test validation of ACI Contract Filter Entry aliasing."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_name_alias_length(self) -> None:
        """Test validation of ACI Contract Filter Entry name alias length."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_description(self) -> None:
        """Test validation of ACI Contract Filter Entry description."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            description="Invalid Description: ö",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_description_length(
        self,
    ) -> None:
        """Test validation of ACI Contract Filter Entry description length."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_ip_protocol_number(
        self,
    ) -> None:
        """Test validation of ACI Contract Filter Entry IP Protocol number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="2200",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_ip_protocol_choice(
        self,
    ) -> None:
        """Test validation of ACI Contract Filter Entry IP Protocol choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="chaos",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_destination_from_port_number(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination From Port number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            destination_from_port=65536,
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_destination_from_port_choice(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination From Port choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            destination_from_port="ftp",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_destination_to_port_number(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination To Port number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            destination_to_port=65536,
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_destination_to_port_choice(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination To Port choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            destination_to_port="ftp",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_source_from_port_number(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination From Port number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            source_from_port=65536,
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_source_from_port_choice(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination From Port choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            source_from_port="ftp",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_source_to_port_number(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination To Port number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            source_to_port=65536,
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_source_to_port_choice(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination To Port choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            source_to_port="ftp",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_tcp_rules_established(
        self,
    ) -> None:
        """Test validation of the TCP rule combination with 'established'."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            tcp_rules=[
                ContractFilterTCPRulesChoices.TCP_ESTABLISHED,
                ContractFilterTCPRulesChoices.TCP_SYN,
            ],
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_tcp_rules_unspecified(
        self,
    ) -> None:
        """Test validation of the TCP rule combination with 'unspecified'."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            tcp_rules=[
                ContractFilterTCPRulesChoices.TCP_UNSPECIFIED,
                ContractFilterTCPRulesChoices.TCP_SYN,
            ],
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_ether_type_arp_opc(
        self,
    ) -> None:
        """Test validation of the ether_type and arp_opc combination."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            arp_opc=ContractFilterARPOpenPeripheralCodesChoices.OPC_REQUEST,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("arp_opc", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_ether_type_ip_protocol(
        self,
    ) -> None:
        """Test validation of the ether_type and ip_protocol combination."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="arp",
            ip_protocol="icmp",
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("ip_protocol", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_ether_type_ports(self) -> None:
        """Test validation of the ether_type and port combination."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            ip_protocol="icmp",
            destination_from_port="443",
            destination_to_port="443",
            source_from_port="https",
            source_to_port="https",
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only four errors
        exception = context_manager.exception
        self.assertIn("destination_from_port", exception.message_dict)
        self.assertIn("destination_to_port", exception.message_dict)
        self.assertIn("source_from_port", exception.message_dict)
        self.assertIn("source_to_port", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 4)

    def test_invalid_aci_contract_filter_entry_icmp_v4_type(self) -> None:
        """Test validation of the ether_type, ip_protocol, and icmp."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            ip_protocol="tcp",
            icmp_v4_type=ContractFilterICMPv4TypesChoices.ICMP_V4_ECHO_REQUEST,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("icmp_v4_type", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_icmp_v6_type(self) -> None:
        """Test validation of the ether_type, ip_protocol, and icmp_v6."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            ip_protocol="tcp",
            icmp_v6_type=ContractFilterICMPv6TypesChoices.ICMP_V6_ECHO_REQUEST,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("icmp_v6_type", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_match_dscp(self) -> None:
        """Test validation of the ether_type, and match_dscp."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="arp",
            match_dscp=QualityOfServiceDSCPChoices.DSCP_EF,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("match_dscp", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_match_fragments(self) -> None:
        """Test validation of the match_only_fragments_enabled."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="arp",
            match_only_fragments_enabled=True,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("match_only_fragments_enabled", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_ip_protocol_tcp_only(
        self,
    ) -> None:
        """Test validation of the ip_protocol and tcp settings combination."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            ip_protocol="udp",
            stateful_enabled=True,
            tcp_rules=[ContractFilterTCPRulesChoices.TCP_ESTABLISHED],
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only four errors
        exception = context_manager.exception
        self.assertIn("stateful_enabled", exception.message_dict)
        self.assertIn("tcp_rules", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 2)

    def test_constraint_unique_aci_filter_entry_name_per_aci_contract_filter(
        self,
    ) -> None:
        """Test unique constraint of ACI Contract Filter Entry name."""
        contract_filter = ACIContractFilter.objects.get(
            name=self.aci_contract_filter_name
        )
        duplicate_contract_filter_entry = ACIContractFilterEntry(
            name=self.aci_contract_filter_entry_name,
            aci_contract_filter=contract_filter,
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract_filter_entry.save()
