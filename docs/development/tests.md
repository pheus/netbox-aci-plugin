# Tests

Tests live under `netbox_aci_plugin/tests/`, organized by layer:

```text
tests/
  models/      base.py + <domain>/test_<model>.py
  forms/       base.py + <domain>/test_<model>.py
  views/       base.py + <domain>/test_<model>.py
  filtersets/  <domain>/test_<model>.py
  tables/      base.py + <domain>/test_<model>.py
  api/         <domain>/test_<model>.py
  graphql/     base.py + test_<topic>.py
  search/      <domain>/test_<model>.py
```

Run the suite with NetBox's Django test runner (the plugin must be
installed editable into NetBox's virtualenv first):

```bash
cd "$NETBOX_ROOT/netbox"
python manage.py test netbox_aci_plugin --keepdb
```

Drop `--keepdb` when model fields, migrations, or schema changed. See
the [contributing guide](contributing.md) for the full setup. This doc
covers conventions for **writing** tests, not running them.

## `setUpTestData`, not `setUp`

Shared fixtures use `setUpTestData()` (a classmethod) so they're
created **once per class** rather than once per test method. Reserve
`setUp()` for per-test state (e.g. logging in a client):

```python
@classmethod
def setUpTestData(cls):
    cls.aci_fabric = ACIFabric.objects.create(
        name="TestFabric", fabric_id=101, infra_vlan_vid=3900,
    )
```

## Per-layer base classes

Four base classes hold the shared fixtures and helpers for their layer.
Each test module subclasses the layer's base.

### `tests/models/base.py:ACIBaseTestCase`

Builds the full ACI hierarchy through `ACIAppProfile` (Fabric, Pod,
Node, Tenant, VRF, BD, AppProfile), ACI VLAN pools and ranges, plus
the universal NetBox objects (Tenant, Site, Manufacturer, DeviceType,
DeviceRole, VRF, IPAddress, MACAddress, Prefix, among others). Use it
for model and manager tests.

### `tests/forms/base.py:ACIBaseFormTestCase`

Same hierarchy as the model base, plus two class attributes carrying
the exact validator error strings, so form tests can assert against
them without duplicating literals:

```python
class ACIBaseFormTestCase(TestCase):
    name_error_message: str = (
        "Only alphanumeric characters, periods, underscores, colons and "
        "hyphens are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )
```

### `tests/views/base.py:ACIModelViewTestCase`

Extends NetBox's `ModelViewTestCase` - authentication is inherited
with no user creation, `setUp`, or `force_login` needed. It overrides
`_get_base_url()` to prefix the `plugins:` namespace required by
plugin views, then seeds a NetBox `nb_tenant` plus the shared ACI
Fabric / Tenant / VRF / BD / AppProfile chain in `setUpTestData`:

```python
class ACIModelViewTestCase(ModelViewTestCase):
    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(
            self.model._meta.app_label,
            self.model._meta.model_name,
        )

    @classmethod
    def setUpTestData(cls) -> None:
        cls.nb_tenant = Tenant.objects.create(
            name="ACIBaseViewTestNBTenant", slug="acibaseviewtestnbtenant",
        )
        cls.aci_fabric = ACIFabric.objects.create(
            name="ACIBaseViewTestFabric", fabric_id=150, infra_vlan_vid=3900,
        )
        cls.aci_tenant = ACITenant.objects.create(
            name="ACIBaseViewTestTenant", aci_fabric=cls.aci_fabric,
        )
        cls.aci_vrf = ACIVRF.objects.create(
            name="ACIBaseViewTestVRF", aci_tenant=cls.aci_tenant,
        )
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name="ACIBaseViewTestBD",
            aci_tenant=cls.aci_tenant, aci_vrf=cls.aci_vrf,
        )
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name="ACIBaseViewTestAppProfile", aci_tenant=cls.aci_tenant,
        )
```

### `tests/graphql/base.py:ACIBaseGraphQLTestCase`

Extends `APITestCase` (with `LOGIN_REQUIRED=True`) and seeds shared
Fabric / Tenant / VRF objects. Provides a `query()` helper that POSTs
to the GraphQL endpoint and asserts HTTP 200:

