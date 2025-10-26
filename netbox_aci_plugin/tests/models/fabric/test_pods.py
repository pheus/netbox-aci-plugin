# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from ipam.models import Prefix
from tenancy.models import Tenant

from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.pods import ACIPod
from ..base import ACIBaseTestCase


class ACIPodTestCase(ACIBaseTestCase):
    """Test case for ACIPod model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIPod model."""
        super().setUpTestData()

        cls.aci_pod_name = "ACITestPod"
        cls.aci_pod_alias = "ACITestPodAlias"
        cls.aci_pod_description = "ACI Test Pod for NetBox ACI Plugin"
        cls.aci_pod_comments = """
        ACI Pod for NetBox ACI Plugin testing.
        """
        cls.aci_pod_id = 10
        cls.aci_pod_tep_pool_prefix = "10.0.0.0/19"

        # Create related objects
        cls.aci_pod_tep_pool = Prefix.objects.create(prefix=cls.aci_pod_tep_pool_prefix)

        # Create objects
        cls.aci_pod = ACIPod.objects.create(
            name=cls.aci_pod_name,
            name_alias=cls.aci_pod_alias,
            description=cls.aci_pod_description,
            pod_id=cls.aci_pod_id,
            aci_fabric=cls.aci_fabric,
            tep_pool=cls.aci_pod_tep_pool,
            nb_tenant=cls.nb_tenant,
            comments=cls.aci_pod_comments,
        )

    def test_aci_pod_instance(self) -> None:
        """Test type of created ACI Pod."""
        self.assertTrue(isinstance(self.aci_pod, ACIPod))

    def test_aci_pod_str_return_value(self) -> None:
        """Test string value of created ACI Pod."""
        self.assertEqual(self.aci_pod.__str__(), self.aci_pod.name)

    def test_aci_pod_alias(self) -> None:
        """Test alias of ACI Pod."""
        self.assertEqual(self.aci_pod.name_alias, self.aci_pod_alias)

    def test_aci_pod_description(self) -> None:
        """Test description of ACI Pod."""
        self.assertEqual(self.aci_pod.description, self.aci_pod_description)

    def test_aci_pod_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance associated with ACI Pod."""
        self.assertTrue(isinstance(self.aci_pod.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_pod.aci_fabric.name, self.aci_fabric_name)

    def test_aci_pod_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Pod."""
        self.assertTrue(isinstance(self.aci_pod.nb_tenant, Tenant))
        self.assertEqual(self.aci_pod.nb_tenant.name, self.nb_tenant_name)

    def test_aci_pod_pod_id(self) -> None:
        """Test pod ID of ACI Pod."""
        self.assertEqual(self.aci_pod.pod_id, self.aci_pod_id)

    def test_aci_pod_tep_pool(self) -> None:
        """Test the NetBox Prefix associated with ACI Pod."""
        self.assertTrue(isinstance(self.aci_pod.tep_pool, Prefix))
        self.assertEqual(self.aci_pod.tep_pool, self.aci_pod_tep_pool)
        self.assertEqual(
            str(self.aci_pod.tep_pool.prefix), self.aci_pod_tep_pool_prefix
        )

    def test_invalid_aci_pod_name(self) -> None:
        """Test validation of ACI Pod naming."""
        pod = ACIPod(
            name="ACI Test Pod 1",
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_pod_name_length(self) -> None:
        """Test validation of ACI Pod name length."""
        pod = ACIPod(
            name="T" * 65,  # Exceeding the maximum length of 64
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_pod_name_alias(self) -> None:
        """Test validation of ACI pod aliasing."""
        pod = ACIPod(
            name="ACIPodTest1",
            name_alias="Invalid Alias",
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_pod_description(self) -> None:
        """Test validation of ACI Pod description."""
        pod = ACIPod(
            name="ACITestPod1",
            description="Invalid Description: ö",
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_pod_description_length(self) -> None:
        """Test validation of ACI Pod description length."""
        pod = ACIPod(
            name="ACITestPod1",
            description="T" * 129,  # Exceeding the maximum length of 128
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_pod_id(self) -> None:
        """Test validation of ACI Pod ID value."""
        pod = ACIPod(
            name="ACITestPod1",
            aci_fabric=self.aci_fabric,
            pod_id=5000,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("pod_id", cm.exception.error_dict)

    def test_invalid_aci_pod_tep_pool(self) -> None:
        """Test validation of the ACI Pod TEP pool prefix."""
        invalid_tep_pool = Prefix(prefix="10.0.0.0/27")
        invalid_tep_pool.full_clean()
        invalid_tep_pool.save()
        pod = ACIPod(
            name="ACITestPod1",
            aci_fabric=self.aci_fabric,
            pod_id=20,
            tep_pool=invalid_tep_pool,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("tep_pool", cm.exception.error_dict)

    def test_constraint_unique_aci_pod_name(self) -> None:
        """Test unique constraint of ACI Pod name."""
        duplicate_pod = ACIPod(
            name=self.aci_pod_name,
            aci_fabric=self.aci_fabric,
            pod_id=100,
        )
        with self.assertRaises(IntegrityError):
            duplicate_pod.save()

    def test_constraint_unique_aci_pod_id(self) -> None:
        """Test unique constraint of ACI Pod ID."""
        duplicate_pod = ACIPod(
            name="ACITestPod1",
            aci_fabric=self.aci_fabric,
            pod_id=self.aci_pod_id,
        )
        with self.assertRaises(IntegrityError):
            duplicate_pod.save()
