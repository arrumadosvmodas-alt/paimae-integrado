import sqlite3
import os

def run_migration():
    # Verifica a localização do banco
    db_path = "paimae.db"
    if not os.path.exists(db_path) and os.path.exists("../paimae.db"):
        db_path = "../paimae.db"
    
    print(f"Conectando ao banco em: {os.path.abspath(db_path)}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN lgpd_accepted BOOLEAN DEFAULT 0")
        print("Coluna lgpd_accepted adicionada com sucesso.")
    except Exception as e:
        print("Aviso/Erro ao adicionar lgpd_accepted:", e)

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN lgpd_accepted_at DATETIME")
        print("Coluna lgpd_accepted_at adicionada com sucesso.")
    except Exception as e:
        print("Aviso/Erro ao adicionar lgpd_accepted_at:", e)

    conn.commit()
    conn.close()
    print("Migração estrutural de colunas da LGPD finalizada.")

if __name__ == "__main__":
    run_migration()
