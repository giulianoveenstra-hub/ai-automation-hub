"""Single authoritative local database with transactional optimistic locking."""
import json
import sqlite3
from .model import seed, validate

class Conflict(Exception):
    pass

class Store:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS workspace (id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, data TEXT NOT NULL)')
            db.execute('INSERT OR IGNORE INTO workspace VALUES (1,0,?)', (json.dumps(seed()),))

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
