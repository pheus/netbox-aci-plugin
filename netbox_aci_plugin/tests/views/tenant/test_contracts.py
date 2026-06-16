# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for tenant Contract models."""

from django.contrib.contenttypes.models import ContentType

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.tenant.contract_filters import ACIContractFilter
from ....models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIModelViewTestCase


class ACIContractViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIContract."""

    model = ACIContract

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContract view tests."""
        super().setUpTestData()

        # 3 ACIContract instances under the shared base tenant.
        cls.aci_contract = ACIContract.objects.create(
            name="ACIViewTestContract1",
            aci_tenant=cls.aci_tenant,
            scope="context",
        )
        ACIContract.objects.create(
            name="ACIViewTestContract2",
            aci_tenant=cls.aci_tenant,
            scope="context",
        )
        ACIContract.objects.create(
            name="ACIViewTestContract3",
            aci_tenant=cls.aci_tenant,
            scope="context",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestContractX",
            "name_alias": "ContractXAlias",
            "description": "Form-data Contract",
            "aci_tenant": cls.aci_tenant.pk,
            "scope": "context",
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        cls.csv_data = (
            "name,aci_fabric,aci_tenant,scope",
            f"ACIViewTestContract4,{fabric},{tenant},context",
            f"ACIViewTestContract5,{fabric},{tenant},context",
            f"ACIViewTestContract6,{fabric},{tenant},context",
        )

        contracts = list(ACIContract.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{contracts[0].pk},Updated Contract 1",
            f"{contracts[1].pk},Updated Contract 2",
            f"{contracts[2].pk},Updated Contract 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Contract"}

    def test_acicontract_relations_tab(self) -> None:
        """Relations tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acicontract",
            "netbox_aci_plugin.view_acicontractrelation",
            "netbox_aci_plugin.add_acicontractrelation",
        )
        url = get_action_url(
            self.aci_contract,
            action="contractrelations",
            kwargs={"pk": self.aci_contract.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractRelation, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_contract.aci_tenant_id}&amp;'
            f"aci_contract={self.aci_contract.pk}",
        )

    def test_acicontract_subjects_tab(self) -> None:
        """Subjects tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acicontract",
            "netbox_aci_plugin.view_acicontractsubject",
            "netbox_aci_plugin.add_acicontractsubject",
        )
        url = get_action_url(
            self.aci_contract,
            action="contractsubjects",
            kwargs={"pk": self.aci_contract.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractSubject, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_contract.aci_tenant_id}&amp;'
            f"aci_contract={self.aci_contract.pk}",
        )


