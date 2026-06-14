# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the tenant ACI Application Profile model."""

from utilities.testing import ViewTestCases, create_tags

from ....models.tenant.app_profiles import ACIAppProfile
from ..base import ACIModelViewTestCase


class ACIAppProfileViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIAppProfile."""

    model = ACIAppProfile

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAppProfile view tests."""
        super().setUpTestData()

        # 3 ACIAppProfile instances under the shared base tenant.
        ACIAppProfile.objects.create(
            name="ACIViewTestAppProfile1", aci_tenant=cls.aci_tenant
        )
        ACIAppProfile.objects.create(
            name="ACIViewTestAppProfile2", aci_tenant=cls.aci_tenant
        )
        ACIAppProfile.objects.create(
            name="ACIViewTestAppProfile3", aci_tenant=cls.aci_tenant
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestAppProfileX",
            "name_alias": "AppProfileXAlias",
            "description": "Form-data Application Profile",
            "aci_tenant": cls.aci_tenant.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        cls.csv_data = (
            "name,aci_fabric,aci_tenant,description",
            f"ACIViewTestAppProfile4,{fabric},{tenant},CSV App Profile 4",
            f"ACIViewTestAppProfile5,{fabric},{tenant},CSV App Profile 5",
            f"ACIViewTestAppProfile6,{fabric},{tenant},CSV App Profile 6",
        )

        app_profiles = list(ACIAppProfile.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{app_profiles[0].pk},Updated App Profile 1",
            f"{app_profiles[1].pk},Updated App Profile 2",
            f"{app_profiles[2].pk},Updated App Profile 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Application Profile"}
