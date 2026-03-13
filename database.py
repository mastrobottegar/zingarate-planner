import sqlite3
import pandas as pd

DB_NAME = "zingarate.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Creiamo la tabella con TUTTI i nuovi campi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferenze (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autore TEXT,
            budget REAL,
            date_preferite TEXT,
            date_evitare TEXT,
            date_impossibili TEXT,
            amerei_fare TEXT,
            preferisco_fare TEXT,
            voglio_evitare TEXT,
            assolutamente_no TEXT,
            proposta_testuale TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_preferenza(autore, budget, date_preferite, date_evitare, date_impossibili,
                      amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO preferenze (
            autore, budget, date_preferite, date_evitare, date_impossibili,
            amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (autore, budget, date_preferite, date_evitare, date_impossibili,
          amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale))
    conn.commit()
    conn.close()

def get_tutte_preferenze():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM preferenze", conn)
    conn.close()
    return df
