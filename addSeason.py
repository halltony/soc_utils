# This script adds a season column to any Excel spreadsheet
# It takes as arguments the file path to the Excel spreadsheet, 
# the name of the sheet to be updated and the name of the column 
# containing the data upon which the season should be calculated
# Seasons are determined as follows:
#   Winter = Jan - Mar
#   Spring = Apr - Jun
#   Summer = Jul - Sept
#   Winter = Oct -Dec

import argparse
import pandas as pd
import datetime
from datetime import date, datetime

#defining function
def get_season(date):
  # date_format = '%d/%m/%Y'
  # date = datetime.strptime(date_str, date_format)
  m = date.month
  x = m%12 // 3 + 1
  if x == 1:
    season = 'Winter'
  if x == 2:
    season = 'Spring'
  if x == 3:
    season = 'Summer'
  if x == 4:
    season = 'Autumn'
  return season

parser = argparse.ArgumentParser(description="Add a season column to an Excel file",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the Excel to be processed')
parser.add_argument("-s", "--sheet_name", type=str, required=True, help='name of the sheet to be updated')
parser.add_argument("-c", "--date_column", type=str, required=True, help="column containing the date")

args = parser.parse_args()
config = vars(args)

df = pd.read_excel(args.file_path, sheet_name=args.sheet_name)
df['Season'] = df[args.date_column].map(get_season)
df.to_excel(args.file_path, index=False)