# This script adds a season column to any Excel spreadsheet
# It takes as arguments the file path to the Excel spreadsheet, 
# the name of the sheet to be updated and the name of the column 
# containing the data upon which the season should be calculated
# Seasons are determined as follows:
#   Winter/Spring is from 1st Jan to 15th April,
#   Summer is from 16th April to end July
#   Autumn/Winter is 1st Aug to 31st Dec.

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import pathlib

#defining function
def get_season(dateTime):
  m = dateTime.month
  d = dateTime.day
  if (m < 4 or (m == 4 and d < 16)):
    season = 'Winter/Spring'
  elif m < 8:
    season = 'Summer'
  else:
    season = 'Autumn/Winter'
  return season

parser = argparse.ArgumentParser(description="Add a season column to an Excel or CSV file",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the Excel or CSV file to be processed')
parser.add_argument("-s", "--sheet_name", type=str, required=False, default='Records#1', help='name of the sheet to be updated')
parser.add_argument("-c", "--date_column", type=str, required=False, default='Date', help="column containing the date")

args = parser.parse_args()
config = vars(args)

if pathlib.Path(args.file_path).suffix == '.csv':
    print('Processing a csv file {}'.format(args.file_path))
    df = pd.read_csv(args.file_path, converters= {'Date': pd.to_datetime})
elif pathlib.Path(args.file_path).suffix == '.xlsx':
    print('Processing sheet {} in Excel file {}'.format(args.sheet_name, args.file_path))
    df = pd.read_excel(args.file_path, sheet_name=args.sheet_name, converters= {'Date': pd.to_datetime})
else:
    sys.exit('Invalid file type {}'.format(args.file_path))

df['Season'] = df[args.date_column].map(get_season)

if pathlib.Path(args.file_path).suffix == '.csv':
    df.to_csv(args.file_path, index=False)
elif pathlib.Path(args.file_path).suffix == '.xlsx':
    with pd.ExcelWriter(args.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace", 
                    date_format='DD MMM', datetime_format='HH:MM') as writer:
        df.to_excel(writer, sheet_name=args.sheet_name, index=False)