from datetime import datetime, timezone
from types import SimpleNamespace

from django.test import SimpleTestCase

from utils.audit_util import parse_changed_fields
from utils.hview_util import Event as HistoryEvent
from utils.view_util import Event


class AuditEventTests(SimpleTestCase):
    def make_event(self, changed_fields, event_type='Create'):
        return SimpleNamespace(
            changed_fields=changed_fields,
            get_event_type_display=lambda: event_type,
            user=None,
            datetime=datetime.now(timezone.utc),
            content_type=SimpleNamespace(app_label='catalogue', model='podcast'),
            object_id='1',
        )

    def test_events_without_field_changes(self):
        for value in ['', '  ', None, 'null', 'None', '{}', {}]:
            for reader in [Event, HistoryEvent]:
                with self.subTest(value=value, reader=reader):
                    event = reader(self.make_event(value))
                    self.assertFalse(event.changed)
                    self.assertEqual(event.changes, [])

    def test_json_changes_with_booleans_and_null(self):
        value = '{"approved": [false, true], "notes": [null, "added"]}'
        for reader in [Event, HistoryEvent]:
            with self.subTest(reader=reader):
                event = reader(self.make_event(value, 'Update'))
                self.assertTrue(event.changed)
                changes = {change.field: change for change in event.changes}
                self.assertIs(changes['approved'].old_state, False)
                self.assertIs(changes['approved'].new_state, True)
                self.assertIsNone(changes['notes'].old_state)
                self.assertEqual(changes['notes'].new_state, 'added')

    def test_legacy_and_dictionary_changes(self):
        changes = {'approved': [False, True], 'notes': [None, 'added']}
        for value in [repr(changes), changes]:
            for reader in [Event, HistoryEvent]:
                with self.subTest(value=value, reader=reader):
                    event = reader(self.make_event(value, 'Update'))
                    self.assertEqual(event.cf_dict, changes)
                    self.assertEqual(len(event.changes), 2)

    def test_related_creation_without_changes_is_preserved(self):
        event = Event(self.make_event(''), 'podcasts', 'Example podcast')
        self.assertEqual(len(event.changes), 1)
        self.assertEqual(event.changes[0].field, 'podcasts (created)')
        self.assertEqual(event.changes[0].new_state, 'Example podcast')

    def test_invalid_values_and_expressions_are_rejected(self):
        for value in ['broken', '[]', 'true', "dict(notes=['old', 'new'])"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_changed_fields(value)
