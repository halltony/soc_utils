import argparse
import pandas as pd
import datetime
from datetime import date, datetime

#defining function
def get_season(date_str):
  date_format = '%d/%m/%Y'
  date = datetime.strptime(date_str, date_format)
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

parser = argparse.ArgumentParser(description="Add a season column to a CSV file",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the csv to be processed')
parser.add_argument("-c", "--date_column", type=str, required=True, help="column containing the date")

args = parser.parse_args()
config = vars(args)

df = pd.read_csv(args.file_path)
df['Season'] = df[args.date_column].map(get_season)
df.to_csv(args.file_path, index=False)