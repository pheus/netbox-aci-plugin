# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase


class AppTest(APITestCase):
    """API test case for NetBox ACI plugin."""

    def test_root(self) -> None:
        """Test API root access of the plugin."""
        url = reverse("plugins-api:netbox_aci_plugin-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
