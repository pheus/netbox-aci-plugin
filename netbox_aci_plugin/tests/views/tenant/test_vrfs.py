# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the tenant ACI VRF model."""

from django.contrib.contenttypes.models import ContentType

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.contracts import ACIContractRelation
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIModelViewTestCase


class ACIVRFViewTestCase(ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase):
    """Standard view tests for ACIVRF."""

    model = ACIVRF

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVRF view tests."""
        super().setUpTestData()

        # The shared base VRF carries a PROTECT'd Bridge Domain child, so
        # NetBox's bulk-delete-everything assertion (count() == 0) can never
        # empty the real table. Scoping the test queryset to only our own
        # rows keeps every inherited view test on deletable leaves.
        cls.fixture_pks = list(ACIVRF.objects.values_list("pk", flat=True))

        # 3 ACIVRF instances under the shared base tenant.
        ACIVRF.objects.create(name="ACIViewTestVRF1", aci_tenant=cls.aci_tenant)
        ACIVRF.objects.create(name="ACIViewTestVRF2", aci_tenant=cls.aci_tenant)
        ACIVRF.objects.create(name="ACIViewTestVRF3", aci_tenant=cls.aci_tenant)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestVRFX",
            "name_alias": "VRFXAlias",
            "description": "Form-data VRF",
            "aci_tenant": cls.aci_tenant.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_tenant,pc_enforcement_direction,"
                "pc_enforcement_preference"
            ),
            f"ACIViewTestVRF4,{fabric},{tenant},ingress,enforced",
            f"ACIViewTestVRF5,{fabric},{tenant},ingress,enforced",
            f"ACIViewTestVRF6,{fabric},{tenant},ingress,enforced",
        )

        vrfs = list(ACIVRF.objects.exclude(pk__in=cls.fixture_pks).order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{vrfs[0].pk},Updated VRF 1",
            f"{vrfs[1].pk},Updated VRF 2",
            f"{vrfs[2].pk},Updated VRF 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited VRF"}

    def _get_queryset(self):
        return self.model.objects.exclude(pk__in=self.fixture_pks)

    def test_acivrf_bridgedomains_tab_add_button(self) -> None:
        """VRF Bridge Domains tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acivrf",
            "netbox_aci_plugin.view_acibridgedomain",
            "netbox_aci_plugin.add_acibridgedomain",
        )
        url = get_action_url(
            self.aci_vrf, action="bridgedomains", kwargs={"pk": self.aci_vrf.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIBridgeDomain, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_vrf.aci_tenant.pk}&amp;'
            f"aci_vrf={self.aci_vrf.pk}",
        )

    def test_acivrf_contractrelations_tab_add_button(self) -> None:
        """VRF Contract Relations tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acivrf",
            "netbox_aci_plugin.view_acicontractrelation",
            "netbox_aci_plugin.add_acicontractrelation",
        )
        url = get_action_url(
            self.aci_vrf,
            action="contractrelations",
            kwargs={"pk": self.aci_vrf.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractRelation, action="add")
        content_type = ContentType.objects.get_for_model(ACIVRF)
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_vrf.aci_tenant.pk}&amp;'
            f"aci_object={self.aci_vrf.pk}&amp;"
            f"aci_object_type={content_type.pk}",
        )
