import psycopg2
from ..config import KV_POSTGRES


class PostgresKV:
    def __enter__(self):
        self.db = psycopg2.connect(**KV_POSTGRES)
        self.cur = self.db.cursor()
        self.cur.execute(
            'CREATE TABLE IF NOT EXISTS kv ('
            'key bytea NOT NULL PRIMARY KEY,'
            'value bytea NOT NULL'
            ')'
        )
        self.db.commit()
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def get(self, key):
        self.cur.execute('SELECT value FROM kv WHERE key = %s', (key, ))
        res = self.cur.fetchone()
        if res is not None:
            res = res[0]
        return res

    def put(self, key, value):
        try:
            self.cur.execute('INSERT INTO kv (key, value) VALUES (%s, %s)', (key, value))
        except psycopg2.IntegrityError:
            self.db.rollback()
        else:
            self.db.commit()
