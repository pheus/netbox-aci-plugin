# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....choices import ContractRelationRoleChoices
from ....models.tenant.contracts import ACIContract, ACIContractRelation
from ....models.tenant.endpoint_groups import ACIEndpointGroup
from ....tables.tenant.contracts import (
    ACIContractRelationTable,
    ACIContractSubjectFilterTable,
    ACIContractSubjectTable,
    ACIContractTable,
)
from ...models.base import ACIBaseTestCase
from .. import base


class ACIContractTableTestCase(base.StandardTableTestCase):
    table = ACIContractTable


class ACIContractRelationTableRenderTestCase(ACIBaseTestCase):
    """Render-method coverage for ACIContractRelationTable."""

    def test_render_aci_object_for_endpoint_group(self) -> None:
        """Test render_aci_object formats an EPG with its app profile."""
        contract = ACIContract.objects.create(
            name="ACITableTestContract", aci_tenant=self.aci_tenant
        )
        epg = ACIEndpointGroup.objects.create(
            name="ACITableTestEPG",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        relation = ACIContractRelation.objects.create(
            aci_contract=contract,
            aci_object=epg,
            role=ContractRelationRoleChoices.ROLE_CONSUMER,
        )
        table = ACIContractRelationTable([])
        self.assertIn("|", table.render_aci_object(relation))


class ACIContractRelationTableTestCase(base.StandardTableTestCase):
    table = ACIContractRelationTable


class ACIContractSubjectTableTestCase(base.StandardTableTestCase):
    table = ACIContractSubjectTable


class ACIContractSubjectFilterTableTestCase(base.StandardTableTestCase):
    table = ACIContractSubjectFilterTable
