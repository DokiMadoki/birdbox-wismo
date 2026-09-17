"""SQLite locally; PostgreSQL on Render. Both use the same parameterized queries."""
import sqlite3

class Connection:
    def __init__(self, target):
        self.postgres = target.startswith(('postgres://', 'postgresql://'))
        if self.postgres:
            import psycopg
            self.raw = psycopg.connect(target, connect_timeout=15)
        else:
            self.raw = sqlite3.connect(target, timeout=15)
    def execute(self, sql, params=()):
        return self.raw.execute(sql.replace('?', '%s') if self.postgres else sql, params)
    def __enter__(self):
        return self
    def __exit__(self, kind, value, traceback):
        self.raw.rollback() if kind else self.raw.commit()
    def close(self):
        self.raw.close()

def connect(target):
    return Connection(target)
