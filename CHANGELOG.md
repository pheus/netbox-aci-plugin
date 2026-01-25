# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning 2.0.0](https://semver.org/).

---

## [0.2.0] – 2026-01-25

> **Compatibility:** NetBox v4.5

### Added

- Support multiple ACI Fabrics.
- Support ACI Pods.
- Support ACI Nodes.
- Record child-object changes (Bridge Domain Subnets, Contract Relations,
  Contract Filter Entries, and Contract Subjects) on the parent object.
- Add `ACITenantFilterSetMixin` and `NBTenantFilterSetMixin` to deduplicate
  filter logic.
- Add `ACIBaseTestCase` for consistent model test fixtures.
- Add ownership support.

### Changed

- **BREAKING:** Require NetBox **4.5+** (was 4.4).
- **BREAKING:** ACI Tenants now require a foreign key to an ACI Fabric.
- Use string-based ForeignKey references for plugin models.
- Use `select_related` for ForeignKey fields to reduce query count.
- Rely on `max_length` (and the database) for length enforcement by
  removing explicit `MaxLengthValidator`s and regex length quantifiers.
- Centralize max-length constants.
- Add `in_list` lookups for GraphQL enum fields.

### Removed

- Drop support for NetBox **4.3**–**4.4**.

### Fixed

- Make `ACITenant.parent_object` a property.
- Localize the `Attributes` and `NetBox Tenant` form fieldset labels
  with gettext.
- Fix navigation permissions for uSeg Endpoint Groups.
- Rename the GraphQL NetBox Tenant filter field from `tenant` to `nb_tenant`.

---

## [0.1.0] – 2025-09-03

> **Compatibility:** NetBox v4.3, NetBox v4.4

### Added

- First PyPI release of the NetBox ACI plugin.
- Models/UI for Tenants, Application Profiles, EPGs, uSeg EPGs, ESGs,
  Bridge Domains, VRFs, Contracts, Contract Subjects, and Contract Filters.

---

[unreleased]: https://github.com/pheus/netbox-aci-plugin/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/pheus/netbox-aci-plugin/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/pheus/netbox-aci-plugin/releases/tag/v0.1.0
