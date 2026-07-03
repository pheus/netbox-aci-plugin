# Validators & Constants

Validators and shared constants are tightly coupled in this codebase:
regex validators reference character-class constants from
`constants.py`, and range/enum validators reference both range
constants and `ChoiceSet` definitions. This doc covers both.

## File layout

- `netbox_aci_plugin/validators.py`: every regex validator instance
  and every function validator used by `validators=[...]`.
- `netbox_aci_plugin/constants.py`: shared constants grouped by
  domain.

## Regex validators: Required / Optional pairs

The *name* validators ship in two variants:

- **Required (`+`)**: matches one or more characters. Pair with
  `blank=False` model fields.
- **Optional (`*`)**: matches zero or more characters (i.e. accepts
  the empty string). Pair with `blank=True` model fields so the schema
  and clients agree on what an empty value looks like.

`ACIPolicyDescriptionValidator` is a single optional-only validator (no
Required variant and no Required/Optional suffix in its name).

Both variants share regex character classes from `constants.py`
(`NAME_CHAR_CLASS`, `DESC_CHAR_CLASS`); don't inline regex literals in
the validator file.

```python
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .constants import DESC_CHAR_CLASS, NAME_CHAR_CLASS


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
```

Naming: `<Domain><Thing><Required|Optional>Validator` (PascalCase,
suffix `Validator`). Required and Optional variants always share the
same error message; the user-facing string doesn't mention
required-vs-optional, only the allowed character set.

## Function validators

Function validators perform range + enum-fallback checks. They go
directly into `validators=[...]` lists on the model field:

```python
def validate_contract_filter_ip_protocol(value: str) -> None:
    """Validate the IP protocol value for ContractFilterEntry."""
    if value in dict(ContractFilterIPProtocolChoices) or value in [
        str(i) for i in range(0, 256)
    ]:
        return

    try:
        number = int(value)
        if 0 <= number <= 255:
            return
    except (ValueError, TypeError):
        pass

    valid_choices = ", ".join(dict(ContractFilterIPProtocolChoices).keys())
    raise ValidationError(
        _(
            "IP Protocol must be a number between 0 and 255 or"
            " one of the following values: {valid_choices}"
        ).format(valid_choices=valid_choices)
    )
```

Conventions:

- Name: `validate_<domain>_<thing>(value)` (snake_case, prefix
  `validate_`).
- Accept either an enum choice or a numeric value in a range.
- On failure, the error message **lists the valid choices** via
  `", ".join(dict(<Choices>).keys())`. The user shouldn't have to dig
  through code to discover the allowed values.

Some function validators check value *combinations* and do not follow the
range + choice shape. `validate_contract_filter_tcp_rules`
(`validators.py`) validates that `established` and `unspecified` are not
combined with other TCP flags; it has no numeric range and lists no
choices.

### Keep f-strings out of `_()`

Do not put f-strings inside translation calls. Eager f-strings are
evaluated before the translation lookup runs, so the source `msgid`
becomes the formatted string and translators cannot match it. Format
after translation instead:

```python
# Bad: f-string evaluates before translation
_(
    f"IP Protocol must be a number between 0 and 255 or one of: "
    f"{valid_choices}"
)

# Good: translate first, then format
_(
    "IP Protocol must be a number between 0 and 255 or one of: {valid_choices}"
).format(valid_choices=valid_choices)
```

## `constants.py` organization

Section grouping by domain, with section comments:

```python
#
# Validation
#
ACI_NAME_MAX_LEN: Final[int] = 64
ACI_DESC_MAX_LEN: Final[int] = 128
NAME_CHAR_CLASS: Final[str] = r"[A-Za-z0-9_.:-]"
DESC_CHAR_CLASS: Final[str] = r"[A-Za-z0-9!#$%()*,-./:;@ _{|}~?&+]"
VLAN_VID_MIN: Final[int] = 1
VLAN_VID_MAX: Final[int] = 4094
FABRIC_ID_MIN: Final[int] = 1
FABRIC_ID_MAX: Final[int] = 128
# ...

#
# Contract Relation
#
CONTRACT_RELATION_OBJECT_TYPES = Q(...)

#
# Endpoint Security Group
#
ESG_ENDPOINT_GROUP_SELECTORS_MODELS = Q(...)
ESG_ENDPOINT_SELECTORS_MODELS = Q(...)
```

### Primitive constants

- `typing.Final` is applied to the length and char-class constants:
  `ACI_NAME_MAX_LEN: Final[int] = 64`, `ACI_DESC_MAX_LEN: Final[int] = 128`,
  `NAME_CHAR_CLASS: Final[str]`, `DESC_CHAR_CLASS: Final[str]`
  (`constants.py:13-17`).
- Range constants follow `<DOMAIN>_<PROPERTY>_<MIN|MAX>`:
  `VLAN_VID_MIN`, `NODE_ID_MAX`, `FABRIC_ID_MIN`. These also carry
  `Final[int]`, same as the length constants above
  (`constants.py:19-29`).

### Q-object content-type filters

`Q` objects encoding `limit_choices_to` predicates for Generic Foreign
Keys live in `constants.py`. Naming:

- `<MODEL>_<RELATION>_OBJECT_TYPES`: the set of valid target models
  for a given GFK relation. Example:
  `CONTRACT_RELATION_OBJECT_TYPES`.
- `<MODEL>_OBJECT_TYPES`: the set of valid target models for a GFK
  that spans multiple object kinds with no named relation. Example:
  `NODE_OBJECT_TYPES` (`constants.py`, used at `nodes.py:64`).
- `<MODEL>_<USAGE>_MODELS`: the set of valid models for a specific
  selector or attribute usage. Example:
  `ESG_ENDPOINT_GROUP_SELECTORS_MODELS`,
  `USEG_NETWORK_ATTRIBUTES_MODELS`.

```python
CONTRACT_RELATION_OBJECT_TYPES = Q(
    app_label="netbox_aci_plugin",
    model__in=(
        "aciendpointgroup",
        "aciendpointsecuritygroup",
        "aciexternalendpointgroup",
        "aciusegendpointgroup",
        "acivrf",
    ),
)
```

These are referenced from:

- Model field `limit_choices_to=CONTRACT_RELATION_OBJECT_TYPES` on the
  GFK's `_type` `ForeignKey(to="contenttypes.ContentType", ...)`.
- The `_validate_generic_uniqueness()` helper in
  `UniqueGenericForeignKeyMixin` (see [Models - Generic Foreign Key
  pattern](models.md#generic-foreign-key-pattern)).
