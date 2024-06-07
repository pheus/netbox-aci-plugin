# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from utilities.choices import ChoiceSet

#
# Bridge Domain
#


class BDMultiDestinationFloodingChoices(ChoiceSet):
    """Choice set of Bridge Domain multi destination flooding."""

    # default "bd-flood"
    FLOOD_BD = "bd-flood"
    FLOOD_ENCAP = "encap-flood"
    FLOOD_DROP = "drop"

    CHOICES = (
        (FLOOD_BD, _("bd-flood"), "blue"),
        (FLOOD_ENCAP, _("encap-flood"), "yellow"),
        (FLOOD_DROP, _("drop"), "red"),
    )


class BDUnknownMulticastChoices(ChoiceSet):
    """Choice set of Bridge Domain unknown multicast forwarding method."""

    # default "flood"
    UNKNOWN_MULTI_FLOOD = "flood"
    UNKNOWN_MULTI_OPT_FLOOD = "opt-flood"

    CHOICES = (
        (UNKNOWN_MULTI_FLOOD, _("flood"), "yellow"),
        (UNKNOWN_MULTI_OPT_FLOOD, _("opt-flood"), "blue"),
    )


class BDUnknownUnicastChoices(ChoiceSet):
    """Choice set of Bridge Domain unknown unicast forwarding method."""

    # default "proxy"
    UNKNOWN_UNI_PROXY = "proxy"
    UNKNOWN_UNI_FLOOD = "flood"

    CHOICES = (
        (UNKNOWN_UNI_PROXY, _("proxy"), "blue"),
        (UNKNOWN_UNI_FLOOD, _("flood"), "yellow"),
    )


#
# Endpoint Group
#


class EPGQualityOfServiceClassChoices(ChoiceSet):
    """Choice set of Endpoint Group QoS class."""

    # default "unspecified"
    CLASS_UNSPECIFIED = "unspecified"
    CLASS_LEVEL_1 = "level1"
    CLASS_LEVEL_2 = "level2"
    CLASS_LEVEL_3 = "level3"
    CLASS_LEVEL_4 = "level4"
    CLASS_LEVEL_5 = "level5"
    CLASS_LEVEL_6 = "level6"

    CHOICES = (
        (CLASS_UNSPECIFIED, _("unspecified"), "gray"),
        (CLASS_LEVEL_1, _("level 1"), "red"),
        (CLASS_LEVEL_2, _("level 2"), "orange"),
        (CLASS_LEVEL_3, _("level 3"), "yellow"),
        (CLASS_LEVEL_4, _("level 4"), "teal"),
        (CLASS_LEVEL_5, _("level 5"), "cyan"),
        (CLASS_LEVEL_6, _("level 6"), "blue"),
    )


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
