# split_by_year.py

Splits the rows of an Excel spreadsheet into separate spreadsheets, one per year, based on the year of a `Start Date` column.

## What it does

1. Reads the input Excel file (defaults to the first sheet).
2. Parses the date column (default `Start Date`) as dates.
3. Warns about and skips any rows with a missing or unparseable date.
4. Groups the remaining rows by year.
5. Writes one output `.xlsx` file per year, named `<input filename>_<year>.xlsx`, containing only that year's rows.

## Requirements

- Python 3
- `pandas`
- `openpyxl`

Install dependencies:

```bash
pip3 install pandas openpyxl
```

## Usage

```bash
python3 split_by_year.py -i <input_file.xlsx> [-o <output_dir>] [-s <sheet_name>] [-c <date_column>]
```

| Argument | Description | Default |
|---|---|---|
| `-i`, `--input_file_path` | Path to the input Excel file | *required* |
| `-o`, `--output_dir` | Directory to write the per-year output files to | current directory (`.`) |
| `-s`, `--sheet_name` | Sheet name or index to read from the input file | first sheet (`0`) |
| `-c`, `--date_column` | Name of the date column to split on | `Start Date` |

**Example:**

```bash
python3 split_by_year.py -i Sightings.xlsx -o yearly_files
```

If `Sightings.xlsx` contains rows dated across 2022, 2023, and 2024, this produces:

```
yearly_files/Sightings_2022.xlsx
yearly_files/Sightings_2023.xlsx
yearly_files/Sightings_2024.xlsx
```

## Notes

- The output directory is created automatically if it doesn't already exist.
- Rows are matched to a year using pandas' date parsing, so most common date formats in the column are handled automatically; anything pandas can't parse is skipped with a warning rather than causing the script to fail.
- Output files contain the same columns as the input, minus the temporary year field used internally to split the data.
