# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for tenant Contract Filter models."""

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ..base import ACIModelViewTestCase


class ACIContractFilterViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIContractFilter."""

    model = ACIContractFilter

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilter view tests."""
        super().setUpTestData()

        # The migration-seeded contract filters (default / arp / est / icmp)
        # carry PROTECT'd filter-entry children, so NetBox's
        # bulk-delete-everything assertion (count() == 0) can never empty the
        # real table. Scoping the test queryset to only our own rows keeps
        # every inherited view test on deletable leaves.
        cls.fixture_pks = list(ACIContractFilter.objects.values_list("pk", flat=True))

        # 3 ACIContractFilter instances under the shared base tenant.
        cls.aci_filter = ACIContractFilter.objects.create(
            name="ACIViewTestContractFilter1", aci_tenant=cls.aci_tenant
        )
        ACIContractFilter.objects.create(
            name="ACIViewTestContractFilter2", aci_tenant=cls.aci_tenant
        )
        ACIContractFilter.objects.create(
            name="ACIViewTestContractFilter3", aci_tenant=cls.aci_tenant
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestContractFilterX",
            "name_alias": "ContractFilterXAlias",
            "description": "Form-data Contract Filter",
            "aci_tenant": cls.aci_tenant.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        cls.csv_data = (
            "name,aci_fabric,aci_tenant,description",
            f"ACIViewTestContractFilter4,{fabric},{tenant},CSV Filter 4",
            f"ACIViewTestContractFilter5,{fabric},{tenant},CSV Filter 5",
            f"ACIViewTestContractFilter6,{fabric},{tenant},CSV Filter 6",
        )

        filters = list(
            ACIContractFilter.objects.exclude(pk__in=cls.fixture_pks).order_by("pk")
        )
        cls.csv_update_data = (
            "id,description",
            f"{filters[0].pk},Updated Contract Filter 1",
            f"{filters[1].pk},Updated Contract Filter 2",
            f"{filters[2].pk},Updated Contract Filter 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Contract Filter"}

    def _get_queryset(self):
        return self.model.objects.exclude(pk__in=self.fixture_pks)

    def test_acicontractfilter_entries_tab(self) -> None:
        """Filter Entries tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acicontractfilter",
            "netbox_aci_plugin.view_acicontractfilterentry",
            "netbox_aci_plugin.add_acicontractfilterentry",
        )
        url = get_action_url(
            self.aci_filter,
            action="contractfilterentries",
            kwargs={"pk": self.aci_filter.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractFilterEntry, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_filter.aci_tenant_id}&amp;'
            f"aci_contract_filter={self.aci_filter.pk}",
        )


class ACIContractFilterEntryViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIContractFilterEntry."""

    model = ACIContractFilterEntry

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilterEntry view tests."""
        super().setUpTestData()

        cls.aci_filter = ACIContractFilter.objects.create(
            name="ACIViewTestEntryFilter", aci_tenant=cls.aci_tenant
        )

        ACIContractFilterEntry.objects.create(
            name="ACIViewTestEntry1", aci_contract_filter=cls.aci_filter
        )
        ACIContractFilterEntry.objects.create(
            name="ACIViewTestEntry2", aci_contract_filter=cls.aci_filter
        )
        ACIContractFilterEntry.objects.create(
            name="ACIViewTestEntry3", aci_contract_filter=cls.aci_filter
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # The model clean() requires every match criterion to read as
        # 'unspecified' unless its dependency is set, so the edit form needs
        # them spelled out (the bulk-import form defaults them instead).
        cls.form_data = {
            "name": "ACIViewTestEntryX",
            "name_alias": "EntryXAlias",
            "description": "Form-data Filter Entry",
            "aci_contract_filter": cls.aci_filter.pk,
            "ether_type": "unspecified",
            "arp_opc": "unspecified",
            "ip_protocol": "unspecified",
            "icmp_v4_type": "unspecified",
            "icmp_v6_type": "unspecified",
            "match_dscp": "unspecified",
            "source_from_port": "unspecified",
            "source_to_port": "unspecified",
            "destination_from_port": "unspecified",
            "destination_to_port": "unspecified",
            "tcp_rules": ["unspecified"],
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        flt = cls.aci_filter.name
        cls.csv_data = (
            "name,aci_fabric,aci_tenant,aci_contract_filter",
            f"ACIViewTestEntry4,{fabric},{tenant},{flt}",
            f"ACIViewTestEntry5,{fabric},{tenant},{flt}",
            f"ACIViewTestEntry6,{fabric},{tenant},{flt}",
        )

        entries = list(
            ACIContractFilterEntry.objects.filter(
                aci_contract_filter=cls.aci_filter
            ).order_by("pk")
        )
        cls.csv_update_data = (
            "id,description",
            f"{entries[0].pk},Updated Filter Entry 1",
            f"{entries[1].pk},Updated Filter Entry 2",
            f"{entries[2].pk},Updated Filter Entry 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Filter Entry"}