```python
def query(self, query_str: str) -> dict:
    """POST a GraphQL query and return the parsed JSON body."""
    response = self.client.post(
        reverse("graphql"),
        data={"query": query_str},
        format="json",
        **self.header,
    )
    self.assertEqual(response.status_code, 200, response.content)
    return response.json()
```

`tests/tables/base.py` aliases `TableTestCases.StandardTableTestCase`
for use as a smoke-test base.

## Module docstrings

API and table test modules carry a short top-level docstring naming
the domain and layer, e.g. `"""API tests for access-policy VLAN pool
models."""` or `"""Table tests for tenant L3Out models."""`. Model
and form test modules omit one.

## Model-test method names

Use this naming pattern so test output stays scannable across the
plugin:

Use these method names:

- `test_<model>_instance`: object created with the expected type.
- `test_<model>_str`: `__str__()` returns the expected representation.
- `test_<model>_<field>`: field value is what was assigned.
- `test_<model>_<related>_instance`: FK / reverse-FK target is the right
  type.
- `test_invalid_<model>_<field>`: invalid value raises
  `ValidationError`.
- `test_invalid_<model>_<field>_length`: length-constraint violation
  raises `ValidationError`.

Example slice from `test_app_profiles.py`:

```python
def test_aci_app_profile_instance(self) -> None: ...
def test_aci_app_profile_str(self) -> None: ...
def test_aci_app_profile_alias(self) -> None: ...
def test_aci_app_profile_description(self) -> None: ...
def test_aci_app_profile_aci_tenant_instance(self) -> None: ...
def test_invalid_aci_app_profile_name(self) -> None: ...
def test_invalid_aci_app_profile_name_length(self) -> None: ...
```

## Form-test assertions

Form tests instantiate the form, then assert on `form.errors`:

- Valid data: `self.assertEqual(form.errors.get("<field>"), None)`.
- Invalid data: assert the error message matches the class-level
  `name_error_message` / `description_error_message` constants. Don't
  duplicate the error string literal in each test.

## FilterSet tests

Every FilterSet test class declares `queryset` and `filterset` class
attributes, then exercises one method per filter plus two
search-related methods that everyone must include:

- `test_q()`: search-term hits expected objects.
- `test_search_with_whitespace_only_returns_all()`: guards the
  whitespace-only no-op branch of `search()` (see
  [FilterSets - search()](filtersets.md#search)).

Assertion pattern:

```python
self.assertIn(obj, self.filterset(params, self.queryset).qs)
```

## API tests

API tests use NetBox's `utilities.testing.APIViewTestCases` mixin
suite, which delivers get/list/create/update/delete coverage for free.
Each `<Model>APIViewTestCase` declares:

Required attributes:

- `model`: concrete model class under test.
- `view_namespace`: `f"plugins-api:{app_name}"`.
- `brief_fields`: fields expected in the `?brief=1` response. This must
  match the serializer's `Meta.brief_fields`.
- `user_permissions`: extra permissions beyond the auto-granted model
  permissions.

`setUpTestData()` uses `bulk_create()` for fixtures. Two class-level
dicts drive the create/update assertions:

- `cls.create_data`: list of payloads for `POST /<resource>/`.
- `cls.bulk_update_data`: payload for `PATCH /<resource>/` (the
  fields you're updating, not the IDs).

```python
class ACIAppProfileAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    model = ACIAppProfile
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant", "description", "display", "id", "name",
        "name_alias", "nb_tenant", "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acitenant",)
```

!!! tip "NetBox test mixins"
    Prefer NetBox's testing mixins whenever they fit: use
    `utilities.testing.ViewTestCases.*` for UI view permission checks,
    `ChangeLoggedFilterSetTests` / `BaseFilterSetTests` for filtersets,
    and `TableTestCases.StandardTableTestCase` for table smoke tests.
    The plugin already uses these patterns in several layers; new tests
    should extend that coverage rather than adding hand-rolled helpers.
