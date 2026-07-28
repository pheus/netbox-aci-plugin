# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, Interface, Site
from virtualization.models import Cluster, ClusterType, VirtualMachine

from ....choices import NodeRoleChoices
from ....forms.fabric.node_interfaces import (
    ACINodeInterfaceBulkEditForm,
    ACINodeInterfaceEditForm,
    ACINodeInterfaceFilterForm,
    ACINodeInterfaceImportForm,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ..base import ACIBaseFormTestCase


class ACINodeInterfaceFormTestCase(ACIBaseFormTestCase):
    """Test case for ACINodeInterface forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACINodeInterface tests."""
        super().setUpTestData()

        cls.device1 = Device.objects.create(
            name="ACINodeInterfaceFormTestDevice1",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site,
        )
        cls.device2 = Device.objects.create(
            name="ACINodeInterfaceFormTestDevice2",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site,
        )

        cls.aci_node = ACINode.objects.create(
            name="ACINodeInterfaceFormTestNode",
            aci_pod=cls.aci_pod,
            node_id=101,
            node_object=cls.device1,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node_no_device = ACINode.objects.create(
            name="ACINodeInterfaceFormTestNodeNoDevice",
            aci_pod=cls.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        cluster_type = ClusterType.objects.create(
            name="ACINodeInterfaceFormTestClusterType",
            slug="acinodeinterfaceformtestclustertype",
        )
        cluster = Cluster.objects.create(
            name="ACINodeInterfaceFormTestCluster", type=cluster_type
        )
        cls.virtual_machine = VirtualMachine.objects.create(
            name="ACINodeInterfaceFormTestVM", cluster=cluster
        )
        cls.aci_node_vm = ACINode.objects.create(
            name="ACINodeInterfaceFormTestNodeVM",
            aci_pod=cls.aci_pod,
            node_id=103,
            node_object=cls.virtual_machine,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        cls.iface_2_5 = Interface.objects.create(
            device=cls.device1,
            name="Ethernet2/5",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.iface_1_1_3 = Interface.objects.create(
            device=cls.device1,
            name="Ethernet1/1/3",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.iface_unparseable = Interface.objects.create(
            device=cls.device1,
            name="FooBar1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        # A second Pod in the same Fabric, carrying a Node with the same
        # name as cls.aci_node: ACINode names are unique per Pod only,
        # not per Fabric, so this exercises the scoped node resolution.
        # Node IDs are unique per Fabric, so this Node still needs a
        # distinct Node ID.
        cls.other_pod = ACIPod.objects.create(
            name="ACINodeInterfaceFormTestOtherPod",
            aci_fabric=cls.aci_fabric,
            pod_id=102,
        )
        cls.duplicate_named_node = ACINode.objects.create(
            name=cls.aci_node.name,
            aci_pod=cls.other_pod,
            node_id=104,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        # A separate Fabric and Pod, to prove the CSV narrowing actually
        # excludes objects scoped to a different Fabric.
        cls.other_fabric = ACIFabric.objects.create(
            name="ACINodeInterfaceFormTestOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_fabric_pod = ACIPod.objects.create(
            name="ACINodeInterfaceFormTestOtherFabricPod",
            aci_fabric=cls.other_fabric,
            pod_id=1,
        )

        # A second Site holding a Device sharing its name with one in
        # cls.site, each with an identically named interface. NetBox
        # device names are unique per Site, not globally, and
        # interface names are unique only within their Device, so this
        # is valid data the Node-scoped device and interface
        # resolution must handle.
        cls.other_site = Site.objects.create(
            name="ACINodeInterfaceFormTestOtherSite",
            slug="acinodeinterfaceformtestothersite",
        )
        cls.dup_device_a = Device.objects.create(
            name="ACINodeInterfaceFormTestDupDevice",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site,
        )
        cls.dup_device_b = Device.objects.create(
            name="ACINodeInterfaceFormTestDupDevice",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.other_site,
        )
        cls.dup_iface_a = Interface.objects.create(
            device=cls.dup_device_a,
            name="Ethernet1/1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.dup_iface_b = Interface.objects.create(
            device=cls.dup_device_b,
            name="Ethernet1/1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.aci_node_dup_device = ACINode.objects.create(
            name="ACINodeInterfaceFormTestNodeDupDevice",
            aci_pod=cls.aci_pod,
            node_id=105,
            node_object=cls.dup_device_a,
            role=NodeRoleChoices.ROLE_LEAF,
        )

    #
    # Coordinate prefill tests (blank coordinates derive from the
    # interface name, explicit values are preserved)
    #

    def test_prefill_module_and_port_blank_kept_sub_port_explicit(self) -> None:
        """Test blank module/port derive while an explicit sub port is kept."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_interface": self.iface_2_5,
                "module": "",
                "port": "",
                "sub_port": "7",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["module"], 2)
        self.assertEqual(form.cleaned_data["port"], 5)
        self.assertEqual(form.cleaned_data["sub_port"], 7)

    def test_prefill_all_coordinates_blank_defaults_sub_port_zero(self) -> None:
        """Test blank coordinates derive module and port, sub port zero."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_interface": self.iface_2_5,
                "module": "",
                "port": "",
                "sub_port": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["module"], 2)
        self.assertEqual(form.cleaned_data["port"], 5)
        self.assertEqual(form.cleaned_data["sub_port"], 0)

    def test_prefill_explicit_module_kept_port_and_sub_port_derive(self) -> None:
        """Test an explicit module is never replaced by the parsed value."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_interface": self.iface_2_5,
                "module": "1",
                "port": "",
                "sub_port": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["module"], 1)
        self.assertEqual(form.cleaned_data["port"], 5)
        self.assertEqual(form.cleaned_data["sub_port"], 0)

    def test_prefill_breakout_interface_all_blank(self) -> None:
        """Test a breakout interface name derives all three coordinates."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_interface": self.iface_1_1_3,
                "module": "",
                "port": "",
                "sub_port": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["module"], 1)
        self.assertEqual(form.cleaned_data["port"], 1)
        self.assertEqual(form.cleaned_data["sub_port"], 3)

    def test_prefill_no_interface_explicit_port_defaults_module_and_sub_port(
        self,
    ) -> None:
        """Test a manual interface still resolves module and sub port."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_interface": "",
                "module": "",
                "port": "7",
                "sub_port": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["module"], 1)
        self.assertEqual(form.cleaned_data["port"], 7)
        self.assertEqual(form.cleaned_data["sub_port"], 0)

    def test_prefill_unparseable_name_explicit_coordinates_accepted(self) -> None:
        """Test explicit coordinates are accepted for an unparseable name."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_interface": self.iface_unparseable,
                "module": "3",
                "port": "9",
                "sub_port": "1",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["module"], 3)
        self.assertEqual(form.cleaned_data["port"], 9)
        self.assertEqual(form.cleaned_data["sub_port"], 1)

    def test_prefill_unparseable_name_missing_port_errors(self) -> None:
        """Test an unparseable name with a blank port raises a clear error."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_interface": self.iface_unparseable,
                "module": "",
                "port": "",
                "sub_port": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("port", form.errors)

    def test_edit_after_interface_rename_leaves_coordinates_unchanged(self) -> None:
        """Test editing after an interface rename keeps the coordinates.

        Coordinates are authoritative once an object exists: resubmitting
        them unchanged must survive, never re-deriving from the renamed
        NetBox interface backing the object.
        """
        interface = Interface.objects.create(
            device=self.device1,
            name="Ethernet4/8",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node,
            nb_interface=interface,
            module=4,
            port=8,
            sub_port=0,
        )

        # Simulate a later, independent rename of the NetBox interface
        interface.name = "Ethernet9/9"
        interface.save()

        form = ACINodeInterfaceEditForm(
            instance=node_interface,
            data={
                "aci_node": self.aci_node,
                "nb_interface": interface,
                "module": 4,
                "port": 8,
                "sub_port": 0,
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertEqual(saved.module, 4)
        self.assertEqual(saved.port, 8)
        self.assertEqual(saved.sub_port, 0)
        self.assertEqual(saved.interface_token, "eth4/8")

    def test_edit_existing_object_blank_coordinates_rejected(self) -> None:
        """Test blank module, port and sub port are each rejected on edit."""
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=2, port=5, sub_port=0
        )
        form = ACINodeInterfaceEditForm(
            instance=node_interface,
            data={
                "aci_node": self.aci_node,
                "module": "",
                "port": "",
                "sub_port": "",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("module", form.errors)
        self.assertIn("port", form.errors)
        self.assertIn("sub_port", form.errors)

    def test_edit_form_unbound_displays_stored_coordinates(self) -> None:
        """Test an unbound edit form shows the stored coordinates."""
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=4, port=8, sub_port=2
        )
        form = ACINodeInterfaceEditForm(instance=node_interface)
        self.assertEqual(form.initial["module"], 4)
        self.assertEqual(form.initial["port"], 8)
        self.assertEqual(form.initial["sub_port"], 2)

    def test_add_form_unbound_renders_blank_module_and_sub_port(self) -> None:
        """Test an unbound add form shows no coordinate defaults.

        The add view builds its form with an unsaved instance, so
        model_to_dict() would otherwise seed the widgets with the
        model's own module and sub port defaults.
        """
        form = ACINodeInterfaceEditForm(instance=ACINodeInterface())

        self.assertIsNone(form["module"].value())
        self.assertIsNone(form["sub_port"].value())

    def test_add_form_rendered_values_still_derive_coordinates(self) -> None:
        """Test resubmitting the rendered add form derives the coordinates.

        A browser posts whatever the widget rendered, never a blank
        key, so the derive path must survive a round trip through the
        rendered values rather than only through an explicit blank.
        """
        rendered = ACINodeInterfaceEditForm(instance=ACINodeInterface())

        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_interface": self.iface_2_5,
                "module": rendered["module"].value() or "",
                "port": rendered["port"].value() or "",
                "sub_port": rendered["sub_port"].value() or "",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["module"], 2)
        self.assertEqual(form.cleaned_data["port"], 5)

    def test_add_form_no_initial_still_blanks_module_and_sub_port(self) -> None:
        """Test a plain add form still blanks the model's coordinate defaults.

        Guards the pre-existing behaviour the clone fix below must
        not regress.
        """
        form = ACINodeInterfaceEditForm(instance=ACINodeInterface())

        self.assertIsNone(form.initial["module"])
        self.assertIsNone(form.initial["sub_port"])

    def test_clone_initial_preserves_module_port_and_sub_port(self) -> None:
        """Test cloning an interface preserves its coordinates."""
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=4, port=17, sub_port=3
        )

        form = ACINodeInterfaceEditForm(
            instance=ACINodeInterface(), initial=node_interface.clone()
        )

        self.assertEqual(form.initial["module"], 4)
        self.assertEqual(form.initial["port"], 17)
        self.assertEqual(form.initial["sub_port"], 3)

    def test_clone_initial_with_string_values_preserves_coordinates(self) -> None:
        """Test string-valued clone initial, as a real request sends, is kept.

        clone() itself returns ints, but ObjectEditView.get() passes
        normalize_querydict(request.GET), which yields strings.
        """
        form = ACINodeInterfaceEditForm(
            instance=ACINodeInterface(),
            initial={"module": "4", "port": "17", "sub_port": "3"},
        )

        self.assertEqual(form.initial["module"], "4")
        self.assertEqual(form.initial["port"], "17")
        self.assertEqual(form.initial["sub_port"], "3")

    def test_clone_resubmit_unchanged_saves_original_coordinates(self) -> None:
        """Test resubmitting a cloned form unchanged saves the original spot.

        Mirrors ObjectEditView.get(): an unsaved instance plus the
        clone workflow's string-valued initial. Targets a different
        Node, as an actual clone to another switch would, so the
        assertions below isolate the coordinate bug rather than
        tripping the per-Node uniqueness constraint. A blanked module
        or sub port here would silently save the wrong coordinates.
        """
        original = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=4, port=17, sub_port=3
        )

        rendered = ACINodeInterfaceEditForm(
            instance=ACINodeInterface(),
            initial={
                "aci_node": str(self.aci_node.pk),
                "module": str(original.module),
                "port": str(original.port),
                "sub_port": str(original.sub_port),
            },
        )

        submitted = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.duplicate_named_node.pk,
                "module": rendered["module"].value() or "",
                "port": rendered["port"].value() or "",
                "sub_port": rendered["sub_port"].value() or "",
            }
        )

        self.assertTrue(submitted.is_valid(), submitted.errors)
        instance = submitted.save()
        self.assertEqual(instance.module, original.module)
        self.assertEqual(instance.port, original.port)
        self.assertEqual(instance.sub_port, original.sub_port)

    def test_add_form_seeds_nb_device_from_the_initial_aci_node(self) -> None:
        """Test the add form seeding nb_device from the parent Node.

        The child-add button passes the Node through as a query
        parameter, so the device must resolve from initial as well as
        from an edited instance.
        """
        form = ACINodeInterfaceEditForm(
            instance=ACINodeInterface(),
            initial={"aci_node": str(self.aci_node.pk)},
        )

        self.assertEqual(form.initial["nb_device"], self.device1)

    def test_add_form_malformed_aci_node_parameter_seeds_nothing(self) -> None:
        """Test a malformed Node query parameter seeding no nb_device."""
        form = ACINodeInterfaceEditForm(
            instance=ACINodeInterface(),
            initial={"aci_node": "not-a-pk"},
        )

        self.assertNotIn("nb_device", form.initial)

    def test_init_skips_nb_device_seed_when_node_has_no_device(self) -> None:
        """Test editing a device-less Node's interface seeds no nb_device."""
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node_no_device,
            module=1,
            port=1,
            sub_port=0,
        )

        form = ACINodeInterfaceEditForm(instance=node_interface)

        self.assertNotIn("nb_device", form.initial)

    #
    # nb_device consistency tests
    #

    def test_nb_device_mismatch_rejected(self) -> None:
        """Test a mismatched nb_device is rejected."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_device": self.device2,
                "module": "1",
                "port": "1",
                "sub_port": "0",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nb_device", form.errors)

    def test_nb_device_matching_accepted(self) -> None:
        """Test nb_device matching the ACI Node's device is accepted."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_device": self.device1,
                "module": "1",
                "port": "1",
                "sub_port": "0",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_nb_device_never_assigned_to_instance(self) -> None:
        """Test nb_device never becomes an attribute on the saved instance."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node,
                "nb_device": self.device1,
                "module": "1",
                "port": "1",
                "sub_port": "0",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertFalse(hasattr(instance, "nb_device"))

    def test_nb_interface_rejected_when_node_has_no_device(self) -> None:
        """Test an interface is rejected when the Node has no device."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node_no_device,
                "nb_interface": self.iface_2_5,
                "module": "",
                "port": "",
                "sub_port": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nb_interface", form.errors)

    def test_nb_interface_rejected_when_node_is_vm_backed(self) -> None:
        """Test selecting an interface is rejected for a VM-backed Node."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node_vm,
                "nb_interface": self.iface_2_5,
                "module": "",
                "port": "",
                "sub_port": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nb_interface", form.errors)

    def test_no_device_node_without_interface_is_valid(self) -> None:
        """Test a device-less Node without an interface submits cleanly."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": self.aci_node_no_device,
                "module": "1",
                "port": "1",
                "sub_port": "0",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_no_aci_node_skips_nb_device_consistency_check(self) -> None:
        """Test a blank ACI Node fails without a spurious nb_device error."""
        form = ACINodeInterfaceEditForm(
            data={
                "aci_node": "",
                "nb_interface": self.iface_2_5,
                "module": "1",
                "port": "1",
                "sub_port": "0",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_node", form.errors)
        self.assertNotIn("nb_device", form.errors)

    #
    # BulkEditForm / FilterForm sanity
    #

    def test_bulk_edit_form_nullable_fields_present(self) -> None:
        """Test the bulk edit form declares the nullable tail fields."""
        form = ACINodeInterfaceBulkEditForm(data={})
        self.assertIn("description", form.fields)
        self.assertIn("nb_tenant", form.fields)
        self.assertIn("owner", form.fields)
        self.assertIn("comments", form.fields)
        self.assertEqual(
            set(ACINodeInterfaceBulkEditForm.nullable_fields),
            {"description", "nb_tenant", "comments"},
        )

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACINodeInterfaceFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests (Node names scoped to Pod, not Fabric)
    #

    def test_import_form_valid_row_resolves_scoped_node(self) -> None:
        """Test the import form resolves the Node scoped by Fabric and Pod.

        A different Pod in the same Fabric carries a Node sharing the
        same name (cls.duplicate_named_node), so this also proves
        Node names resolve scoped to their Pod, not their Fabric
        alone: the row must resolve to cls.aci_node, not its
        same-named sibling.
        """
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "nb_device": self.device1.name,
                "nb_interface": self.iface_2_5.name,
                "module": "2",
                "port": "5",
                "sub_port": "0",
                "description": "Imported node interface",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_node, self.aci_node)
        self.assertEqual(instance.nb_interface, self.iface_2_5)

    def test_import_form_missing_coordinates_default_module_and_sub_port(
        self,
    ) -> None:
        """Test a row omitting module and sub port imports with 1 and 0."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "nb_device": self.device1.name,
                "nb_interface": self.iface_1_1_3.name,
                "port": "7",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.module, 1)
        self.assertEqual(instance.port, 7)
        self.assertEqual(instance.sub_port, 0)

    def test_import_form_blank_coordinates_default_module_and_sub_port(
        self,
    ) -> None:
        """Test a row with blank module and sub port columns defaults them."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "nb_device": self.device1.name,
                "nb_interface": self.iface_1_1_3.name,
                "module": "",
                "port": "7",
                "sub_port": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.module, 1)
        self.assertEqual(instance.port, 7)
        self.assertEqual(instance.sub_port, 0)

    def test_import_form_missing_port_errors(self) -> None:
        """Test a row omitting port still fails, keyed to port."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "nb_device": self.device1.name,
                "nb_interface": self.iface_1_1_3.name,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("port", form.errors)

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves every queryset unnarrowed."""
        form = ACINodeInterfaceImportForm(data=None)
        self.assertEqual(
            form.fields["aci_pod"].queryset.count(), ACIPod.objects.count()
        )
        self.assertEqual(
            form.fields["aci_node"].queryset.count(), ACINode.objects.count()
        )
        self.assertEqual(
            form.fields["nb_interface"].queryset.count(), Interface.objects.count()
        )

    def test_import_form_missing_pod_leaves_querysets_unnarrowed(self) -> None:
        """Test a row with only Fabric narrows the Pod but not the Node."""
        form = ACINodeInterfaceImportForm(data={"aci_fabric": self.aci_fabric.name})
        pod_queryset = form.fields["aci_pod"].queryset
        self.assertIn(self.aci_pod, pod_queryset)
        self.assertIn(self.other_pod, pod_queryset)
        self.assertNotIn(self.other_fabric_pod, pod_queryset)
        self.assertEqual(
            form.fields["aci_node"].queryset.count(), ACINode.objects.count()
        )
        self.assertEqual(
            form.fields["nb_interface"].queryset.count(), Interface.objects.count()
        )

    def test_import_form_missing_node_narrows_pod_only(self) -> None:
        """Test a row with Fabric and Pod but no Node narrows only the Pod."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
            }
        )
        pod_queryset = form.fields["aci_pod"].queryset
        self.assertIn(self.aci_pod, pod_queryset)
        self.assertIn(self.other_pod, pod_queryset)
        self.assertNotIn(self.other_fabric_pod, pod_queryset)
        self.assertEqual(
            form.fields["aci_node"].queryset.count(), ACINode.objects.count()
        )

    def test_import_form_ambiguous_node_name_leaves_device_querysets_unnarrowed(
        self,
    ) -> None:
        """Test an ambiguous Node name fails to resolve cleanly."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_node": self.aci_node.name,
                "nb_interface": self.iface_2_5.name,
                "port": "5",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_node", form.errors)
        self.assertEqual(
            form.fields["nb_device"].queryset.count(), Device.objects.count()
        )
        self.assertEqual(
            form.fields["nb_interface"].queryset.count(), Interface.objects.count()
        )

    #
    # Import form tests (Node-scoped device and interface resolution)
    #

    def test_import_form_duplicate_device_name_resolves_through_node(self) -> None:
        """Test a globally duplicated device name resolves via the Node."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node_dup_device.name,
                "nb_device": self.dup_device_a.name,
                "nb_interface": self.dup_iface_a.name,
                "port": "1",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.nb_interface, self.dup_iface_a)

    def test_import_form_duplicate_interface_name_resolves_through_node(self) -> None:
        """Test a globally duplicated interface name resolves via the Node."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node_dup_device.name,
                "nb_interface": self.dup_iface_a.name,
                "port": "1",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.nb_interface, self.dup_iface_a)

    def test_import_form_nb_interface_resolves_without_nb_device(self) -> None:
        """Test nb_interface resolves via the Node without nb_device."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "nb_interface": self.iface_2_5.name,
                "module": "2",
                "port": "5",
                "sub_port": "0",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.nb_interface, self.iface_2_5)

    def test_import_form_mismatched_nb_device_rejected(self) -> None:
        """Test an nb_device not matching the Node's device is rejected."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "nb_device": self.device2.name,
                "port": "1",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nb_device", form.errors)

    def test_import_form_device_less_node_with_nb_interface_rejected(self) -> None:
        """Test a device-less Node with nb_interface is rejected."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node_no_device.name,
                "nb_interface": self.iface_2_5.name,
                "port": "1",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nb_interface", form.errors)
        self.assertIn(
            "no assigned NetBox device",
            " ".join(str(error) for error in form.errors["nb_interface"]),
        )

    def test_import_form_vm_backed_node_with_nb_interface_rejected(self) -> None:
        """Test a VM-backed Node with nb_interface is rejected."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node_vm.name,
                "nb_interface": self.iface_2_5.name,
                "port": "1",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nb_interface", form.errors)

    def test_import_form_device_less_node_without_nb_interface_is_valid(self) -> None:
        """Test a device-less Node import without nb_interface succeeds."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node_no_device.name,
                "port": "1",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_import_form_nb_device_never_assigned_to_instance(self) -> None:
        """Test nb_device never becomes an attribute on the instance."""
        form = ACINodeInterfaceImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "nb_device": self.device1.name,
                "nb_interface": self.iface_2_5.name,
                "module": "2",
                "port": "5",
                "sub_port": "0",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertFalse(hasattr(instance, "nb_device"))

    #
    # Proof: CSV update defaults must not clobber stored coordinates
    #

    @staticmethod
    def _delete_unused_import_fields(form, record: dict) -> None:
        """Delete fields BulkImportView would delete for an update row.

        Mirrors bulk_views.py's own _process_import_records: for a row
        carrying an id, every field whose column is absent from the
        record is removed before validation, so no field is required
        to modify an existing object. The plugin's own tests construct
        the form directly rather than driving the view, so this must
        be replicated by hand to reproduce the real update contract.
        """
        for field_name in [name for name in form.fields if name not in record]:
            del form.fields[field_name]

    def test_import_form_update_omitting_coordinates_preserves_stored_values(
        self,
    ) -> None:
        """Test a CSV update row omitting coordinate columns preserves them."""
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node,
            module=4,
            port=8,
            sub_port=2,
        )
        record = {"description": "Updated via CSV"}
        form = ACINodeInterfaceImportForm(data=record, instance=node_interface)
        self._delete_unused_import_fields(form, record)

        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        instance.refresh_from_db()
        self.assertEqual(instance.module, 4)
        self.assertEqual(instance.port, 8)
        self.assertEqual(instance.sub_port, 2)
        self.assertEqual(instance.description, "Updated via CSV")

    def test_import_form_update_blank_coordinate_rejected(self) -> None:
        """Test a CSV update row with a blank coordinate cell is rejected."""
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node,
            module=4,
            port=8,
            sub_port=2,
        )
        record = {"module": ""}
        form = ACINodeInterfaceImportForm(data=record, instance=node_interface)
        self._delete_unused_import_fields(form, record)

        self.assertFalse(form.is_valid())
        self.assertIn("module", form.errors)

    def test_import_form_update_missing_node_resolves_interface_via_stored_node(
        self,
    ) -> None:
        """Test a sparse update row missing aci_node narrows nb_interface.

        The row supplies only nb_interface, an ambiguous name shared by
        the duplicate-name fixtures. Without falling back to the
        stored instance's aci_node, nb_interface resolves against the
        fully open queryset and fails as not unique.
        """
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node_dup_device,
            module=1,
            port=1,
            sub_port=0,
        )
        record = {"nb_interface": self.dup_iface_a.name}
        form = ACINodeInterfaceImportForm(data=record, instance=node_interface)
        self._delete_unused_import_fields(form, record)

        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.nb_interface, self.dup_iface_a)
