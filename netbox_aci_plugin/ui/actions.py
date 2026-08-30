# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Panel-action classes for the declarative UI layer."""

from __future__ import annotations

from urllib.parse import urlencode

from django.urls import reverse

from netbox.ui.actions import LinkAction

__all__ = ("ACIObjectLinkAction",)


class ACIObjectLinkAction(LinkAction):
    """A LinkAction with a render condition and callable view_kwargs.

    Stock LinkAction resolves view_kwargs once at construction time and
    has no way to hide itself beyond a permission check. Panel actions
    are instantiated once per view class at module import and shared
    across every request, so resolution happens per render() call
    rather than by mutating shared instance state. Carries no knowledge
    of any specific panel or model.
    """

    def __init__(self, view_name, *, condition=None, **kwargs) -> None:
        """Guard against a positional condition binding to view_kwargs."""
        super().__init__(view_name, **kwargs)
        self.condition = condition

    def get_url(self, context):
        """Resolve callable view_kwargs against the context, build the URL.

        Does not mutate self.view_kwargs, since panel actions are
        instantiated once per view class and shared across requests.
        Unlike stock LinkAction, return_url is appended even when
        url_params is otherwise empty (the Edit and Delete actions of
        the Override triad carry no url_params of their own, but must
        still return to the port they came from).
        """
        view_kwargs = {
            key: value(context) if callable(value) else value
            for key, value in self.view_kwargs.items()
        }
        url = reverse(self.view_name, kwargs=view_kwargs)

        url_params = {
            key: value(context) if callable(value) else value
            for key, value in self.url_params.items()
        }
        url_params = {k: v for k, v in url_params.items() if v is not None}
        if "return_url" not in url_params and "object" in context:
            url_params["return_url"] = context["object"].get_absolute_url()
        if url_params:
            url = f"{url}?{urlencode(url_params)}"

        return url

    def render(self, context):
        """Render the action, gated by condition() before the permission check.

        A None condition (the default) never hides the action.
        """
        if self.condition is not None and not self.condition(context):
            return ""
        return super().render(context)
