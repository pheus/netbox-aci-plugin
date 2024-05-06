# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

ACIPolicyNameValidator = RegexValidator(
    regex=r"^[a-zA-Z0-9_.:-]{1,64}$",
    message=_(
        "Only alphanumeric characters, hyphens, periods and underscores are\
        allowed."
    ),
    code="invalid",
)

ACIPolicyDescriptionValidator = RegexValidator(
    regex=r"^[a-zA-Z0-9\\!#$%()*,-./:;@ _{|}~?&+]{1,128}$",
    message=_(
        "Only alphanumeric characters and !#$%%()*,-./:;@ _{|}~?&+ are\
        allowed."
    ),
    code="invalid",
)
