import os
import pandas as pd
import pyodbc

folder = r"C:\Users\somis\Downloads\Superpacks"
mdb_path = r"C:\Users\somis\Downloads\output.mdb"

conn = pyodbc.connect(
    rf"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_path};"
)

cursor = conn.cursor()

for file in os.listdir(folder):
    if file.endswith(".xlsx"):
        filepath = os.path.join(folder, file)

        # Read first sheet
        df = pd.read_excel(filepath)

        table_name = os.path.splitext(file)[0]

        # Create table dynamically
        columns = ", ".join(
            f"[{col}] TEXT(255)"
            for col in df.columns
        )

        try:
            cursor.execute(f"CREATE TABLE [{table_name}] ({columns})")
            conn.commit()
        except:
            pass

        # Insert data
        for _, row in df.iterrows():
            placeholders = ",".join(["?"] * len(row))
            cursor.execute(
                f"INSERT INTO [{table_name}] VALUES ({placeholders})",
                tuple(str(x) if pd.notna(x) else None for x in row)
            )

        conn.commit()

conn.close()