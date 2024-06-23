# Changelog

## 0.1.0 (unreleased)

* First release on PyPI.

---

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

* Add ACI Endpoint Group model and views
* Prefill NetBox tenant while adding a new element through a ChildrenView

### Bug Fixes

* Fix typo in ACI Bridge Domain Subnet form for NetBox VRF
* Filter Bridge Domain choices based on ACI Tenant and/or ACI VRF in ACI Bridge Domain Subnet form
* Fix typo in ChildrenView registration
* Use the relevant model class for the tag filter

## 0.0.4 (2024-05-27)

### Enhancements

* Add ACI Bridge Domain Subnet model and views
* Add ACI Bridge Domain tab to ACI Tenant
* Rename `alias` to `name_alias` following the ACI policy model
* Change related name of ACI VRF for ACI Bridge Domain to `aci_bridge_domains`

### Bug Fixes

* Fix form query parameters for NetBox tenants
* Add blank choices to boolean fields for filter forms
* Add NetBox tenant field to ACI Bridge Domain form

## 0.0.3 (2024-05-22)

### Enhancements

* Add ACI Bridge Domain model and views
* Allow certain model fields to be cloned

## 0.0.2 (2024-05-19)

### Enhancements

* Add ACI Application Profile model and views
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
