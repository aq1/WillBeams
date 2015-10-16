import psycopg2
from ..config import KV_POSTGRES


class PostgresKV:
    def __enter__(self):
        self.db = psycopg2.connect(**KV_POSTGRES)
        cur = self.db.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS kv ('
            'key bytea NOT NULL PRIMARY KEY,'
            'value bytea NOT NULL'
            ')'
        )
        self.db.commit()
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def get_many(self, key_set):
        cur = self.db.cursor()
        cur.execute('SELECT key, value FROM kv WHERE key IN %s', (tuple(key_set), ))
        result = {bytes(k): bytes(v) for k, v in cur.fetchall()}
        self.db.commit()  # finish transaction
        for k in key_set - result.keys():
            result[k] = None
        return result

    def put_many(self, kv_dict):
        cur = self.db.cursor()
        ins = []
        for key, value in kv_dict.items():
            cur.execute('UPDATE kv SET value = %s WHERE key = %s', (value, key))
            if not cur.rowcount:
                ins.append(key)
                ins.append(value)
        if ins:
            cur.execute(
                'INSERT INTO kv (key, value) VALUES ' + ', '.join(['(%s, %s)'] * (len(ins) // 2)),
                ins
            )
        self.db.commit()
