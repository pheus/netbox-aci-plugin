from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0018_bridge_domain_l3out_binding"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="aciappprofile",
            options={
                "default_related_name": "aci_app_profiles",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acibridgedomain",
            options={
                "default_related_name": "aci_bridge_domains",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acibridgedomainl3outbinding",
            options={
                "default_related_name": "aci_bridge_domain_l3out_bindings",
                "ordering": ("aci_bridge_domain", "aci_l3out"),
            },
        ),
        migrations.AlterModelOptions(
            name="acibridgedomainsubnet",
            options={
                "default_related_name": "aci_bridge_domain_subnets",
                "ordering": ("aci_bridge_domain", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acicontract",
            options={
                "default_related_name": "aci_contracts",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acicontractfilter",
            options={
                "default_related_name": "aci_contract_filters",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acicontractfilterentry",
            options={
                "default_related_name": "aci_contract_filter_entries",
                "ordering": ("aci_contract_filter", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acicontractrelation",
            options={
                "default_related_name": "aci_contract_relations",
                "ordering": (
                    "aci_contract",
                    "_aci_endpoint_group",
                    "_aci_external_endpoint_group",
                    "_aci_vrf",
                    "role",
                ),
            },
        ),
        migrations.AlterModelOptions(
            name="acicontractsubject",
            options={
                "default_related_name": "aci_contract_subjects",
                "ordering": ("aci_contract", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acicontractsubjectfilter",
            options={
                "default_related_name": "aci_contract_subject_filters",
                "ordering": ("aci_contract_subject", "aci_contract_filter"),
            },
        ),
        migrations.AlterModelOptions(
            name="aciexternalendpointgroup",
            options={
                "default_related_name": "aci_external_endpoint_groups",
                "ordering": ("aci_l3out", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="aciexternalsubnet",
            options={
                "default_related_name": "aci_external_subnets",
                "ordering": ("aci_external_endpoint_group", "matched_prefix", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acifabric",
            options={"default_related_name": "aci_fabrics", "ordering": ("name",)},
        ),
        migrations.AlterModelOptions(
            name="acil3out",
            options={
                "default_related_name": "aci_l3outs",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acinode",
            options={
                "default_related_name": "aci_nodes",
                "ordering": ("aci_pod", "node_id"),
            },
        ),
        migrations.AlterModelOptions(
            name="acipod",
            options={
                "default_related_name": "aci_pods",
                "ordering": ("aci_fabric", "pod_id"),
            },
        ),
        migrations.AlterModelOptions(
            name="acirouteddomain",
            options={
                "default_related_name": "aci_routed_domains",
                "ordering": ("aci_fabric", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acitenant",
            options={
                "default_related_name": "aci_tenants",
                "ordering": ("aci_fabric", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="acivrf",
            options={
                "default_related_name": "aci_vrfs",
                "ordering": ("aci_tenant", "name"),
            },
        ),
    ]
