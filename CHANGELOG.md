# Changelog

## 0.1.0 (unreleased)

* First release on PyPI.

---

## 0.0.11 (2025-02-10)

### Breaking Changes

* Requires NetBox version 4.2.0 or higher

### Enhancements

* Add Contract Relations views to ACI Endpoint Group and ACI VRF
* Refactor view registration leveraging the `get_model_urls` utility
  introduced in **NetBox v4.2**
* Refactors API serializers into separate modules for better organization
* Utilize `GetRelatedModelsMixin` for managing related models in
  `ACITenantView`
* Reorganizes the ACI menu into distinct groups for better clarity:
  Tenants, Application Profiles, Networking and Contracts.
* Extracts common fields and methods into a new `ACIBaseModel` to reduce
  duplicate code across ACI-related models
* Enhance GraphQL queries by adding support for related ACI objects

### Bug Fixes

* Rename the search index for ACI Contract Relation
* Fix `aci_object_id` field type supporting larger ID values

## 0.0.10 (2025-01-12)

### Breaking Changes

* Requires NetBox version 4.1.5 or higher

### Enhancements

* Add the ACI Contract Filter model, along with its forms and views
* Add the model, views and forms for the Entries in the ACI Contract Filter
* Move the Bridge Domain Subnet addition control to the Subnet table header
* Add the model, views and forms for ACI Contract Subject and its associated
  Filters within the ACI Contract Subject
* Add support for relations between ACI objects (Endpoint Groups, VRFs) and
  the ACI Contract via the ACIContractRelation model, views and forms
* Add NetBox v4.2 compatibility

### Bug Fixes

* Fix column headers of ACI Tenant and VRF fields for the Bridge Domain Subnet
  table

## 0.0.9 (2024-10-08)

### Breaking Changes

* Requires NetBox version 4.1.0 or higher

### Enhancements

* Add database migration for ACITenant
* Allow creation of default ACI Tenants (`common`, `infra`, `mgmt`) during
  migration
* Add database migrations for ACIVRF, ACIBridgeDomain, ACIBridgeDomainSubnet
* Add database migrations for ACIAppProfile, ACIEndpointGroup
* Provide a plugin configuration option to disable the creation of the default
  ACI Tenants
* Add support for GraphQL extended permissions in NetBox v4.0.10 and v4.0.11
* Add NetBox v4.1 compatibility

### Bug Fixes

* Fix OpenAPI schema generation warning for 'present_in_aci_tenant_or_common'
  filter
* Include `_id` suffix for filter `present_in_aci_tenant_or_common`

## 0.0.8 (2024-07-17)

### Enhancements

* Rename plugin's verbose name to "ACI" for simplicity and better user
  experience
* Allow referenced NetBox tenants to be deleted without raising a
  ProtectedError
* Enable cascade deletion of ACI Bridge Domain Subnets when the parent ACI
  Bridge Domain gets deleted
* Enhance tests for the models ACITenant, ACIVRF, ACIBridgeDomain,
  ACIBridgeDomainSubnet, ACIAppProfile, ACIEndpointGroup
* Ensure ACI Bridge Domain assigned ACI VRF belongs to the same ACI Tenant or
  to the special ACI Tenant 'common' on the model level
* Enforce ACI Endpoint Group assigned ACI Bridge Domain belongs to the same
  ACI Tenant or the special ACI Tenant 'common' on the model level

### Bug Fixes

* Remove NetBox tenant filtering in the ACI object forms

## 0.0.7 (2024-07-07)

### Enhancements

* Allow only one preferred (primary) gateway IP address per ACI Bridge Domain
* Enforce unique ACI Tenant name (following ACI policy model)
* Add ACI Tenant field to ACI Bridge Domain
* Remove ACI VRF requirement from ACI Endpoint Group import
* Allow ACI Bridge Domain assigning an ACI VRF from the same or from the
  special "common" ACI Tenant
* Allow ACI Bridge Domain from special "common" ACI Tenant to be assigned to
  the ACI Endpoint Group
* Add the ACI BD Subnets (Gateway IP addresses) column to the ACI Bridge Domain
  table in the list view

### Bug Fixes

* Add a preferred IP address and virtual IP address to ACI Bridge Domain Subnet
  template
* Fix unique ACI Bridge Domain Subnet name per ACI Bridge Domain
* Add type declaration to API serializer for MAC Address and Virtual MAC
  Address of ACI Bridge Domain
* Add blank choices to FilterForms of ACI Bridge Domain, ACI Endpoint Group and
  ACI VRF
* Fix multiple typos in comments, help texts and labels

## 0.0.6 (2024-06-21)

### Enhancements

* Add bulk edit and delete views
* Add import views
* Add import buttons to navigation
* Add `add` and `view` permission handling in UI
* Add related names for NetBox models

### Bug Fixes

* Fix PIM IPv4 source filter verbose name

## 0.0.5 (2024-06-07)

### Enhancements

* Add the ACI Endpoint Group model and views
* Prefill NetBox tenant while adding a new element through a ChildrenView

### Bug Fixes

* Fix typo in ACI Bridge Domain Subnet form for NetBox VRF
* Filter Bridge Domain choices based on ACI Tenant and/or ACI VRF in ACI Bridge
  Domain Subnet form
* Fix typo in ChildrenView registration
* Use the relevant model class for the tag filter

## 0.0.4 (2024-05-27)

### Enhancements

* Add an ACI Bridge Domain Subnet model and views
* Add ACI Bridge Domain tab to ACI Tenant
* Rename `alias` to `name_alias` following the ACI policy model
* Change related name of ACI VRF for ACI Bridge Domain to `aci_bridge_domains`

### Bug Fixes

* Fix form query parameters for NetBox tenants
* Add blank choices to boolean fields for filter forms
* Add the NetBox tenant field to the ACI Bridge Domain form

## 0.0.3 (2024-05-22)

### Enhancements

* Add the ACI Bridge Domain model and views
* Allow certain model fields to be cloned

## 0.0.2 (2024-05-19)

### Enhancements

* Add the ACI Application Profile model and views
* Add ACI VRF model and views
* Add ACI Application Profile tab view to ACITenant

### Bug Fixes

* Allow translation of table headers
* Add placeholders in templates (for empty fields)
* Change model's url paths to plural
* Add length validator to alias and description

## 0.0.1 (2024-05-09)

### Enhancements

* Add ACI Tenant model and views
* Support NetBox 4.0.0
