"""Single authoritative local database with transactional optimistic locking."""
import json
import sqlite3
from .model import seed, validate, migrate

class Conflict(Exception):
    pass

class Store:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS workspace (id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, data TEXT NOT NULL)')
            db.execute('INSERT OR IGNORE INTO workspace VALUES (1,0,?)', (json.dumps(seed()),))
            # Migration and its exact original snapshot commit together. An older
            # browser keeps its old revision and cannot overwrite the new schema.
            if not db.in_transaction:
                db.execute('BEGIN IMMEDIATE')
            revision, raw = db.execute('SELECT revision,data FROM workspace WHERE id=1').fetchone()
            converted = migrate(json.loads(raw))
            if converted != json.loads(raw):
                validate(converted)
                db.execute('CREATE TABLE IF NOT EXISTS migration_backup (revision INTEGER PRIMARY KEY, data TEXT NOT NULL)')
                db.execute('INSERT OR IGNORE INTO migration_backup VALUES (?,?)', (revision, raw))
                db.execute('UPDATE workspace SET revision=revision+1,data=? WHERE id=1', (json.dumps(converted,ensure_ascii=False),))

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def read(self):
        with self.connect() as db:
            revision, raw = db.execute('SELECT revision,data FROM workspace WHERE id=1').fetchone()
            return dict(revision=revision, data=json.loads(raw))

    def save(self, revision, data):
        data = validate(data)
        with self.connect() as db:
            changed = db.execute('UPDATE workspace SET revision=revision+1,data=? WHERE id=1 AND revision=?', (json.dumps(data, ensure_ascii=False), revision)).rowcount
            if not changed:
                raise Conflict('Zwischenzeitlich geändert. JSON-Sicherung deiner Änderungen exportieren, dann neu laden und abgleichen.')
        # Return this transaction's exact revision, never a later concurrent read.
        return dict(revision=revision + 1, data=data)
