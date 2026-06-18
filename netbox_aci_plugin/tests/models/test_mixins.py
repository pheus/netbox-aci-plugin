# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the ACI model mixins."""

from django.test import TestCase

from ...models.mixins import UniqueGenericForeignKeyMixin


class UniqueGenericForeignKeyMixinTestCase(TestCase):
    """Tests for the GenericForeignKey uniqueness mixin contract."""

    def test_validate_generic_uniqueness_requires_fk_field(self) -> None:
        """Test the uniqueness check rejects a missing generic_fk_field."""

        class _Stub(UniqueGenericForeignKeyMixin):
            pass

        with self.assertRaises(NotImplementedError):
            _Stub()._validate_generic_uniqueness()  # noqa: SLF001
