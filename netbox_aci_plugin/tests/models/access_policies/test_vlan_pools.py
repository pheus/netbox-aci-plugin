# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the ACI VLAN pool models."""

from django.core.exceptions import ValidationError
from django.db.backends.postgresql.psycopg_any import NumericRange

from ipam.models import VLANGroup
from tenancy.models import Tenant

from ....choices import (
    VLANAllocationModeChoices,
    VLANPoolRangeAllocationModeChoices,
    VLANPoolRangeRoleChoices,
)
from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ....models.fabric.fabrics import ACIFabric
from ..base import ACIBaseTestCase


class ACIVLANPoolTestCase(ACIBaseTestCase):
    """Test case for the ACIVLANPool model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIVLANPool model."""
        super().setUpTestData()

        cls.aci_vlan_pool_name = "ACITestVLANPool"
        cls.aci_vlan_pool_alias = "ACITestVLANPoolAlias"
        cls.aci_vlan_pool_description = "ACI Test VLAN Pool for NetBox ACI Plugin"
        cls.aci_vlan_pool_comments = """
        ACI VLAN Pool for NetBox ACI Plugin testing.
        """
        cls.aci_vlan_pool_allocation_mode = VLANAllocationModeChoices.MODE_DYNAMIC

        # Create objects
        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name=cls.aci_vlan_pool_name,
            name_alias=cls.aci_vlan_pool_alias,
            description=cls.aci_vlan_pool_description,
            comments=cls.aci_vlan_pool_comments,
            aci_fabric=cls.aci_fabric,
            allocation_mode=cls.aci_vlan_pool_allocation_mode,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_vlan_pool_instance(self) -> None:
        """Test type of created ACI VLAN Pool."""
        self.assertTrue(isinstance(self.aci_vlan_pool, ACIVLANPool))

    def test_aci_vlan_pool_str(self) -> None:
        """Test string value of created ACI VLAN Pool."""
        self.assertEqual(self.aci_vlan_pool.__str__(), self.aci_vlan_pool.name)

    def test_aci_vlan_pool_name_alias(self) -> None:
        """Test alias of created ACI VLAN Pool."""
        self.assertEqual(self.aci_vlan_pool.name_alias, self.aci_vlan_pool_alias)

    def test_aci_vlan_pool_description(self) -> None:
        """Test description of created ACI VLAN Pool."""
        self.assertEqual(self.aci_vlan_pool.description, self.aci_vlan_pool_description)

    def test_aci_vlan_pool_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance associated with ACI VLAN Pool."""
        self.assertTrue(isinstance(self.aci_vlan_pool.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_vlan_pool.aci_fabric.name, self.aci_fabric_name)

    def test_aci_vlan_pool_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI VLAN Pool."""
        self.assertTrue(isinstance(self.aci_vlan_pool.nb_tenant, Tenant))
        self.assertEqual(self.aci_vlan_pool.nb_tenant.name, self.nb_tenant_name)

    def test_aci_vlan_pool_allocation_mode(self) -> None:
        """Test the 'allocation mode' option of ACI VLAN Pool."""
        self.assertEqual(
            self.aci_vlan_pool.allocation_mode,
            self.aci_vlan_pool_allocation_mode,
        )

    def test_default_allocation_mode(self) -> None:
        """Test default allocation mode of ACI VLAN Pool."""
        pool = ACIVLANPool(name="VLANPoolTmp", aci_fabric=self.aci_fabric)
        self.assertEqual(pool.allocation_mode, VLANAllocationModeChoices.MODE_STATIC)

    def test_parent_object(self) -> None:
        """Test parent object of ACI VLAN Pool."""
        self.assertEqual(self.aci_vlan_pool1.parent_object, self.aci_fabric)

    def test_get_allocation_mode_color(self) -> None:
        """Test allocation mode color of ACI VLAN Pool."""
        self.assertEqual(
            self.aci_vlan_pool1.get_allocation_mode_color(),
            VLANAllocationModeChoices.colors.get(VLANAllocationModeChoices.MODE_STATIC),
        )

    def test_unique_name_per_fabric(self) -> None:
        """Test uniqueness of ACI VLAN Pool name per ACI Fabric."""
        duplicate = ACIVLANPool(
            name=self.aci_vlan_pool1.name, aci_fabric=self.aci_fabric
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_clean_rejects_group_not_covering_existing_ranges(self) -> None:
        """Test rejection of a VLAN group not covering existing pool ranges."""
        group = VLANGroup.objects.create(
            name="VLANGroupTooNarrow",
            slug="vlan-group-too-narrow",
            vid_ranges=[NumericRange(100, 151)],  # covers 100-150 only
        )
        self.aci_vlan_pool1.nb_vlan_group = group  # pool1 has 100-199, 200-299
        with self.assertRaises(ValidationError) as cm:
            self.aci_vlan_pool1.full_clean()
        self.assertIn("nb_vlan_group", cm.exception.message_dict)

    def test_clean_allows_group_covering_existing_ranges(self) -> None:
        """Test acceptance of a VLAN group covering existing pool ranges."""
        group = VLANGroup.objects.create(
            name="VLANGroupWide",
            slug="vlan-group-wide",
            vid_ranges=[NumericRange(100, 300)],  # covers 100-299
        )
        self.aci_vlan_pool1.nb_vlan_group = group
        self.aci_vlan_pool1.full_clean()  # all ranges fit -> no error

    def test_clean_allows_group_on_pool_without_ranges(self) -> None:
        """Test acceptance of a VLAN group on a pool without ranges."""
        group = VLANGroup.objects.create(
            name="VLANGroupNoRanges",
            slug="vlan-group-no-ranges",
            vid_ranges=[NumericRange(100, 151)],
        )
        pool = ACIVLANPool.objects.create(
            name="VLANPoolNoRanges", aci_fabric=self.aci_fabric
        )
        pool.nb_vlan_group = group
        pool.full_clean()  # no ranges -> nothing to validate


class ACIVLANPoolRangeTestCase(ACIBaseTestCase):
    """Test case for the ACIVLANPoolRange model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIVLANPoolRange model."""
        super().setUpTestData()
        cls.nb_vlan_group = VLANGroup.objects.create(
            name="VLANGroupRange",
            slug="vlan-group-range",
            vid_ranges=[NumericRange(1000, 1100)],  # covers 1000-1099
        )
        cls.aci_vlan_pool_grouped = ACIVLANPool.objects.create(
            name="VLANPoolGrouped",
            aci_fabric=cls.aci_fabric,
            nb_vlan_group=cls.nb_vlan_group,
        )

    def test_aci_vlan_pool_range_instance(self) -> None:
        """Test type of created ACI VLAN Pool Range."""
        self.assertTrue(isinstance(self.aci_vlan_pool_range1, ACIVLANPoolRange))

    def test_aci_vlan_pool_range_str(self) -> None:
        """Test string value of created ACI VLAN Pool Range."""
        self.assertEqual(str(self.aci_vlan_pool_range1), "100-199")

    def test_default_allocation_mode_and_role(self) -> None:
        """Test default allocation mode and role of ACI VLAN Pool Range."""
        rng = ACIVLANPoolRange(
            aci_vlan_pool=self.aci_vlan_pool1,
            vlan_id_from=400,
            vlan_id_to=499,
        )
        self.assertEqual(
            rng.allocation_mode,
            VLANPoolRangeAllocationModeChoices.MODE_INHERIT,
        )
        self.assertEqual(rng.role, VLANPoolRangeRoleChoices.ROLE_EXTERNAL)

    def test_parent_object(self) -> None:
        """Test parent object of ACI VLAN Pool Range."""
        self.assertEqual(self.aci_vlan_pool_range1.parent_object, self.aci_vlan_pool1)

    def test_clean_rejects_inverted_range(self) -> None:
        """Test rejection of an inverted ACI VLAN Pool Range."""
        rng = ACIVLANPoolRange(
            aci_vlan_pool=self.aci_vlan_pool1, vlan_id_from=50, vlan_id_to=10
        )
        with self.assertRaises(ValidationError) as cm:
            rng.full_clean()
        self.assertIn("vlan_id_to", cm.exception.message_dict)

    def test_clean_rejects_overlapping_range(self) -> None:
        """Test rejection of an overlapping ACI VLAN Pool Range."""
        rng = ACIVLANPoolRange(
            aci_vlan_pool=self.aci_vlan_pool1, vlan_id_from=150, vlan_id_to=250
        )
        with self.assertRaises(ValidationError) as cm:
            rng.full_clean()
        self.assertIn("vlan_id_from", cm.exception.message_dict)

    def test_clean_allows_non_overlapping_range(self) -> None:
        """Test acceptance of a non-overlapping ACI VLAN Pool Range."""
        rng = ACIVLANPoolRange(
            aci_vlan_pool=self.aci_vlan_pool1, vlan_id_from=300, vlan_id_to=399
        )
        rng.full_clean()

    def test_clean_allows_range_within_group(self) -> None:
        """Test acceptance of an ACI VLAN Pool Range within the VLAN group."""
        rng = ACIVLANPoolRange(
            aci_vlan_pool=self.aci_vlan_pool_grouped,
            vlan_id_from=1000,
            vlan_id_to=1099,
        )
        rng.full_clean()  # within the group's ranges -> no error

    def test_clean_rejects_range_outside_group(self) -> None:
        """Test keying the group error to the end when only it is outside."""
        rng = ACIVLANPoolRange(
            aci_vlan_pool=self.aci_vlan_pool_grouped,
            vlan_id_from=1000,  # inside the group (1000-1099)
            vlan_id_to=1200,  # above the group
        )
        with self.assertRaises(ValidationError) as cm:
            rng.full_clean()
        self.assertIn("vlan_id_to", cm.exception.message_dict)
        self.assertNotIn("vlan_id_from", cm.exception.message_dict)

    def test_clean_keys_group_error_to_start_field(self) -> None:
        """Test keying the group error to the start when only it is outside."""
        rng = ACIVLANPoolRange(
            aci_vlan_pool=self.aci_vlan_pool_grouped,
            vlan_id_from=900,  # below the group (1000-1099)
            vlan_id_to=1099,  # inside the group
        )
        with self.assertRaises(ValidationError) as cm:
            rng.full_clean()
        self.assertIn("vlan_id_from", cm.exception.message_dict)
        self.assertNotIn("vlan_id_to", cm.exception.message_dict)

    def test_clean_skips_group_check_when_no_group(self) -> None:
        """Test skipping the VLAN group check when no group is set."""
        rng = ACIVLANPoolRange(
            aci_vlan_pool=self.aci_vlan_pool1,  # no nb_vlan_group
            vlan_id_from=3000,
            vlan_id_to=3099,
        )
        rng.full_clean()  # no group -> containment not checked
