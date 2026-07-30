# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the ACI plugin validators."""

from django.test import SimpleTestCase

from ..validators import ParsedInterfaceName, parse_interface_name


class ParseInterfaceNameTestCase(SimpleTestCase):
    """Pure-function tests for parse_interface_name()."""

    def test_parse_interface_name_accepts_ethernet_names(self) -> None:
        """Test the accepted Ethernet spellings map to coordinates."""
        cases = {
            "Ethernet1/1": ParsedInterfaceName(module=1, port=1, sub_port=None),
            "eth1/1": ParsedInterfaceName(module=1, port=1, sub_port=None),
            "ETH1/1": ParsedInterfaceName(module=1, port=1, sub_port=None),
            "eth2/17": ParsedInterfaceName(module=2, port=17, sub_port=None),
            "Ethernet1/1/3": ParsedInterfaceName(module=1, port=1, sub_port=3),
            "eth255/127/64": ParsedInterfaceName(module=255, port=127, sub_port=64),
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(parse_interface_name(name), expected)

    def test_parse_interface_name_rejects_other_names(self) -> None:
        """Test a name outside the Ethernet port pattern returns None."""
        names = [
            "",
            "Gi1/1",
            "Ethernet1",
            "Ethernet1/",
            "Ethernet1/1/",
            "Ethernet1/1/1/1",
            "Ethernet1/1.100",
            " Ethernet1/1",
            "server-facing-a",
        ]
        for name in names:
            with self.subTest(name=name):
                self.assertIsNone(parse_interface_name(name))

    def test_parse_interface_name_absent_sub_port_stays_none(self) -> None:
        """Test a name without a breakout segment parses as None."""
        parsed = parse_interface_name("Ethernet1/17")
        self.assertIsNone(parsed.sub_port)

    def test_parse_interface_name_keeps_explicit_zero_sub_port(self) -> None:
        """Test an explicit zero breakout segment survives the parse."""
        parsed = parse_interface_name("Ethernet1/17/0")
        self.assertEqual(parsed.sub_port, 0)
