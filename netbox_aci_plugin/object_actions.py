# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Reusable object-action button classes for ACI child-relation views."""

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.urls.exceptions import NoReverseMatch

from netbox.object_actions import AddObject
from utilities.querydict import dict_to_querydict
from utilities.views import get_action_url

__all__ = (
    "AddChildObject",
    "add_child_action",
)


class AddChildObject(AddObject):
    """An "Add <child>" button that prefills the new object's parent fields.

    Build one with add_child_action(). Unlike the stock AddObject, it links to
    the child model's add form (not the parent's) and prefills it from the
    parent object.
    """

    child_model_label = None
    url_params_spec = {}
    template_name = "netbox_aci_plugin/buttons/add_child.html"

    @classmethod
    def get_child_model(cls):
        """Resolve the configured child model."""
        if (
            not isinstance(cls.child_model_label, str)
            or cls.child_model_label.count(".") != 1
        ):
            raise ImproperlyConfigured(
                f"{cls.__name__}.child_model_label must be a dotted model label "
                f"such as 'netbox_aci_plugin.ACIContractRelation'."
            )

        try:
            return apps.get_model(cls.child_model_label)
        except (LookupError, ValueError) as exc:
            raise ImproperlyConfigured(
                f"{cls.__name__}.child_model_label is invalid: "
                f"{cls.child_model_label!r}"
            ) from exc

    @classmethod
    def get_url(cls, obj):
        """Return the child model's add URL (not the parent object's)."""
        try:
            return get_action_url(cls.get_child_model(), action="add")
        except NoReverseMatch:
            return None

    @classmethod
    def get_url_params(cls, context):
        """Build the prefilled add-form parameters, omitting None values."""
        params = {}

        for key, value in cls.url_params_spec.items():
            resolved = value(context) if callable(value) else value
            if resolved is not None:
                params[key] = resolved

        if "return_url" not in params and context.get("return_url"):
            params["return_url"] = context["return_url"]

        return dict_to_querydict(params)


def add_child_action(model, label, url_params=None):
    """Build an AddChildObject subclass for one child relation."""
    class_name = f"Add{model.rsplit('.', 1)[-1]}ChildObject"

    return type(
        class_name,
        (AddChildObject,),
        {
            "__module__": __name__,
            "child_model_label": model,
            "label": label,
            "url_params_spec": dict(url_params or {}),
        },
    )
