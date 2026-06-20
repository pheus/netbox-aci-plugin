# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning 2.0.0](https://semver.org/).

---

## [0.3.1] – 2026-06-21

> **Compatibility:** NetBox v4.5, NetBox v4.6

### Added

- Allow multi-select choice filters across Endpoint Group, VRF, Bridge Domain,
  Contract Filter Entry, Contract Relation, L3Out, and External Endpoint Group
  views, including QoS, protocol, port, role, policy-control, and Bridge Domain
  forwarding-mode fields.
- Filter ACI uSeg Network Attributes and ESG endpoint selectors by IP address,
  prefix, and MAC address.
- Enable pagination for GraphQL list queries.
- Document filtering GraphQL list queries by object ID lists, as provided by
  NetBox core.
- Include the ACI Tenant and VRF in External Endpoint Group search results.
- Add BGP-enabled and OSPF-enabled columns to the ACI L3Out table.
- Add a Tenant External navigation group for L3Out objects.
- Validate VRF consistency when an Endpoint Group's Bridge Domain is changed.

### Changed

- Compare foreign keys by ID in model validation to avoid extra database
  queries.
- Rename the L3Out Bridge Domain bindings tab URL from
  `bridge-domain-bindings` to `bridge-domains`.
- Clarify the `multipod_enabled` help text to state that it is a NetBox-side
  marker and is not pushed to APIC.
- Split Tenant documentation into feature-specific pages and add a GraphQL API
  filtering guide.
- Expand tests to maintain full coverage.

### Fixed

- Correct the search field on the ACI Bridge Domain Subnet filter.
- Disable ordering on foreign-key columns in object tables.
- Raise object-type validation errors at the form level for ACI Contract
  Relations, ESG selectors, and uSeg Network Attributes.
- Stop copying target object IDs when cloning ACI Contract Relations and uSeg
  Network Attributes.
- Require an attribute object on ACI uSeg Network Attributes unless the EPG
  subnet is used.

---

## [0.3.0] – 2026-05-31

> **Compatibility:** NetBox v4.5, NetBox v4.6

### Added

- Model ACI L3Outs, External Endpoint Groups, and External Subnets with full
  UI, REST API, GraphQL, and search support.
- Model ACI Routed Domains (external routed L3 domains).
- Add ACI Bridge Domain to L3Out bindings.
- Allow ACI External Endpoint Groups as Contract Relation targets.

### Changed

- Migrate the documentation toolchain to Zensical.

### Fixed

- Correct the AF12 and AF13 QoS DSCP value labels.
- Index `comments` on the remaining ACI search indexes.
- Group `description` with the identity fields in the filter forms.
- Remove the unused PIM IPv6 source and destination filter fields from the
  ACI Bridge Domain GraphQL filter.
- Apply interpolation after translation in validator error messages so the
  strings stay extractable.

---

## [0.2.2] – 2026-05-05

> **Compatibility:** NetBox v4.5, NetBox v4.6

### Added

- Add support for NetBox v4.6.

---

## [0.2.1] – 2026-03-22

> **Compatibility:** NetBox v4.5

### Added

- Allow Contract Relations to use Contracts from the `common` ACI Tenant.

### Changed

- Clarify Contract Relation documentation, including ESG and uSeg EPG support
  and the same-fabric / tenant-or-`common` requirements.
- Remove the uniqueness constraint on ACI Fabric IDs to support multi-fabric
  deployments.
- Add validation to ensure Contract Filters belong to the same ACI Tenant as the
  Contract Subject, or to the `common` Tenant in the same fabric.
- Refactor Contract Relation form initialization so Tenant and Fabric values are
  derived from the selected ACI object.
- Update GraphQL filter compatibility for newer `strawberry-graphql-django`
  APIs.
- Replace deprecated GraphQL filter decorators with the current API.
- Refactor tenant-or-common filtering into reusable FilterSet mixins.
- Update project linting, formatting, and dependency configuration.

### Fixed

- Remove a redundant validation check in Contract Filter protocol validation.
- Simplify Node uniqueness validation by moving logic into model clean methods.
- Initialize ESG and uSeg EPG cache attributes in Contract Relations.

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

[unreleased]: https://github.com/pheus/netbox-aci-plugin/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/pheus/netbox-aci-plugin/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/pheus/netbox-aci-plugin/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/pheus/netbox-aci-plugin/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/pheus/netbox-aci-plugin/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/pheus/netbox-aci-plugin/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/pheus/netbox-aci-plugin/releases/tag/v0.1.0
