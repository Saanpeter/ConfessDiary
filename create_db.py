import os
import psycopg2

conn = psycopg2.connect(
    dbname=os.environ.get('DB_ADMIN_NAME', 'postgres'),
    user=os.environ.get('DB_ADMIN_USER', 'postgres'),
    password=os.environ.get('DB_ADMIN_PASSWORD', ''),
    host=os.environ.get('DB_HOST', 'localhost'),
    port=os.environ.get('DB_PORT', '5432')
)
conn.autocommit = True
cur = conn.cursor()
cur.execute('CREATE DATABASE whisperbook;')
cur.close()
conn.close()
print('Database created.')
