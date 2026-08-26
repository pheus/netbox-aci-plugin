# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Search index tests for fabric node interface models."""

from django.contrib.contenttypes.models import ContentType

from extras.models import CachedValue
from netbox.search.backends import search_backend

from ....models.fabric.node_interfaces import ACINodeInterface
from ....search import ACINodeInterfaceIndex
from ...models.base import ACIBaseTestCase


class ACINodeInterfaceSearchIndexTestCase(ACIBaseTestCase):
    """Search index tests for ACINodeInterface free-text fields."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create a Node Interface carrying a description and comments."""
        super().setUpTestData()
        cls.description = "Uplink toward the spine layer"
        cls.comments = "Reserved for the ACISearchTest migration window."
        cls.aci_node_interface = ACINodeInterface.objects.create(
            aci_node=cls.aci_node,
            port=41,
            description=cls.description,
            comments=cls.comments,
        )

    def test_index_carries_the_primary_model_free_text_weights(self) -> None:
        """Test the index declares both free-text fields at house weights."""
        weights = dict(ACINodeInterfaceIndex.fields)
        self.assertEqual(weights["description"], 500)
        self.assertEqual(weights["comments"], 5000)

    def test_description_and_comments_are_cached(self) -> None:
        """Test both free-text fields reach the search cache."""
        search_backend.cache(self.aci_node_interface)
        content_type = ContentType.objects.get_for_model(ACINodeInterface)
        for field, value in (
            ("description", self.description),
            ("comments", self.comments),
        ):
            with self.subTest(field=field):
                self.assertTrue(
                    CachedValue.objects.filter(
                        object_type=content_type,
                        object_id=self.aci_node_interface.pk,
                        field=field,
                        value=value,
                    ).exists()
                )

    def test_search_finds_the_node_interface_by_description(self) -> None:
        """Test global search matches a Node Interface description.

        The gap this closes: display_attrs already listed description,
        so search showed a column it could not match on.
        """
        search_backend.cache(ACINodeInterface.objects.all())
        found = [result.object for result in search_backend.search("spine layer")]
        self.assertIn(self.aci_node_interface, found)
