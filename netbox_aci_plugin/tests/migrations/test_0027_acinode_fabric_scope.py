# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the 0027 ACI node fabric-scope staging migration."""

from importlib import import_module

from django.apps import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import SimpleTestCase, TransactionTestCase

from ..models.base import ACIBaseTestCase

# A numeric-prefixed module name is not a valid identifier, so it cannot be
# imported with a literal import statement
_migration_0027 = import_module(
    "netbox_aci_plugin.migrations.0027_acinode_fabric_scope_stage"
)
find_duplicate_node_ids = _migration_0027.find_duplicate_node_ids
format_duplicate_node_id_error = _migration_0027.format_duplicate_node_id_error
assert_unique_node_ids_per_fabric = _migration_0027.assert_unique_node_ids_per_fabric

APP_LABEL = "netbox_aci_plugin"
MIGRATE_FROM = "0026_fabric_cached_scope_set_null"
MIGRATE_TO = "0027_acinode_fabric_scope_stage"
ACINODE_TABLE = "netbox_aci_plugin_acinode"


class FindDuplicateNodeIdsTestCase(SimpleTestCase):
    """Pure-function tests for find_duplicate_node_ids()."""

    def test_find_duplicate_node_ids_across_pods_same_fabric(self) -> None:
        """Test a Node ID repeated across Pods of one Fabric is found."""
        rows = [(1, 101), (1, 102), (1, 101)]
        self.assertEqual(find_duplicate_node_ids(rows), [(1, 101)])

    def test_find_duplicate_node_ids_empty_on_clean_data(self) -> None:
        """Test clean, non-repeating rows yield an empty result."""
        rows = [(1, 101), (1, 102), (2, 101)]
        self.assertEqual(find_duplicate_node_ids(rows), [])

    def test_find_duplicate_node_ids_different_fabrics_not_duplicate(self) -> None:
        """Test the same Node ID in two different Fabrics is not duplicate."""
        rows = [(1, 101), (2, 101)]
        self.assertEqual(find_duplicate_node_ids(rows), [])

    def test_find_duplicate_node_ids_deterministic_ordering(self) -> None:
        """Test the returned duplicate pairs are sorted deterministically."""
        rows = [
            (3, 201),
            (3, 201),
            (1, 101),
            (1, 101),
            (2, 150),
            (2, 150),
        ]
        self.assertEqual(
            find_duplicate_node_ids(rows),
            [(1, 101), (2, 150), (3, 201)],
        )


class FormatDuplicateNodeIdErrorTestCase(SimpleTestCase):
    """Pure-function tests for format_duplicate_node_id_error()."""

    def test_format_duplicate_node_id_error_lists_every_pair(self) -> None:
        """Test the rendered message lists every conflicting pair."""
        message = format_duplicate_node_id_error([(1, 101), (2, 150)])
        self.assertIn("ACI Fabric 1 Node ID 101", message)
        self.assertIn("ACI Fabric 2 Node ID 150", message)


class AssertUniqueNodeIdsPerFabricTestCase(ACIBaseTestCase):
    """Wiring check for assert_unique_node_ids_per_fabric() on a live DB."""

    def test_assert_unique_node_ids_per_fabric_passes_on_clean_data(self) -> None:
        """Test the wrapper does not raise against the clean test database."""
        with connection.schema_editor(atomic=False) as schema_editor:
            assert_unique_node_ids_per_fabric(apps, schema_editor)


