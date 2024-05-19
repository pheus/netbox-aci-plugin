# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from utilities.choices import ChoiceSet

#
# VRF
#


class VRFPCEnforcementDirectionChoices(ChoiceSet):
    """Choice set of VRF policy control enforcement direction."""

    # default "ingress"
    DIR_INGRESS = "ingress"
    DIR_EGRESS = "egress"

    CHOICES = (
        (DIR_INGRESS, _("ingress"), "blue"),
        (DIR_EGRESS, _("egress"), "yellow"),
    )


class VRFPCEnforcementPreferenceChoices(ChoiceSet):
    """Choice set of VRF policy control enforcement preference."""

    # default "enforced"
    PREF_ENFORCED = "enforced"
    PREF_UNENFORCED = "unenforced"

    CHOICES = (
        (PREF_ENFORCED, _("enforced"), "green"),
        (PREF_UNENFORCED, _("unenforced"), "red"),
    )
