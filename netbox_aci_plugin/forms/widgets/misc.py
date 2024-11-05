# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms


class TextInputWithOptions(forms.TextInput):
    """Text input form with option dropdown."""

    template_name = "netbox_aci_plugin/widgets/textinput_with_options.html"

    def __init__(self, options, attrs=None) -> None:
        """Initialize the widget."""
        self.options = options
        super().__init__(attrs)

    def get_context(self, name, value, attrs) -> dict:
        """Get the context for the widget and add options to the context."""
        context = super().get_context(name, value, attrs)
        context["widget"]["options"] = self.options
        return context
