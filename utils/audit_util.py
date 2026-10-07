"""Read current JSON and legacy Python literals from audit history."""

import ast
import json


def parse_changed_fields(value):
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return {}
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError) as exc:
                raise ValueError('Invalid audit changed_fields') from exc
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError('Audit changed_fields must be a dictionary')
    return value
