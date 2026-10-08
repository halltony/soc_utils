#!/usr/bin/env python3
"""
split_by_year.py

Splits the rows of an Excel spreadsheet into separate spreadsheets, one per
year, based on the year of a 'Start Date' column.

Usage:
    python3 split_by_year.py -i input.xlsx [-o output_dir] [-s SheetName]

Requirements:
    pip3 install pandas openpyxl
"""

import argparse
import os
import sys
import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="Split an Excel file into one file per year based on a 'Start Date' column.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-i", "--input_file_path", type=str, required=True,
                         help="Path to the input Excel file")
    parser.add_argument("-o", "--output_dir", type=str, default=".",
                         help="Directory to write the per-year output files to")
    parser.add_argument("-s", "--sheet_name", type=str, default=0,
                         help="Sheet name (or index) to read from the input file")
    parser.add_argument("-c", "--date_column", type=str, default="Start Date",
                         help="Name of the date column to split on")

    args = parser.parse_args()

    if not os.path.isfile(args.input_file_path):
        sys.exit(f"Error: input file not found: {args.input_file_path}")

    # Read the input spreadsheet
    df = pd.read_excel(args.input_file_path, sheet_name=args.sheet_name)

    if args.date_column not in df.columns:
        sys.exit(f"Error: column '{args.date_column}' not found in the input file. "
                  f"Available columns: {list(df.columns)}")

    # Make sure the date column is parsed as dates
    df[args.date_column] = pd.to_datetime(df[args.date_column], errors="coerce")

    # Warn about any rows with an unparseable/missing date
    missing_dates = df[args.date_column].isna().sum()
    if missing_dates:
        print(f"Warning: {missing_dates} row(s) have a missing or unparseable "
              f"'{args.date_column}' and will be skipped.")

    df = df.dropna(subset=[args.date_column])

    # Derive the year and base output filename
    df["_Year"] = df[args.date_column].dt.year
    base_name = os.path.splitext(os.path.basename(args.input_file_path))[0]

    os.makedirs(args.output_dir, exist_ok=True)

    years = sorted(df["_Year"].unique())
    for year in years:
        year_df = df[df["_Year"] == year].drop(columns=["_Year"])
        output_path = os.path.join(args.output_dir, f"{base_name}_{year}.xlsx")
        year_df.to_excel(output_path, index=False)
        print(f"Wrote {len(year_df)} row(s) for {year} to {output_path}")

    print(f"Done. {len(years)} year file(s) written to {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
