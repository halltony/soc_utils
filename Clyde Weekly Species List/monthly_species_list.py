import os
from datetime import date, timedelta
import pandas as pd

INPUT = "your_file.xlsx"

# Previous month, e.g. run in Nov 2026 -> Oct-2026
first_of_this_month = date.today().replace(day=1)
last_month = first_of_this_month - timedelta(days=1)
OUTPUT = f"{last_month.strftime('%b')}-{last_month.year}_species_list.csv"

if os.path.exists(OUTPUT):
    os.remove(OUTPUT)

df = pd.read_excel(INPUT, sheet_name="Summary")

# Keep only the first 6 columns
df = df.iloc[:, :6].copy()

col = df["Selected Species"].astype(str).str.strip()

# Rows to drop: value in square or round brackets, or starting with 'Unidentified'
drop = (
    col.str.match(r"^\[.*\]$")
    | col.str.match(r"^\(.*\)$")
    | col.str.startswith("Unidentified")
)

df = df[~drop].copy()

# Rename Rock Dove -> Feral Pigeon
df["Selected Species"] = df["Selected Species"].replace("Rock Dove", "Feral Pigeon")

df.to_csv(OUTPUT, index=False)
print(f"Wrote {OUTPUT}: kept {len(df)} rows, dropped {drop.sum()}; columns: {list(df.columns)}")