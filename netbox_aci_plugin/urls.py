# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import include, path
from utilities.urls import get_model_urls

from . import views  # noqa F401

urlpatterns: tuple = (
    # ACI Tenants
    path(
        "tenants/",
        include(get_model_urls("netbox_aci_plugin", "acitenant", detail=False)),
    ),
    path(
        "tenants/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acitenant")),
    ),
    # ACI Application Profiles
    path(
        "app-profiles/",
        include(get_model_urls("netbox_aci_plugin", "aciappprofile", detail=False)),
    ),
    path(
        "app-profiles/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciappprofile")),
    ),
    # ACI Endpoint Group
    path(
        "endpoint-groups/",
        include(get_model_urls("netbox_aci_plugin", "aciendpointgroup", detail=False)),
    ),
    path(
        "endpoint-groups/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciendpointgroup")),
    ),
    # ACI uSeg Endpoint Group
    path(
        "useg-endpoint-groups/",
        include(
            get_model_urls("netbox_aci_plugin", "aciusegendpointgroup", detail=False)
        ),
    ),
    path(
        "useg-endpoint-groups/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciusegendpointgroup")),
    ),
    # ACI uSeg Network Attribute
    path(
        "useg-endpoint-groups/network-attributes/",
        include(
            get_model_urls("netbox_aci_plugin", "aciusegnetworkattribute", detail=False)
        ),
    ),
    path(
        "useg-endpoint-groups/network-attributes/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciusegnetworkattribute")),
    ),
    # ACI Security Endpoint Group
    path(
        "endpoint-security-groups/",
        include(
            get_model_urls(
                "netbox_aci_plugin", "aciendpointsecuritygroup", detail=False
            )
        ),
    ),
    path(
        "endpoint-security-groups/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciendpointsecuritygroup")),
    ),
    # ACI ESG Endpoint Group Selector
    path(
        "endpoint-security-groups/epg-selectors/",
        include(
            get_model_urls(
                "netbox_aci_plugin",
                "aciesgendpointgroupselector",
                detail=False,
            )
        ),
    ),
    path(
        "endpoint-security-groups/epg-selectors/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciesgendpointgroupselector")),
    ),
    # ACI ESG Endpoint Selector
    path(
        "endpoint-security-groups/ep-selectors/",
        include(
            get_model_urls("netbox_aci_plugin", "aciesgendpointselector", detail=False)
        ),
    ),
    path(
        "endpoint-security-groups/ep-selectors/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciesgendpointselector")),
    ),
    # ACI Bridge Domain
    path(
        "bridge-domains/",
        include(get_model_urls("netbox_aci_plugin", "acibridgedomain", detail=False)),
    ),
    path(
        "bridge-domains/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acibridgedomain")),
    ),
    # ACI Bridge Domain Subnet
    path(
        "bridge-domain-subnets/",
        include(
            get_model_urls("netbox_aci_plugin", "acibridgedomainsubnet", detail=False)
        ),
    ),
    path(
        "bridge-domain-subnets/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acibridgedomainsubnet")),
    ),
    # ACI VRF
    path(
        "vrfs/",
        include(get_model_urls("netbox_aci_plugin", "acivrf", detail=False)),
    ),
    path(
        "vrfs/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acivrf")),
    ),
    # ACI Contract Filter
    path(
        "contract-filters/",
        include(get_model_urls("netbox_aci_plugin", "acicontractfilter", detail=False)),
    ),
    path(
        "contract-filters/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acicontractfilter")),
    ),
    # ACI Contract Filter Entry
    path(
        "contract-filter-entries/",
        include(
            get_model_urls("netbox_aci_plugin", "acicontractfilterentry", detail=False)
        ),
    ),
    path(
        "contract-filter-entries/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acicontractfilterentry")),
    ),
    # ACI Contract
    path(
        "contracts/",
        include(get_model_urls("netbox_aci_plugin", "acicontract", detail=False)),
    ),
    path(
        "contracts/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acicontract")),
    ),
    # ACI Contract Relation
    path(
        "contracts/relations/",
        include(
            get_model_urls("netbox_aci_plugin", "acicontractrelation", detail=False)
        ),
    ),
    path(
        "contracts/relations/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acicontractrelation")),
    ),
    # ACI Contract Subject
    path(
        "contract-subjects/",
        include(
            get_model_urls("netbox_aci_plugin", "acicontractsubject", detail=False)
        ),
    ),
    path(
        "contract-subjects/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acicontractsubject")),
    ),
    # ACI Contract Subject Filter
    path(
        "contract-subjects/filters/",
        include(
            get_model_urls(
                "netbox_aci_plugin", "acicontractsubjectfilter", detail=False
            )
        ),
    ),
    path(
        "contract-subjects/filters/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acicontractsubjectfilter")),
    ),
)
