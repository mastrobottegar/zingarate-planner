import sqlite3
import pandas as pd

DB_NAME = "zingarate.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferenze (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autore TEXT UNIQUE,
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

def upsert_preferenza(autore, budget, date_preferite, date_evitare, date_impossibili,
                      amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Controlla se l'autore esiste già
    cursor.execute("SELECT id FROM preferenze WHERE autore=?", (autore,))
    row = cursor.fetchone()
    
    if row:
        # UPDATE: Se esiste, sovrascrivi i dati
        cursor.execute('''
            UPDATE preferenze SET 
                budget=?, date_preferite=?, date_evitare=?, date_impossibili=?,
                amerei_fare=?, preferisco_fare=?, voglio_evitare=?, assolutamente_no=?, proposta_testuale=?
            WHERE autore=?
        ''', (budget, date_preferite, date_evitare, date_impossibili,
              amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale, autore))
    else:
        # INSERT: Se non esiste, crea una nuova riga
        cursor.execute('''
            INSERT INTO preferenze (
                autore, budget, date_preferite, date_evitare, date_impossibili,
                amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (autore, budget, date_preferite, date_evitare, date_impossibili,
              amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale))
        
    conn.commit()
    conn.close()

def get_preferenza_autore(autore):
    """Recupera i dati di un singolo autore se esiste, altrimenti restituisce None"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM preferenze WHERE autore=?", (autore,))
    row = cursor.fetchone()
    
    if row:
        # Trasforma la riga in un dizionario per comodità
        col_names = [description[0] for description in cursor.description]
        dati = dict(zip(col_names, row))
    else:
        dati = None
        
    conn.close()
    return dati

def get_tutte_preferenze():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM preferenze", conn)
    conn.close()
    return df
