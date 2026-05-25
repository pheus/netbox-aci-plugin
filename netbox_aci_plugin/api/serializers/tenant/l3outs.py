# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Serializers for tenant L3Out models."""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ipam.api.field_serializers import IPNetworkField
from ipam.api.serializers import PrefixSerializer
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ..access_policies.domains import ACIRoutedDomainSerializer
from .tenants import ACITenantSerializer
from .vrfs import ACIVRFSerializer


class ACIL3OutSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for ACIL3Out model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acil3out-detail",
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    aci_vrf = ACIVRFSerializer(nested=True, required=True)
    aci_routed_domain = ACIRoutedDomainSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIL3Out
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "aci_routed_domain",
            "target_dscp",
            "import_route_control_enforcement_enabled",
            "export_route_control_enforcement_enabled",
            "bgp_enabled",
            "ospf_enabled",
            "eigrp_enabled",
            "l3_multicast_ipv4_enabled",
            "l3_multicast_ipv6_enabled",
            "multipod_enabled",
            "custom_qos_policy_name",
            "bfd_policy_name",
            "pim_policy_name",
            "igmp_interface_policy_name",
            "ospf_external_policy_name",
            "eigrp_interface_policy_name",
            "interleak_route_map_name",
            "ingress_data_plane_policing_policy_name",
            "egress_data_plane_policing_policy_name",
            "nb_tenant",
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
            "description",
            "aci_tenant",
            "aci_vrf",
        )
        read_only_fields: tuple = ("export_route_control_enforcement_enabled",)


class ACIExternalEndpointGroupSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for ACIExternalEndpointGroup model."""

    url = serializers.HyperlinkedIdentityField(
        view_name=("plugins-api:netbox_aci_plugin-api:aciexternalendpointgroup-detail"),
    )
    aci_l3out = ACIL3OutSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIExternalEndpointGroup
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_l3out",
            "preferred_group_member_enabled",
            "qos_class",
            "target_dscp",
            "nb_tenant",
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
            "description",
            "aci_l3out",
        )


class ACIExternalSubnetSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for ACIExternalSubnet model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciexternalsubnet-detail",
    )
    aci_external_endpoint_group = ACIExternalEndpointGroupSerializer(
        nested=True, required=True
    )
    matched_prefix = IPNetworkField(required=False, allow_null=True)
    nb_prefix = PrefixSerializer(nested=True, required=False, allow_null=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIExternalSubnet
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_external_endpoint_group",
            "matched_prefix",
            "nb_prefix",
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_route_control_enabled",
            "import_security_enabled",
            "shared_security_enabled",
            "aggregate_import_route_control_enabled",
            "aggregate_export_route_control_enabled",
            "aggregate_shared_route_control_enabled",
            "bgp_route_summarization_enabled",
            "bgp_route_summarization_policy_name",
            "ospf_route_summarization_enabled",
            "ospf_route_summarization_policy_name",
            "eigrp_route_summarization_enabled",
            "nb_tenant",
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
            "description",
            "aci_external_endpoint_group",
            "matched_prefix",
        )

    def validate(self, attrs):
        """Validate matched prefix consistency with selected NetBox Prefix."""
        nb_prefix = attrs.get("nb_prefix", getattr(self.instance, "nb_prefix", None))
        matched_prefix = attrs.get(
            "matched_prefix",
            getattr(self.instance, "matched_prefix", None),
        )

        # Only reject when supplied matched_prefix conflicts with nb_prefix.
        # If matched_prefix is absent, the model's sync handles it.
        if (
            "matched_prefix" in attrs
            and nb_prefix
            and matched_prefix
            and matched_prefix != nb_prefix.prefix
        ):
            raise serializers.ValidationError(
                {"matched_prefix": _("Must match the selected NetBox Prefix.")}
            )

        if not nb_prefix and not matched_prefix:
            raise serializers.ValidationError(
                {
                    "matched_prefix": _(
                        "A matched prefix is required when no NetBox"
                        " Prefix is selected."
                    )
                }
            )

        return attrs
