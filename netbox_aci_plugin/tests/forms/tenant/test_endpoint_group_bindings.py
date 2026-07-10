# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType

from ....choices import DeploymentImmediacyChoices, ResolutionImmediacyChoices
from ....forms.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBindingBulkEditForm,
    ACIEndpointGroupDomainBindingEditForm,
    ACIEndpointGroupDomainBindingFilterForm,
    ACIEndpointGroupDomainBindingImportForm,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ..base import ACIBaseFormTestCase


class ACIEndpointGroupDomainBindingFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACIEndpointGroupDomainBinding forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACIEndpointGroupDomainBinding tests."""
        super().setUpTestData()
        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIEPGDomainBindingFormTestVLANPool",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIEPGDomainBindingFormTestPhysicalDomain",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIEPGDomainBindingFormTestEPG",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIEPGDomainBindingFormTestUSegEPG",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )

    def test_edit_form_aci_epg_object_type_unknown(self) -> None:
        """Test the edit form tolerates an unknown ACI EPG object type."""
        form = ACIEndpointGroupDomainBindingEditForm(
            data={"aci_epg_object_type": 99999999}
        )
        self.assertTrue(form.fields["aci_epg_object"].disabled)
        self.assertEqual(form.fields["aci_epg_object"].queryset.count(), 0)

    def test_edit_form_aci_domain_object_type_unknown(self) -> None:
        """Test the edit form tolerates an unknown ACI domain object type."""
        form = ACIEndpointGroupDomainBindingEditForm(
            data={"aci_domain_object_type": 99999999}
        )
        self.assertTrue(form.fields["aci_domain_object"].disabled)
        self.assertEqual(form.fields["aci_domain_object"].queryset.count(), 0)

    def test_edit_form_endpoint_group_type_configures_field(self) -> None:
        """Test edit form configures aci_epg_object for the EPG type."""
        aci_epg_object_type = ContentType.objects.get_for_model(ACIEndpointGroup)
        form = ACIEndpointGroupDomainBindingEditForm(
            data={"aci_epg_object_type": aci_epg_object_type.pk}
        )
        self.assertEqual(form.fields["aci_epg_object"].queryset.model, ACIEndpointGroup)

    def test_edit_form_useg_endpoint_group_type_configures_field(self) -> None:
        """Test edit form configures aci_epg_object for the uSeg EPG type."""
        aci_epg_object_type = ContentType.objects.get_for_model(ACIUSegEndpointGroup)
        form = ACIEndpointGroupDomainBindingEditForm(
            data={"aci_epg_object_type": aci_epg_object_type.pk}
        )
        self.assertEqual(
            form.fields["aci_epg_object"].queryset.model, ACIUSegEndpointGroup
        )

    def test_edit_form_physical_domain_type_configures_field(self) -> None:
        """Test edit form configures aci_domain_object for physical domain."""
        aci_domain_object_type = ContentType.objects.get_for_model(ACIPhysicalDomain)
        form = ACIEndpointGroupDomainBindingEditForm(
            data={"aci_domain_object_type": aci_domain_object_type.pk}
        )
        self.assertEqual(
            form.fields["aci_domain_object"].queryset.model, ACIPhysicalDomain
        )

    def test_edit_form_partial_submit_missing_epg_object(self) -> None:
        """Test a partial submit without aci_epg_object fails validation."""
        aci_epg_object_type = ContentType.objects.get_for_model(ACIEndpointGroup)
        form = ACIEndpointGroupDomainBindingEditForm(
            data={"aci_epg_object_type": aci_epg_object_type.pk}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_epg_object", form.errors)

    def test_edit_form_partial_submit_missing_domain_object(self) -> None:
        """Test a partial submit without aci_domain_object fails validation."""
        aci_domain_object_type = ContentType.objects.get_for_model(ACIPhysicalDomain)
        form = ACIEndpointGroupDomainBindingEditForm(
            data={"aci_domain_object_type": aci_domain_object_type.pk}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_domain_object", form.errors)

    def test_edit_form_valid_epg_domain_binding(self) -> None:
        """Test a valid full submit binds an EPG to a physical domain."""
        aci_epg_object_type = ContentType.objects.get_for_model(ACIEndpointGroup)
        aci_domain_object_type = ContentType.objects.get_for_model(ACIPhysicalDomain)
        form = ACIEndpointGroupDomainBindingEditForm(
            data={
                "aci_epg_object_type": aci_epg_object_type.pk,
                "aci_epg_object": self.aci_epg.pk,
                "aci_domain_object_type": aci_domain_object_type.pk,
                "aci_domain_object": self.aci_physical_domain.pk,
                "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
                "resolution_immediacy": ResolutionImmediacyChoices.IMMEDIACY_IMMEDIATE,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.aci_epg_object, self.aci_epg)
        self.assertEqual(form.instance.aci_domain_object, self.aci_physical_domain)

    def test_edit_form_valid_useg_epg_domain_binding(self) -> None:
        """Test a valid full submit binds a uSeg EPG to a physical domain."""
        aci_epg_object_type = ContentType.objects.get_for_model(ACIUSegEndpointGroup)
        aci_domain_object_type = ContentType.objects.get_for_model(ACIPhysicalDomain)
        form = ACIEndpointGroupDomainBindingEditForm(
            data={
                "aci_epg_object_type": aci_epg_object_type.pk,
                "aci_epg_object": self.aci_useg_epg.pk,
                "aci_domain_object_type": aci_domain_object_type.pk,
                "aci_domain_object": self.aci_physical_domain.pk,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.aci_epg_object, self.aci_useg_epg)
        self.assertEqual(form.instance.aci_domain_object, self.aci_physical_domain)

    def test_bulk_edit_form_covers_immediacy_fields_only(self) -> None:
        """Test the bulk edit form exposes only immediacies and comments."""
        form = ACIEndpointGroupDomainBindingBulkEditForm()
        self.assertIn("deployment_immediacy", form.fields)
        self.assertIn("resolution_immediacy", form.fields)
        self.assertIn("comments", form.fields)
        self.assertNotIn("aci_epg_object_type", form.fields)
        self.assertNotIn("aci_domain_object_type", form.fields)

    def test_import_form_resolves_epg_and_domain_object_columns(self) -> None:
        """Test the import form resolves both GFK object/type CSV columns."""
        aci_epg_object_type = ContentType.objects.get_for_model(ACIEndpointGroup)
        aci_domain_object_type = ContentType.objects.get_for_model(ACIPhysicalDomain)
        form = ACIEndpointGroupDomainBindingImportForm(
            data={
                "aci_epg_object_type": (
                    f"{aci_epg_object_type.app_label}.{aci_epg_object_type.model}"
                ),
                "aci_epg_object_id": self.aci_epg.pk,
                "aci_domain_object_type": (
                    f"{aci_domain_object_type.app_label}.{aci_domain_object_type.model}"
                ),
                "aci_domain_object_id": self.aci_physical_domain.pk,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_import_form_clean_deployment_immediacy_defaults_to_lazy(self) -> None:
        """Test the import form defaults an empty deployment_immediacy."""
        form = ACIEndpointGroupDomainBindingImportForm(data={})
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("deployment_immediacy"),
            DeploymentImmediacyChoices.IMMEDIACY_LAZY,
        )

    def test_import_form_clean_resolution_immediacy_defaults_to_lazy(self) -> None:
        """Test the import form defaults an empty resolution_immediacy."""
        form = ACIEndpointGroupDomainBindingImportForm(data={})
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("resolution_immediacy"),
            ResolutionImmediacyChoices.IMMEDIACY_LAZY,
        )

    def test_import_form_clean_deployment_immediacy_keeps_provided_value(self) -> None:
        """Test the import form keeps a provided deployment_immediacy."""
        form = ACIEndpointGroupDomainBindingImportForm(
            data={
                "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            }
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("deployment_immediacy"),
            DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
        )

    def test_import_form_clean_resolution_immediacy_keeps_provided_value(self) -> None:
        """Test the import form keeps a provided resolution_immediacy."""
        form = ACIEndpointGroupDomainBindingImportForm(
            data={
                "resolution_immediacy": ResolutionImmediacyChoices.IMMEDIACY_IMMEDIATE,
            }
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("resolution_immediacy"),
            ResolutionImmediacyChoices.IMMEDIACY_IMMEDIATE,
        )

    def test_filter_form_deployment_immediacy_accepts_multiple(self) -> None:
        """Test the filter form accepts multiple immediacy values."""
        unbound = ACIEndpointGroupDomainBindingFilterForm()
        field = unbound.fields["deployment_immediacy"]
        self.assertIsInstance(field, forms.MultipleChoiceField)
        values = [choice[0] for choice in field.choices if choice[0]][:2]
        form = ACIEndpointGroupDomainBindingFilterForm(
            data={"deployment_immediacy": values}
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["deployment_immediacy"], values)
