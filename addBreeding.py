import argparse
import pandas as pd
import numpy as np
import datetime
from datetime import date, datetime
import pathlib
import sys


#defining function
def set_breeding_status(breeding_code_str):
#     # Assumes the column will either be empty or contains an integer
    breeding_code = float(breeding_code_str)
    if pd.isna(breeding_code):
        breeding_status = 'Unknown'
    elif breeding_code == 0:
        breeding_status = 'Non-breeding'
    elif 0 < breeding_code < 3:
        breeding_status = 'Possible breeder'
    elif 2 < breeding_code < 10:
        breeding_status = 'Probable breeding'
    elif 9 < breeding_code < 17:
        breeding_status = 'Confirmed breeding'
    else:
        breeding_status = 'Invalid'
    return breeding_status

parser = argparse.ArgumentParser(description='Add a breeding status column to a CSV oe Excel file',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-f', '--input_file_path', type=str, required=True, help='filepath to the csv to be processed')
parser.add_argument('-s', '--sheet_name', type=str, required=False, default='Records#1', help='name of the sheet to be updated')
parser.add_argument('-b', '--breeding_code_column', type=str, required=False, default='Breeding status', help='column containing the breeding code')

args = parser.parse_args()
config = vars(args)

if pathlib.Path(args.input_file_path).suffix == '.csv':
    print('Processing a csv file {}'.format(args.file_path))
    df = pd.read_csv(args.input_file_path, converters= {args.date_column: pd.to_datetime})
elif pathlib.Path(args.input_file_path).suffix == '.xlsx':
    print('Processing sheet {} in Excel file {}'.format(args.sheet_name, args.input_file_path))
    df = pd.read_excel(args.input_file_path, sheet_name=args.sheet_name)
else:
    sys.exit('Invalid file type {}'.format(args.input_file_path))

df['Decoded Breeding Status'] = df[args.breeding_code_column].map(set_breeding_status)

if pathlib.Path(args.input_file_path).suffix == '.csv':
    df.to_csv(args.input_file_path, index=False)
elif pathlib.Path(args.input_file_path).suffix == '.xlsx':
    with pd.ExcelWriter(args.input_file_path, engine="openpyxl", mode="a", if_sheet_exists="replace", 
                    date_format='DD MMM', datetime_format='HH:MM') as writer:
        df.to_excel(writer, args.sheet_name, index=False)