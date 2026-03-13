import sqlite3
import pandas as pd

# Connessione al DB
conn = sqlite3.connect("zingarate.db")

# Estrazione dati in un DataFrame
df = pd.read_sql_query("SELECT * FROM preferenze", conn)

# Stampa a schermo
print(df.to_string())

conn.close()