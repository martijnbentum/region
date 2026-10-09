# Region

## Django upgrade

The project targets Django 5.2.18. Use Python 3.10–3.12 with the pinned
dependencies and install into a separate environment before switching production:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install /path/to/partial_date-0.1-py3-none-any.whl
```

The `partial-date` package is maintained separately. The archive path in
`partial_date_requirement.txt` is specific to the original server.

Preserve the production app migration files: app migrations are excluded from
Git. The local SQLite database has easy-audit migrations 0001–0016 applied.
`region.audit_migrations` preserves migration 0004 from easy-audit 1.3.3 while
loading all other migrations from easy-audit 1.3.9. This avoids duplicate index
state caused by upstream rewriting migration 0004.

Check the production audit migration history matches this starting point. Test
against a database backup in the new environment:

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
python manage.py migrate
python manage.py collectstatic --noinput
```

Stop application writes and take a fresh database backup before production
migrations, then switch to the new environment. The save override changes in
`Item`, `Person`, `Movement`, and `Location` are deferred to a separate follow-up.

## CARTO basemaps

All current CARTO maps load `CARTO_BASEMAP_API_KEY` from the environment or the
project's ignored `.env` file, using `python-decouple`. There is no default key.
Add the replacement key to `.env` on each deployment before restarting Django:

```dotenv
CARTO_BASEMAP_API_KEY=your-new-carto-basemap-key
```

The key is passed to JavaScript using Django's `json_script` and remains visible
in browser tile requests. Use a basemap key restricted to the Region hostname
and any development hosts used for testing. Revoke the exposed key; removing it
from the current code does not remove it from Git history.
