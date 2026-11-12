"""Adapt existing profile arrays for ordinary forms and readable presentation."""

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _


ENTRY_FIELDS = {
    "project": {
        "heading": ("title", "name"),
        "description": ("description", "summary"),
        "url": ("url", "link"),
    },
    "experience": {
        "heading": ("role", "position", "title"),
        "organization": ("organization", "company", "organisation", "employer"),
        "period": ("period", "dates", "duration", "year"),
        "description": ("description", "summary"),
    },
}


def entry_fields(value, kind):
    initial, keys = {}, {}
    for field, aliases in ENTRY_FIELDS[kind].items():
        key = next((alias for alias in aliases if isinstance(value, dict) and alias in value), aliases[0])
        item = value.get(key) if isinstance(value, dict) else None
        if field == "heading" and isinstance(value, str):
            item = value
        initial[field] = str(item).strip() if isinstance(item, (str, int, float)) and not isinstance(item, bool) else ""
        keys[field] = key
    return initial, keys


def readable_value(value):
    if value is None:
        return _("Not specified")
    if isinstance(value, bool):
        return _("Yes") if value else _("No")
    if isinstance(value, dict):
        return "\n".join(f"{str(key).replace('_', ' ').capitalize()}: {readable_value(item)}" for key, item in value.items())
    if isinstance(value, list):
        return " · ".join(str(readable_value(item)) for item in value)
    return str(value)


def present_entry(value, kind):
    fields, keys = entry_fields(value, kind)
    fallback = _("Project") if kind == "project" else _("Experience")
    heading = fields["heading"] or (fallback if isinstance(value, dict) else readable_value(value))
    result = {
        "heading": heading,
        "subtitle": " · ".join(fields.get(field, "") for field in ("organization", "period") if fields.get(field)),
        "description": fields["description"],
        "url": "",
        "details": [],
    }
    used = {keys[field] for field, text in fields.items() if text and field != "url"}
    if fields.get("url"):
        try:
            URLValidator(schemes=["http", "https"])(fields["url"])
        except ValidationError:
            pass
        else:
            result["url"] = fields["url"]
            used.add(keys["url"])
    if isinstance(value, dict):
        result["details"] = [
            {"label": str(key).replace("_", " ").capitalize(), "value": readable_value(item)}
            for key, item in value.items()
            if key not in used
        ]
    return result


def present_entries(values, kind):
    return [present_entry(value, kind) for value in values] if isinstance(values, list) else []
