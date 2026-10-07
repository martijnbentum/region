"""Use upstream audit migrations with the original migration 0004 restored."""

from easyaudit import migrations as upstream_migrations

__path__ = [*__path__, *upstream_migrations.__path__]
