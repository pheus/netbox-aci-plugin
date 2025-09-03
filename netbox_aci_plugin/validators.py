# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .choices import (
    ContractFilterIPProtocolChoices,
    ContractFilterPortChoices,
    ContractFilterTCPRulesChoices,
)

#
# ACI Policy Validators
#

ACIPolicyNameValidator = RegexValidator(
    regex=r"^[a-zA-Z0-9_.:-]{1,64}$",
    message=_(
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    ),
    code="invalid",
)

ACIPolicyDescriptionValidator = RegexValidator(
    regex=r"^[a-zA-Z0-9\\!#$%()*,-./:;@ _{|}~?&+]{1,128}$",
    message=_("Only alphanumeric characters and !#$%%()*,-./:;@ _{|}~?&+ are allowed."),
    code="invalid",
)


def validate_contract_filter_ip_protocol(value: str) -> None:
    """Validate the IP protocol value for ContractFilterEntry."""
    # Check if the protocol value is a valid choice in the ChoiceSet
    if value in dict(ContractFilterIPProtocolChoices):
        return

    if value in dict(ContractFilterIPProtocolChoices) or value in [
        str(i) for i in range(0, 256)
    ]:
        return

    # Check if the protocol value is a valid number between 0 and 255
    try:
        number = int(value)
        if 0 <= number <= 255:
            return
    except (ValueError, TypeError):
        pass

    # if neither condition is met, raise a ValidationError
    valid_choices = ", ".join(dict(ContractFilterIPProtocolChoices).keys())
    raise ValidationError(
        _(
            f"IP Protocol must be a number between 0 and 255 or"
            f" one of the following values: {valid_choices}"
        )
    )


def validate_contract_filter_port(value: str) -> None:
    """Validate the layer 4 port value for ContractFilterEntry."""
    # Check if the port value is a valid choice in the ChoiceSet
    if value in dict(ContractFilterPortChoices):
        return

    # Check if the port value is a valid number between 0 and 65,535
    try:
        number = int(value)
        if 0 <= number <= 65535:
            return
    except (ValueError, TypeError):
        pass

    # if neither condition is met, raise a ValidationError
    valid_choices = ", ".join(dict(ContractFilterPortChoices).keys())
    raise ValidationError(
        _(
            f"Layer 4 Port must be a number between 0 and 65535 or"
            f" one of the following values: {valid_choices}"
        )
    )


def validate_contract_filter_tcp_rules(value_list: list[str]) -> None:
    """Validate the TCP rule combinations for ContractFilterEntry."""
    if (
        ContractFilterTCPRulesChoices.TCP_ESTABLISHED in value_list
        and len(value_list) > 1
    ):
        raise ValidationError(_("TCP rules cannot be combined with 'established'."))
    if (
        ContractFilterTCPRulesChoices.TCP_UNSPECIFIED in value_list
        and len(value_list) > 1
    ):
        raise ValidationError(_("TCP rules cannot be combined with 'unspecified'."))
