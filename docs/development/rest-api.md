# REST API

The REST API is built on Django REST Framework via NetBox's
`NetBoxModelViewSet` + `NetBoxRouter`. Routes are registered in
`netbox_aci_plugin/api/urls.py`; viewsets in `api/views.py`;
serializers under `api/serializers/<domain>/<model>.py`.

## Router paths

Use kebab-case nouns. API routes stay **flat** even when the UI
nests relation/binding models under their parent (see [Views - URL
routing](views.md#url-routing)). REST consumers expect unambiguous
resource paths, so use flat compound names like
`bridge-domain-l3out-bindings`:

```python
# netbox_aci_plugin/api/urls.py
from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_aci_plugin"
router = NetBoxRouter()

# ACI Fabric
router.register("fabrics", views.ACIFabricListViewSet)
router.register("nodes", views.ACINodeListViewSet)
router.register("pods", views.ACIPodListViewSet)

# ACI Access Policies
router.register("routed-domains", views.ACIRoutedDomainListViewSet)

# ACI Tenant
router.register("tenants", views.ACITenantListViewSet)
router.register("app-profiles", views.ACIAppProfileListViewSet)
router.register("bridge-domains", views.ACIBridgeDomainListViewSet)
router.register(
    "bridge-domain-l3out-bindings",
    views.ACIBridgeDomainL3OutBindingListViewSet,
)
# ...

urlpatterns = router.urls
```

Group registrations by domain with `# ACI <Domain>` section comments,
matching the model-tree structure (Fabric, Access Policies, Tenant).

## ViewSet contract

Every viewset extends `NetBoxModelViewSet`. Class names end in
**`ListViewSet`** (not just `ViewSet`):

```python
class ACIBridgeDomainListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Bridge Domain instances."""

    queryset = ACIBridgeDomain.objects.select_related(
        "aci_tenant",
        "aci_tenant__aci_fabric",
        "aci_tenant__aci_fabric__nb_tenant",
        "aci_tenant__nb_tenant",
        "aci_vrf",
        "aci_vrf__aci_tenant",
        "aci_vrf__aci_tenant__aci_fabric",
        "aci_vrf__aci_tenant__aci_fabric__nb_tenant",
        "aci_vrf__aci_tenant__nb_tenant",
        "aci_vrf__nb_tenant",
        "aci_vrf__nb_vrf",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIBridgeDomainSerializer
    filterset_class = ACIBridgeDomainFilterSet
```

Three attributes are mandatory on every viewset:

1. **`queryset`**: explicit `select_related` + `prefetch_related("tags")`
   chain. Derive it from the **serializer**, not from the UI view. A
   nested serializer renders its `brief_fields`, which carry its own
   parent reference and `nb_tenant`, so the chain has to be walked to
   the end of that graph. Anything NetBox would otherwise resolve with
   a separate prefetch query belongs in `select_related`, and
   `tests/api/test_conventions.py` asserts exactly that. Generic
   foreign keys and tags cannot be joined and stay in
   `prefetch_related`.
2. **`serializer_class`**: the model's serializer.
3. **`filterset_class`**: the model's FilterSet, so `?field=value`
   query params work the same way the UI list-view filter sidebar
   does.

No custom `@action(...)` endpoints exist in the plugin yet.

## Serializers

Serializers live at `api/serializers/<domain>/<model>.py`. Every
serializer follows the same pattern; one shared example covers
most rules:

```python
from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin


class ACIBridgeDomainSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Bridge Domain model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acibridgedomain-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    aci_vrf = ACIVRFSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    mac_address = serializers.CharField(
        required=False, default=None, allow_blank=True, allow_null=True
    )
    virtual_mac_address = serializers.CharField(
        required=False, default=None, allow_blank=True, allow_null=True
    )

    class Meta:
        model = ACIBridgeDomain
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
            # ... domain-specific fields ...
            "owner",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
        )
```

### Inheritance

- **Primary models**: `class <Model>Serializer(OwnerMixin, NetBoxModelSerializer)`.
- **Relation / binding models**: `class <Model>Serializer(NetBoxModelSerializer)`,
  with no `OwnerMixin` (see [Models - OwnerMixin
  coverage](models.md#ownermixin-coverage)).

### `url` HyperlinkedIdentityField

Every serializer declares a `url` field as
`serializers.HyperlinkedIdentityField(view_name="...")` explicitly.
`view_name` follows the NetBox plugin API URL-name format:

```text
plugins-api:<app_label>-api:<modellower>-detail
```

For this plugin that's `plugins-api:netbox_aci_plugin-api:<modellower>-detail`.

### Nested related serializers

Related models are declared as nested serializers with `nested=True`.
Use the actual serializer class (not a `<Model>NestedSerializer`):

```python
aci_tenant = ACITenantSerializer(nested=True, required=True)
nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)
```

**Hard-FK rule:** every FK without `null=True` on the model **must**
have `required=True` on its nested serializer. Without it, the API
silently accepts payloads missing the FK and fails at the database
level.

`required=False, allow_null=True` is for optional FKs only (model has
`blank=True, null=True`), so JSON `null` and missing key both behave
correctly.

### Custom string fields

For non-FK string fields that are optional on the model (MAC,
IPv4/IPv6 strings, free-text identifiers), declare them explicitly
with the full optional-flag combo:

```python
mac_address = serializers.CharField(
    required=False,
    default=None,
    allow_blank=True,
    allow_null=True,
)
```

All four flags together (`required=False`, `default=None`,
`allow_blank=True`, `allow_null=True`) make JSON `null`, missing key,
and `""` all behave consistently with `blank=True` on the model.

### `Meta.fields` and `Meta.brief_fields`

Both tuples are declared, both annotated `: tuple`:

- `fields`: every field the full serializer renders. Order:
  identity (`id`, `url`, `display`, `name`, `name_alias`,
  `description`), then relations, then domain-specific, then `owner`,
  `comments`, `tags`, `custom_fields`, `created`, `last_updated`.
- `brief_fields`: what `?brief=1` returns and what nested
  representations include. Always contains `id`, `url`, `display`
  plus a small set of human-meaningful identity/scope fields.
  For primary models, `brief_fields` must include `"description"` in
  addition to `"id"`, `"url"`, `"display"`, `"name"`, and parent FK
  references. **Must match** the API test case's `brief_fields`
  attribute (see [Tests - API tests](tests.md#api-tests)).

For relation/binding serializers, `brief_fields` is often just the FK
references they relate:

```python
brief_fields = ("id", "url", "display", "aci_bridge_domain", "aci_l3out")
```

### Custom `validate()`

NetBox triggers the model's `full_clean()` inside
`ValidatedModelSerializer.validate()`. A serializer that overrides
`validate()` must therefore call `super().validate(attrs)` and return its
result. Skipping the super() call silently disables the model's `clean()`
and `clean_fields()` for every API write handled by that serializer.

Reserve serializer-level checks for rules the model cannot express. The
canonical example is `ACIExternalSubnetSerializer`: the model cannot tell a
user-supplied conflicting `matched_prefix` apart from a stale value that is
waiting to be re-synced from `nb_prefix`, so the serializer rejects the
explicit conflict and leaves the re-sync to the model. Everything else
belongs in the model's `clean()`.

## Serializer field kwarg ordering

Pass kwargs to `rest_framework` serializer fields in this order. Skip
any that aren't needed; don't reorder:

```text
read_only
write_only
required
default
initial
source
label
help_text
style
error_messages
validators
allow_blank
allow_null
```
