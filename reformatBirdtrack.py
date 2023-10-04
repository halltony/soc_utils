#!/Users/Tony/.pyenv/shims/python

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil



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

parser = argparse.ArgumentParser(description="Reformat Birdtrack Data for Annual Report",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the csv to be processed')


args = parser.parse_args()
config = vars(args)

#Save a backup of the original file
backup = args.file_path.replace('.csv', '.bak')
shutil.copyfile(args.file_path, backup)

df = pd.read_csv(args.file_path)

# Remove columns that are not required
columnsToRemove = ['BTO species code', 'BOU order', 'Scientific name', 'Grid reference', 'Uncertainty radius',
                   'Geometry type', 'Lat', 'Long', 'Pinpoint', 'Observer name', 'User ID', 'User name', 
                   'Start time', 'End time']

df = df.drop(columnsToRemove, axis=1)

# Reorder the remaining columns
requiredColumnOrder = ['Species', 'Count', 'Place', 'Date', 'Comment']
df = df.reindex(columns=requiredColumnOrder)

# Insert a season column
df['Season'] = df['Date'].map(get_season)

# Sort by date order within species - this requires converting to a datetime object
df['Date'] = pd.to_datetime(df.Date, dayfirst=True)
df = df.sort_values(['Species','Date'],ascending=[True,True])
df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

# Overwrite the file
df.to_csv(args.file_path, index=False)