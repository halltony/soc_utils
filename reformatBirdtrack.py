#!/Users/Tony/.pyenv/shims/python

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil

#defining function
def get_season(dateTime):
  m = dateTime.month
  d = dateTime.day
  if (m < 5 and d < 16):
    season = 'Winter/Spring'
  elif m < 8:
    season = 'Summer'
  else:
    season = 'Autumn/Winter'
  return season

parser = argparse.ArgumentParser(description="Reformat Birdtrack Data for Annual Report",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='Filepath to the Excel file to be processed')


args = parser.parse_args()
config = vars(args)

#Save a backup of the original file
backup = args.file_path.replace('.xlsx', '.bak')
shutil.copyfile(args.file_path, backup)

df = pd.read_excel(args.file_path, converters= {'Date': pd.to_datetime})

# Remove columns that are not required
columnsToRemove = ['BTO species code', 'BOU order', 'Grid reference', 'Uncertainty radius',
                   'Geometry type', 'Lat', 'Long', 'Pinpoint', 'Observer name', 'User ID', 'User name', 
                   'Start time', 'End time']

df = df.drop(columnsToRemove, axis=1)

# Reorder the remaining columns
requiredColumnOrder = ['Species', 'Scientific name', 'Count', 'Place', 'Date', 'Comment']
df = df.reindex(columns=requiredColumnOrder)

# Insert a season column
df['Season'] = df['Date'].map(get_season)

# Sort by date order within species - this requires converting to a datetime object
df['Date'] = pd.to_datetime(df.Date, dayfirst=True)
df = df.sort_values(['Species','Date'],ascending=[True,True])
df['Date'] = df['Date'].dt.strftime('%d %b')

# Overwrite the file
df.to_excel(args.file_path, index=False)