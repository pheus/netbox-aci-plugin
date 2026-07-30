# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from typing import NamedTuple

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .choices import (
    ContractFilterIPProtocolChoices,
    ContractFilterPortChoices,
    ContractFilterTCPRulesChoices,
)
from .constants import DESC_CHAR_CLASS, NAME_CHAR_CLASS

#
# ACI Policy Validators
#


# Required (1+)
ACIPolicyNameRequiredValidator = RegexValidator(
    regex=rf"^{NAME_CHAR_CLASS}+$",
    message=_(
        "Only alphanumeric characters, periods, underscores, colons and "
        "hyphens are allowed."
    ),
    code="invalid",
)

# Optional (0+): use on blank=True fields to align schema and clients
ACIPolicyNameOptionalValidator = RegexValidator(
    regex=rf"^{NAME_CHAR_CLASS}*$",
    message=_(
        "Only alphanumeric characters, periods, underscores, colons and "
        "hyphens are allowed."
    ),
    code="invalid",
)

ACIPolicyDescriptionValidator = RegexValidator(
    regex=rf"^{DESC_CHAR_CLASS}*$",
    message=_("Only alphanumeric characters and !#$%%()*,-./:;@ _{|}~?&+ are allowed."),
    code="invalid",
)


def validate_contract_filter_ip_protocol(value: str) -> None:
    """Validate the IP protocol value for ContractFilterEntry."""
    # Check if the protocol value is a valid choice in the ChoiceSet
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
            "IP Protocol must be a number between 0 and 255 or"
            " one of the following values: {valid_choices}"
        ).format(valid_choices=valid_choices)
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
            "Layer 4 Port must be a number between 0 and 65535 or"
            " one of the following values: {valid_choices}"
        ).format(valid_choices=valid_choices)
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


#
# Node Interface
#

# ACI node interface name: an Ethernet port with an optional breakout
# sub port ("Ethernet1/1", "eth1/1", "Ethernet1/1/1").
ACI_INTERFACE_NAME_REGEX = re.compile(
    r"^(?i:eth(?:ernet)?)(?P<module>\d+)/(?P<port>\d+)(?:/(?P<sub_port>\d+))?$"
)


class ParsedInterfaceName(NamedTuple):
    """Coordinates parsed from an ACI node interface name."""

    module: int
    port: int
    sub_port: int | None


def parse_interface_name(name: str) -> ParsedInterfaceName | None:
    """Parse an Ethernet interface name into node interface coordinates.

    Returns None when the name does not match the expected Ethernet
    port pattern. The sub port is None when the name carries no
    breakout segment, leaving any zero-sentinel substitution to the
    caller.
    """
    match = ACI_INTERFACE_NAME_REGEX.match(name)
    if not match:
        return None

    sub_port = match.group("sub_port")
    return ParsedInterfaceName(
        module=int(match.group("module")),
        port=int(match.group("port")),
        sub_port=int(sub_port) if sub_port is not None else None,
    )
