import psycopg2



cur = conn.cursor()
cur.execute("SELECT datname FROM pg_database")
rows = cur.fetchall()

print("List of databases:")
for row in rows:
    print("  ",row[0])