class ACINodeFabricScopeMigrationTestCase(TransactionTestCase):
    """Upgrade-path tests for the 0027 fabric-scope staging migration.

    Moves the plugin's migration state backward and forward with
    MigrationExecutor, so per-test setup through explicit calls (rather
    than setUpTestData) is unavoidable here: TransactionTestCase is the
    documented exception to the house rule.

    Teardown contract: every test registers its restore with
    addCleanup() before migrating backward, so it also fires when the
    test body raises. Django runs doCleanups() before
    TransactionTestCase's post-teardown flush, which is the only chance
    to put the schema back before the next test (in this run, and in
    the next --keepdb run) sees it. See _restore_to_leaf() for why the
    restore must delete the seeded fixture before migrating forward
    again, and why it must do so through the 0026 historical models.
    """

    def _get_historical_models(self, executor: MigrationExecutor) -> tuple:
        """Return the ACIFabric, ACIPod and ACINode classes frozen at 0026.

        Historical, not the current code's classes: at the 0026 schema
        ACINode has no `_aci_fabric` column yet, so the current ACINode
        class would fail on that missing column before any assertion
        under test is ever reached. project_state() is a pure function
        of the loaded migration graph, so it is safe to call again
        later for the cleanup, regardless of what has been migrated in
        between.
        """
        historical_apps = executor.loader.project_state(
            [(APP_LABEL, MIGRATE_FROM)]
        ).apps
        return (
            historical_apps.get_model(APP_LABEL, "ACIFabric"),
            historical_apps.get_model(APP_LABEL, "ACIPod"),
            historical_apps.get_model(APP_LABEL, "ACINode"),
        )

    def _seed_fabric_with_two_pods(
        self,
        executor: MigrationExecutor,
        fabric_name: str,
        node_id_a: int,
        node_id_b: int,
    ):
        """Create one historical Fabric with two Pods, one Node each.

        Returns the historical ACIFabric instance so callers can key
        assertions off its primary key, which is what the migration's
        error message actually names.
        """
        historical_fabric, historical_pod, historical_node = (
            self._get_historical_models(executor)
        )
        fabric = historical_fabric.objects.create(
            name=fabric_name, fabric_id=200, infra_vlan_vid=3901
        )
        pod_a = historical_pod.objects.create(
            name=f"{fabric_name}PodA", aci_fabric=fabric, pod_id=1
        )
        pod_b = historical_pod.objects.create(
            name=f"{fabric_name}PodB", aci_fabric=fabric, pod_id=2
        )
        historical_node.objects.create(
            name=f"{fabric_name}NodeA", aci_pod=pod_a, node_id=node_id_a
        )
        historical_node.objects.create(
            name=f"{fabric_name}NodeB", aci_pod=pod_b, node_id=node_id_b
        )
        return fabric

    def _restore_to_leaf(self, executor: MigrationExecutor, fabric_name: str) -> None:
        """Delete the seeded fixture, then migrate forward to the current leaf.

        Registered with addCleanup() before the backward migration in
        every test, so it also runs when the test body fails. Django
        runs doCleanups() before TransactionTestCase's post-teardown
        flush (verified against the installed Django source), so this
        is the only chance to restore the schema before that flush, and
        before any later test, touches it.

        Deletes through the 0026 historical models FIRST, before
        migrating anywhere. The expected 0027 failure rolls back only
        its own migration transaction. It does not undo the fixture
        rows this test committed directly with plain objects.create()
        calls before that migration ever ran. If this method instead
        migrated forward first, it would walk straight into the same
        duplicate rows, hit the same RuntimeError, and strand the
        database at 0026 exactly as this contract exists to prevent.
        The current-code ACINode class cannot stand in for this delete
        either: while the schema is still at 0026 (the duplicate-case
        test never gets past 0027's AddField), that class references
        `_aci_fabric`, a column that does not exist yet.

        Deletes are scoped to the Fabric name this test's own fixture
        used (a fresh, distinctive name per test, threaded through from
        addCleanup so it is fixed before the backward migration even
        though the fixture itself is only seeded afterward), not a
        blanket queryset over the whole table. The kept test database
        may still hold seed data here: netbox_aci_plugin ships a
        one-time data migration (0001/0011, gated behind
        create_default_aci_tenants/create_default_aci_fabric) that
        seeds a default ACIFabric plus three ACITenants the first time
        the database is built. Nothing re-runs an already-applied
        migration, so those rows are present on a freshly built
        database, until the first TransactionTestCase flush removes
        them for good. A blanket `.objects.all().delete()` on ACIFabric
        collides with that seed data through ACITenant.aci_fabric's
        PROTECT relation. Name-scoping avoids the collision entirely
        while still deleting the WHOLE fixture this test created, not
        one conflicting pk, so nothing is left behind if a test fails
        before seeding completes. Deletion order (Node, then Pod, then
        Fabric) still matters because both FKs are on_delete=PROTECT.

        The forward migration runs immediately after the deletes, ahead
        of every assertion below. Everything from here on is pure
        verification: if it ran interleaved with the restore and one of
        these assertions raised, that would abort the method before the
        forward migrate and leave the schema stranded, which is the
        exact outcome this whole method exists to prevent. A failure in
        the verification block below is reported as an ordinary test
        failure instead, with the schema already back at its leaf.
        """
        historical_fabric, historical_pod, historical_node = (
            self._get_historical_models(executor)
        )
        historical_node.objects.filter(aci_pod__aci_fabric__name=fabric_name).delete()
        historical_pod.objects.filter(aci_fabric__name=fabric_name).delete()
        historical_fabric.objects.filter(name=fabric_name).delete()

        # migrate() does not refresh loader.applied_migrations, so rebuild
        # the graph before resolving the leaf
        executor.loader.build_graph()
        leaf = executor.loader.graph.leaf_nodes(APP_LABEL)[0]
        executor.migrate([leaf])

        # Verification only from here on, the schema is restored. Scoped
        # by name, since the seeded default Fabric is expected to remain.
        self.assertFalse(
            historical_node.objects.filter(
                aci_pod__aci_fabric__name=fabric_name
            ).exists()
        )
        self.assertFalse(
            historical_pod.objects.filter(aci_fabric__name=fabric_name).exists()
        )
        self.assertFalse(historical_fabric.objects.filter(name=fabric_name).exists())

        # Confirm nothing is left pending: rebuild once more (the
        # migrate() call above made applied_migrations stale again) and
        # check that migrating to the same leaf is now a no-op.
        executor.loader.build_graph()
        self.assertEqual(executor.migration_plan([leaf]), [])

        with connection.cursor() as cursor:
            description = connection.introspection.get_table_description(
                cursor, ACINODE_TABLE
            )
        fabric_cache_column = next(
            column for column in description if column.name == "_aci_fabric_id"
        )
        self.assertFalse(fabric_cache_column.null_ok)

    def test_duplicate_node_id_across_pods_rejected(self) -> None:
        """Test 0027 rejects a Node ID duplicated across Pods of one Fabric."""
        executor = MigrationExecutor(connection)
        fabric_name = "Migration0027DupFabric"
        self.addCleanup(self._restore_to_leaf, executor, fabric_name)
        executor.migrate([(APP_LABEL, MIGRATE_FROM)])

        fabric = self._seed_fabric_with_two_pods(executor, fabric_name, 101, 101)

        executor.loader.build_graph()
        with self.assertRaises(RuntimeError) as cm:
            executor.migrate([(APP_LABEL, MIGRATE_TO)])
        self.assertIn(f"ACI Fabric {fabric.pk} Node ID 101", str(cm.exception))

    def test_clean_node_ids_pass_and_backfill(self) -> None:
        """Test 0027 backfills distinct Node IDs across Pods without error."""
        executor = MigrationExecutor(connection)
        fabric_name = "Migration0027CleanFabric"
        self.addCleanup(self._restore_to_leaf, executor, fabric_name)
        executor.migrate([(APP_LABEL, MIGRATE_FROM)])

        fabric = self._seed_fabric_with_two_pods(executor, fabric_name, 101, 102)

        executor.loader.build_graph()
        executor.migrate([(APP_LABEL, MIGRATE_TO)])

        migrated_apps = executor.loader.project_state([(APP_LABEL, MIGRATE_TO)]).apps
        migrated_node_model = migrated_apps.get_model(APP_LABEL, "ACINode")
        for node_id in (101, 102):
            with self.subTest(node_id=node_id):
                node = migrated_node_model.objects.get(node_id=node_id)
                self.assertEqual(node._aci_fabric_id, fabric.pk)  # noqa: SLF001
