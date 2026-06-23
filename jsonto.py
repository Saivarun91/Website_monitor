import json
import pandas as pd
from pathlib import Path

json_file = "test26.json"  # your JSON file

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

output_dir = Path("C:\Users\somis\Downloads")
output_dir.mkdir(exist_ok=True)

for key, value in data.items():

    try:
        # List of records -> table
        if isinstance(value, list):
            df = pd.json_normalize(value)

        # Single object -> one-row table
        elif isinstance(value, dict):
            df = pd.json_normalize(value)

        else:
            df = pd.DataFrame([{key: value}])

        output_file = output_dir / f"{key}.xlsx"
        df.to_excel(output_file, index=False)

        print(f"Created: {output_file}")

    except Exception as e:
        print(f"Failed for {key}: {e}")