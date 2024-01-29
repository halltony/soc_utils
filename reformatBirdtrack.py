# This script takes a BirdTrack export file in Excel format and reformats it for use in preparation of an Annual Bird Report
# Specifically:
# 1.  It removes the columns thast are not needed: BTO species code', 'Grid reference', 'Uncertainty radius',
#     'Geometry type', 'Lat', 'Long', 'Pinpoint', 'Observer name', 'User ID', 'User name', 
#     'Start time', 'End time
# 2.  It add a season column using the Date column where: Winter/Spring is from 1st Jan to 15th April,
#     Summer is from 16th April to end July and Autumn/Winter is 1st Aug to 31st Dec.
# 3.  It overwrites the input file but saves a backup of it using a suffix of .bak
# 4.  The command takes one argument which is the file path to the input file.  NB it doesn't like spaces
#     in file names

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil

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
columnsToRemove = ['BTO species code', 'Grid reference', 'Uncertainty radius',
                   'Geometry type', 'Lat', 'Long', 'Pinpoint', 'Observer name', 'User ID', 'User name', 
                   'Start time', 'End time']

df = df.drop(columnsToRemove, axis=1)

# Reorder the remaining columns
requiredColumnOrder = ['BOU order', 'Species', 'Scientific name', 'Count', 'Place', 'Date', 'Comment']
df = df.reindex(columns=requiredColumnOrder)

# Insert a season column
df['Season'] = df['Date'].map(get_season)

# Sort by date order within species - this requires converting to a datetime object
df['Date'] = pd.to_datetime(df.Date, dayfirst=True)
df = df.sort_values(['Species','Date'],ascending=[True,True])
df['Date'] = df['Date'].dt.strftime('%d %b')

# Overwrite the file
df.to_excel(args.file_path, index=False)