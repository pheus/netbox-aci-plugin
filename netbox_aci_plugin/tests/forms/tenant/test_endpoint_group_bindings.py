# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.backends.postgresql.psycopg_any import NumericRange

from ipam.models import VLAN, VLANGroup

from ....choices import (
    DeploymentImmediacyChoices,
    PortModeChoices,
    ResolutionImmediacyChoices,
)
from ....forms.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBindingBulkEditForm,
    ACIEndpointGroupAAEPBindingEditForm,
    ACIEndpointGroupAAEPBindingFilterForm,
    ACIEndpointGroupAAEPBindingImportForm,
    ACIEndpointGroupDomainBindingBulkEditForm,
    ACIEndpointGroupDomainBindingEditForm,
    ACIEndpointGroupDomainBindingFilterForm,
    ACIEndpointGroupDomainBindingImportForm,
)
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ....models.tenant.endpoint_group_bindings import ACIEndpointGroupDomainBinding
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

    def test_edit_form_rejects_blank_immediacy_values(self) -> None:
        """Test the edit form rejects blank immediacy values."""
        aci_epg_object_type = ContentType.objects.get_for_model(ACIEndpointGroup)
        aci_domain_object_type = ContentType.objects.get_for_model(ACIPhysicalDomain)
        form = ACIEndpointGroupDomainBindingEditForm(
            data={
                "aci_epg_object_type": aci_epg_object_type.pk,
                "aci_epg_object": self.aci_epg.pk,
                "aci_domain_object_type": aci_domain_object_type.pk,
                "aci_domain_object": self.aci_physical_domain.pk,
                "deployment_immediacy": "",
                "resolution_immediacy": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("deployment_immediacy", form.errors)
        self.assertIn("resolution_immediacy", form.errors)

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
                "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_LAZY,
                "resolution_immediacy": ResolutionImmediacyChoices.IMMEDIACY_LAZY,
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


class ACIEndpointGroupAAEPBindingFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACIEndpointGroupAAEPBinding forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACIEndpointGroupAAEPBinding tests."""
        super().setUpTestData()
        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIEPGAAEPBindingFormTestVLANPool",
            aci_fabric=cls.aci_fabric,
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=cls.aci_vlan_pool,
            vlan_id_from=100,
            vlan_id_to=299,
        )
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIEPGAAEPBindingFormTestPhysicalDomain",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIEPGAAEPBindingFormTestEPG",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg_domain_binding = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIEPGAAEPBindingFormTestAAEP",
            aci_fabric=cls.aci_fabric,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.nb_vlan = VLAN.objects.create(vid=150, name="ACIEPGAAEPBindingFormTestVLAN")
        cls.primary_nb_vlan = VLAN.objects.create(
            vid=151, name="ACIEPGAAEPBindingFormTestPrimaryVLAN"
        )

    def test_edit_form_valid_epg_aaep_binding(self) -> None:
        """Test a valid full submit binds the ACI Endpoint Group to an AAEP."""
        form = ACIEndpointGroupAAEPBindingEditForm(
            data={
                "aci_endpoint_group": self.aci_epg.pk,
                "aci_aaep": self.aci_aaep.pk,
                "nb_vlan": self.nb_vlan.pk,
                "mode": PortModeChoices.MODE_REGULAR,
                "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.aci_endpoint_group, self.aci_epg)
        self.assertEqual(form.instance.aci_aaep, self.aci_aaep)

    def test_edit_form_rejects_blank_mode_and_immediacy(self) -> None:
        """Test the edit form rejects blank mode and immediacy values."""
        form = ACIEndpointGroupAAEPBindingEditForm(
            data={
                "aci_endpoint_group": self.aci_epg.pk,
                "aci_aaep": self.aci_aaep.pk,
                "nb_vlan": self.nb_vlan.pk,
                "mode": "",
                "deployment_immediacy": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("mode", form.errors)
        self.assertIn("deployment_immediacy", form.errors)

    def test_edit_form_partial_submit_missing_encap_vlan_id(self) -> None:
        """Test a submit without any VLAN encapsulation fails validation."""
        form = ACIEndpointGroupAAEPBindingEditForm(
            data={
                "aci_endpoint_group": self.aci_epg.pk,
                "aci_aaep": self.aci_aaep.pk,
                "mode": PortModeChoices.MODE_REGULAR,
                "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("encap_vlan_id", form.errors)

    def test_edit_form_epg_choices_exclude_useg_epgs(self) -> None:
        """Test the EPG field offers regular EPGs but not uSeg EPGs."""
        useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACITestUSegEPGExcluded",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        form = ACIEndpointGroupAAEPBindingEditForm()
        queryset = form.fields["aci_endpoint_group"].queryset
        self.assertIn(self.aci_epg, queryset)
        self.assertNotIn(useg_epg, queryset)

    def test_bulk_edit_form_covers_mode_and_immediacy_fields_only(self) -> None:
        """Test the bulk edit form exposes only mode, immediacy, comments."""
        form = ACIEndpointGroupAAEPBindingBulkEditForm()
        self.assertIn("mode", form.fields)
        self.assertIn("deployment_immediacy", form.fields)
        self.assertIn("comments", form.fields)
        self.assertNotIn("nb_vlan", form.fields)
        self.assertNotIn("aci_endpoint_group", form.fields)
        self.assertNotIn("aci_aaep", form.fields)

    def test_import_form_resolves_epg_aaep_and_vlan_columns(self) -> None:
        """Test the import form resolves the EPG, AAEP and VLAN columns."""
        form = ACIEndpointGroupAAEPBindingImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_tenant": self.aci_tenant.name,
                "aci_app_profile": self.aci_app_profile.name,
                "aci_endpoint_group": self.aci_epg.name,
                "aci_aaep": self.aci_aaep.name,
                "nb_vlan": self.nb_vlan.vid,
                "primary_nb_vlan": self.primary_nb_vlan.vid,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["aci_endpoint_group"], self.aci_epg)

    def test_import_form_resolves_duplicate_vid_via_vlan_group(self) -> None:
        """Test import disambiguates a duplicated VID by the VLAN group."""
        group_a = VLANGroup.objects.create(
            name="ACIEPGAAEPBindingFormTestGroupA",
            slug="aci-epg-aaep-binding-form-test-group-a",
            vid_ranges=[NumericRange(100, 299)],
        )
        group_b = VLANGroup.objects.create(
            name="ACIEPGAAEPBindingFormTestGroupB",
            slug="aci-epg-aaep-binding-form-test-group-b",
            vid_ranges=[NumericRange(100, 299)],
        )
        VLAN.objects.create(vid=160, name="ACIEPGAAEPDupVIDGroupA", group=group_a)
        vlan_b = VLAN.objects.create(
            vid=160, name="ACIEPGAAEPDupVIDGroupB", group=group_b
        )

        form = ACIEndpointGroupAAEPBindingImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_tenant": self.aci_tenant.name,
                "aci_app_profile": self.aci_app_profile.name,
                "aci_endpoint_group": self.aci_epg.name,
                "aci_aaep": self.aci_aaep.name,
                "nb_vlan": 160,
                "nb_vlan_group": group_b.name,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["nb_vlan"], vlan_b)

    def test_import_form_clean_mode_defaults_to_regular(self) -> None:
        """Test the import form defaults an empty mode to 'regular'."""
        form = ACIEndpointGroupAAEPBindingImportForm(data={})
        form.is_valid()
        self.assertEqual(form.cleaned_data.get("mode"), PortModeChoices.MODE_REGULAR)

    def test_import_form_clean_mode_keeps_provided_value(self) -> None:
        """Test the import form keeps a provided mode value."""
        form = ACIEndpointGroupAAEPBindingImportForm(
            data={"mode": PortModeChoices.MODE_NATIVE}
        )
        form.is_valid()
        self.assertEqual(form.cleaned_data.get("mode"), PortModeChoices.MODE_NATIVE)

    def test_import_form_clean_deployment_immediacy_defaults_to_lazy(self) -> None:
        """Test the import form defaults an empty deployment_immediacy."""
        form = ACIEndpointGroupAAEPBindingImportForm(data={})
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("deployment_immediacy"),
            DeploymentImmediacyChoices.IMMEDIACY_LAZY,
        )

    def test_import_form_clean_deployment_immediacy_keeps_provided_value(
        self,
    ) -> None:
        """Test the import form keeps a provided deployment_immediacy."""
        form = ACIEndpointGroupAAEPBindingImportForm(
            data={
                "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            }
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("deployment_immediacy"),
            DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
        )

    def test_filter_form_deployment_immediacy_accepts_multiple(self) -> None:
        """Test the filter form accepts multiple immediacy values."""
        unbound = ACIEndpointGroupAAEPBindingFilterForm()
        field = unbound.fields["deployment_immediacy"]
        self.assertIsInstance(field, forms.MultipleChoiceField)
        values = [choice[0] for choice in field.choices if choice[0]][:2]
        form = ACIEndpointGroupAAEPBindingFilterForm(
            data={"deployment_immediacy": values}
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["deployment_immediacy"], values)
