from django.db import connection


class InlineEncodedStorage(object):
    def __init__(self, key):
        self.key = key

    def read(self, name):
        curs = connection.cursor()
        curs.execute("SELECT data FROM util_storage WHERE key=%(key)s AND storageid=%(id)s", {
            'key': self.key, 'id': name})
        rows = curs.fetchall()
        if len(rows) != 1:
            return None
        return rows[0][0]

    def save(self, name, content):
        content.seek(0)
        curs = connection.cursor()
        params = {
            'key': self.key,
            'id': name,
            'data': content.read(),
            }
        curs.execute("UPDATE util_storage SET data=%(data)s WHERE key=%(key)s AND storageid=%(id)s", params)
        if curs.rowcount == 0:
            curs.execute("INSERT INTO util_storage (key, storageid, data) VALUES (%(key)s, %(id)s, %(data)s)", params)
        return name


def inlineencoded_upload_path(instance, filename):
    # Needs to exist for old migrations, but *NOT* in use
    return None
