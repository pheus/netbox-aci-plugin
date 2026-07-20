# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Reusable model mixins for ACI policy objects."""

from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import gettext as _

from dcim.models.mixins import CachedScopeMixin


class ACICachedScopeMixin(CachedScopeMixin):
    """Cached scope with a version-independent on_delete behavior.

    Overrides the _region and _site_group cache fields inherited from
    NetBox's CachedScopeMixin, pinning on_delete to SET_NULL. Both
    fields may cache an ancestor of the actual scope, so deleting that
    ancestor must not delete the scoped object (NetBox issue #22682).
    The explicit declarations also keep the migration state identical
    on every supported NetBox version. Remove the overrides once the
    minimum supported NetBox release ships the upstream fix.
    """

    _region = models.ForeignKey(
        to="dcim.Region",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    _site_group = models.ForeignKey(
        to="dcim.SiteGroup",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


class UniqueGenericForeignKeyMixin:
    """Enforce uniqueness for models with a GenericForeignKey.

    Attributes:
        generic_fk_field: Name of the GenericForeignKey attribute (for
            example, "aci_object").
        generic_unique_fields: Tuple of additional field names that,
            together with the GenericForeignKey, must be unique (for
            example, ("aci_contract", "role")).

    Notes:
        This mixin assumes the underlying fields for the GenericForeignKey
        follow the "<generic_fk_field>_type" and "<generic_fk_field>_id"
        naming convention.
    """

    generic_fk_field: str
    generic_unique_fields: tuple[str] = ()

    def _validate_generic_uniqueness(self) -> None:
        """Validate the uniqueness of the instance.

        Ensure that no other instance exists with the same values for the
        specified GenericForeignKey and any additional fields defined in
        generic_unique_fields.
        If a duplicate is found (excluding the current instance on update),
        raise a ValidationError.
        """
        if not getattr(self, "generic_fk_field", None):
            raise NotImplementedError(
                _("You must define 'generic_fk_field' in your model.")
            )

        # Determine the underlying fields for the GenericForeignKey.
        type_field = f"{self.generic_fk_field}_type"
        id_field = f"{self.generic_fk_field}_id"
        filter_kwargs = {
            type_field: getattr(self, type_field),
            id_field: getattr(self, id_field),
        }

        # Add additional unique fields to the filter, resolving each via its
        # attribute name so relational fields use the stored "_id" value
        # rather than the descriptor (which raises RelatedObjectDoesNotExist
        # for an unset non-nullable parent foreign key).
        for field in self.generic_unique_fields:
            model_field = self._meta.get_field(field)
            value = getattr(self, model_field.attname)
            # An incomplete instance whose required parent relation is unset
            # cannot violate uniqueness; defer to required-field validation.
            if model_field.is_relation and value is None:
                return
            filter_kwargs[model_field.attname] = value

        # Filter out the current instance (if editing an existing record).
        qs = self.__class__.objects.filter(**filter_kwargs)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        # If any instance matches these field values, raise an error.
        if qs.exists():
            # We'll only include the additional unique fields but also prepend
            # the underlying model name from the GFK for context.
            fields_in_conflict = tuple(self.generic_unique_fields)

            content_type = getattr(self, type_field, None)
            # Safely get the model name or fall back to an "Unknown" label
            model_class = content_type.model_class() if content_type else None
            model_name = (
                str(model_class._meta.verbose_name)
                if model_class and hasattr(model_class, "_meta")
                else _("Unknown model")
            )

            # Start the collected verbose names with the model name
            field_verbose_names = [model_name]

            # Convert each field to its verbose name if possible
            for field_name in fields_in_conflict:
                try:
                    model_field = self._meta.get_field(field_name)
                    verbose_name = str(model_field.verbose_name)
                except FieldDoesNotExist:  # pragma: no cover
                    # Fallback to the raw field name if it's not a recognized
                    # model field
                    verbose_name = field_name
                field_verbose_names.append(verbose_name)

            # Build a descriptive, comma-separated list of these field names.
            field_names_str = ", ".join(field_verbose_names)

            raise ValidationError(
                {
                    "__all__": _(
                        "A record already exists using the same values for "
                        "the following fields: {field_verbose_names}"
                    ).format(field_verbose_names=field_names_str)
                }
            )
