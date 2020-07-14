import sqlite3
import pandas as pd

with sqlite3.connect('C:/Users/Fede/source/repos/CRUD/database.db') as conn:
    conn.row_factory = sqlite3.Row
    query = 'SELECT * FROM {}'.format("product")
    df = pd.read_sql(query,conn)
    print(df)