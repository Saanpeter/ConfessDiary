import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="735698.Sa",
    host="localhost",
    port="5432"
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE DATABASE whisperbook;")
cur.close()
conn.close()
print("Database created.")
