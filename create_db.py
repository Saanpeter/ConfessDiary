import os
from urllib.parse import urlparse

import psycopg2


def build_connection_kwargs():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL is not set.')

    parsed = urlparse(database_url)
    return {
        'dbname': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'sslmode': 'require',
    }


connection_kwargs = build_connection_kwargs()
conn = psycopg2.connect(**connection_kwargs)
conn.autocommit = True
cur = conn.cursor()
cur.execute('CREATE DATABASE IF NOT EXISTS whisperbook;')
cur.close()
conn.close()
print('Database created.')