class ACIContractRelationViewTestCase(
    ACIModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """Standard view tests for ACIContractRelation.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    relation has no ``name`` field. The generic-FK target is an ACI VRF.
    """

    model = ACIContractRelation

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractRelation view tests."""
        super().setUpTestData()

        cls.aci_contract = ACIContract.objects.create(
            name="ACIViewTestRelContract",
            aci_tenant=cls.aci_tenant,
            scope="context",
        )
        # The relation's generic-FK target is an ACI VRF; each relation
        # needs a distinct (contract, object) pair to stay unique.
        vrfs = [
            ACIVRF.objects.create(
                name=f"ACIViewTestRelVRF{i}", aci_tenant=cls.aci_tenant
            )
            for i in range(1, 8)
        ]
        cls.vrf_ct = ContentType.objects.get_for_model(ACIVRF)

        ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract, aci_object=vrfs[0], role="prov"
        )
        ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract, aci_object=vrfs[1], role="prov"
        )
        ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract, aci_object=vrfs[2], role="prov"
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "aci_contract": cls.aci_contract.pk,
            "aci_object_type": cls.vrf_ct.pk,
            "aci_object": vrfs[3].pk,
            "role": "prov",
            "comments": "Form-data relation",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        contract = cls.aci_contract.name
        cls.csv_data = (
            ("aci_fabric,aci_tenant,aci_contract,aci_object_type,aci_object_id,role"),
            (
                f"{fabric},{tenant},{contract},netbox_aci_plugin.acivrf,"
                f"{vrfs[4].pk},prov"
            ),
            (
                f"{fabric},{tenant},{contract},netbox_aci_plugin.acivrf,"
                f"{vrfs[5].pk},prov"
            ),
            (
                f"{fabric},{tenant},{contract},netbox_aci_plugin.acivrf,"
                f"{vrfs[6].pk},prov"
            ),
        )

        relations = list(ACIContractRelation.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,comments",
            f"{relations[0].pk},Updated relation 1",
            f"{relations[1].pk},Updated relation 2",
            f"{relations[2].pk},Updated relation 3",
        )

        cls.bulk_edit_data = {"comments": "Bulk-edited relation"}


class ACIContractSubjectViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIContractSubject."""

    model = ACIContractSubject

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractSubject view tests."""
        super().setUpTestData()

        cls.aci_contract = ACIContract.objects.create(
            name="ACIViewTestSubjContract",
            aci_tenant=cls.aci_tenant,
            scope="context",
        )

        ACIContractSubject.objects.create(
            name="ACIViewTestSubject1", aci_contract=cls.aci_contract
        )
        ACIContractSubject.objects.create(
            name="ACIViewTestSubject2", aci_contract=cls.aci_contract
        )
        ACIContractSubject.objects.create(
            name="ACIViewTestSubject3", aci_contract=cls.aci_contract
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestSubjectX",
            "name_alias": "SubjectXAlias",
            "description": "Form-data Subject",
            "aci_contract": cls.aci_contract.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        contract = cls.aci_contract.name
        cls.csv_data = (
            "name,aci_fabric,aci_tenant,aci_contract",
            f"ACIViewTestSubject4,{fabric},{tenant},{contract}",
            f"ACIViewTestSubject5,{fabric},{tenant},{contract}",
            f"ACIViewTestSubject6,{fabric},{tenant},{contract}",
        )

        subjects = list(ACIContractSubject.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{subjects[0].pk},Updated Subject 1",
            f"{subjects[1].pk},Updated Subject 2",
            f"{subjects[2].pk},Updated Subject 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Subject"}


class ACIContractSubjectFilterViewTestCase(
    ACIModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """Standard view tests for ACIContractSubjectFilter.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    association has no ``name`` field.
    """

    model = ACIContractSubjectFilter

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractSubjectFilter view tests."""
        super().setUpTestData()

        cls.aci_contract = ACIContract.objects.create(
            name="ACIViewTestSFContract",
            aci_tenant=cls.aci_tenant,
            scope="context",
        )
        cls.aci_subject = ACIContractSubject.objects.create(
            name="ACIViewTestSFSubject", aci_contract=cls.aci_contract
        )
        # Each association needs a distinct contract filter to stay unique.
        filters = [
            ACIContractFilter.objects.create(
                name=f"ACIViewTestSFFilter{i}", aci_tenant=cls.aci_tenant
            )
            for i in range(1, 8)
        ]
        cls.filters = filters

        ACIContractSubjectFilter.objects.create(
            aci_contract_subject=cls.aci_subject,
            aci_contract_filter=filters[0],
            action="permit",
        )
        ACIContractSubjectFilter.objects.create(
            aci_contract_subject=cls.aci_subject,
            aci_contract_filter=filters[1],
            action="permit",
        )
        ACIContractSubjectFilter.objects.create(
            aci_contract_subject=cls.aci_subject,
            aci_contract_filter=filters[2],
            action="permit",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "aci_contract_subject": cls.aci_subject.pk,
            "aci_contract_filter": filters[3].pk,
            "action": "permit",
            "comments": "Form-data subject filter",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        contract = cls.aci_contract.name
        subject = cls.aci_subject.name
        cls.csv_data = (
            (
                "aci_fabric,aci_tenant,aci_contract,aci_contract_filter,"
                "aci_contract_subject,action"
            ),
            (f"{fabric},{tenant},{contract},{filters[4].name},{subject},permit"),
            (f"{fabric},{tenant},{contract},{filters[5].name},{subject},permit"),
            (f"{fabric},{tenant},{contract},{filters[6].name},{subject},permit"),
        )

        sfilters = list(ACIContractSubjectFilter.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,comments",
            f"{sfilters[0].pk},Updated subject filter 1",
            f"{sfilters[1].pk},Updated subject filter 2",
            f"{sfilters[2].pk},Updated subject filter 3",
        )

        cls.bulk_edit_data = {"comments": "Bulk-edited subject filter"}

    def test_acicontractsubject_filters_tab(self) -> None:
        """Subject Filters tab renders the registered Assign button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acicontractsubject",
            "netbox_aci_plugin.view_acicontractsubjectfilter",
            "netbox_aci_plugin.add_acicontractsubjectfilter",
        )
        url = get_action_url(
            self.aci_subject,
            action="contractsubjectfilters",
            kwargs={"pk": self.aci_subject.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContractSubjectFilter, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_contract_subject={self.aci_subject.pk}',
        )
