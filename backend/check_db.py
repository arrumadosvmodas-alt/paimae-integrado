import sqlite3
conn = sqlite3.connect("paimae.db")
cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables:", [t[0] for t in tables])
cur = conn.execute("SELECT COUNT(*) FROM users")
print("Users:", cur.fetchone()[0])
conn.close()
