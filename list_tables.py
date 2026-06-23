import pyodbc

mdb = r"C:\Users\somis\Downloads\ARU.mdb"

conn = pyodbc.connect(
    rf"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb};"
)

cursor = conn.cursor()

print("Tables:")

for t in cursor.tables(tableType='TABLE'):
    print(t.table_name)

conn.close()