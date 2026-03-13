import sqlite3
import pandas as pd

DB_NAME = "zingarate.db"

def init_db():
    """Inizializza il database se non esiste."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS preferenze (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget REAL,
            periodo TEXT,
            must_have TEXT,
            deal_breaker TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_preferenza(budget, periodo, must_have, deal_breaker):
    """Inserisce un voto segreto."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO preferenze (budget, periodo, must_have, deal_breaker)
        VALUES (?, ?, ?, ?)
    ''', (budget, periodo, must_have, deal_breaker))
    conn.commit()
    conn.close()

def get_tutte_preferenze():
    """Recupera tutti i voti anonimi sotto forma di DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM preferenze", conn)
    conn.close()
    return df