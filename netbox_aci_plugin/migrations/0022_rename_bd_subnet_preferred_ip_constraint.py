from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0021_access_policy_physical_domain"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="acibridgedomainsubnet",
            name="unique_aci_bd_subnet_preferred_ip_per_bridge_domain",
        ),
        migrations.AddConstraint(
            model_name="acibridgedomainsubnet",
            constraint=models.UniqueConstraint(
                condition=models.Q(preferred_ip_address_enabled=True),
                fields=("aci_bridge_domain",),
                name="netbox_aci_plugin_acibridgedomainsubnet_unique_preferred_ip_per_bridge_domain",
                violation_error_message="ACI Bridge Domain with a preferred (primary) gateway IP address already exists.",
            ),
        ),
    ]
