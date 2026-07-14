import sqlite3

conn = sqlite3.connect("paimae.db")
cursor = conn.cursor()

try:
    cursor.execute("SELECT id, name, email, role, document, first_access_completed FROM users")
    rows = cursor.fetchall()
    print("All users:")
    for row in rows:
        print(row)
except Exception as e:
    print("Error:", e)

conn.close()
