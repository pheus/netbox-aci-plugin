# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the abstract ACI base models."""

from django.test import TestCase

from ...models.base import (
    ACIBaseModel,
    ACIFabricBaseModel,
    ACITenantBaseModel,
)


class ACIAbstractBaseModelTestCase(TestCase):
    """Tests for the abstract base-model property contracts."""

    def test_parent_object_requires_override(self) -> None:
        """Test ACIBaseModel.parent_object raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            ACIBaseModel.parent_object.fget(object())

    def test_aci_fabric_requires_override(self) -> None:
        """Test ACIFabricBaseModel.aci_fabric raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            ACIFabricBaseModel.aci_fabric.fget(object())

    def test_aci_tenant_requires_override(self) -> None:
        """Test ACITenantBaseModel.aci_tenant raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            ACITenantBaseModel.aci_tenant.fget(object())
