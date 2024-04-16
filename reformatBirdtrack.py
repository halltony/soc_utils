# This script takes a BirdTrack export file in Excel format and reformats it for use in preparation of an Annual Bird Report
# Specifically:
# 1.  It removes the columns that are not needed: BTO species code', 'Grid reference', 'Uncertainty radius',
#     'Geometry type', 'Lat', 'Long', 'Pinpoint', 'Observer name', 'User ID', 'User name', 
#     'Start time', 'End time
# 2.  It add a season column using the Date column where: Winter/Spring is from 1st Jan to 15th April,
#     Summer is from 16th April to end July and Autumn/Winter is 1st Aug to 31st Dec.
# 3.  It overwrites the input file but saves a backup of it using a suffix of .bak
# 4.  The command takes two arguments, the file path to the input file (NB it doesn't like spaces
#     in file names) and the name of the sheet in the Excel workbook to be processed

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil
import time

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

start_time = time.time()

parser = argparse.ArgumentParser(description="Reformat Birdtrack Data for Annual Report",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='Filepath to the Excel file to be processed')
parser.add_argument("-s", "--sheet_name", type=str, required=True, help='name of the sheet to be updated')

args = parser.parse_args()
config = vars(args)

#Save a backup of the original file
backup = args.file_path.replace('.xlsx', '.bak')
shutil.copyfile(args.file_path, backup)

df = pd.read_excel(args.file_path, sheet_name=args.sheet_name, converters= {'Date': pd.to_datetime})

print('Birdtrack export file to be processed contains {} records'.format(len(df)))

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

# Overwrite the file
with pd.ExcelWriter(args.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace", 
                    date_format='DD MMM', datetime_format='HH:MM') as writer:
    df.to_excel(writer, sheet_name=args.sheet_name, index=False)

runTime = time.time() - start_time
convert = time.strftime("%H:%M:%S", time.gmtime(runTime))
print('Execution took {}'.format(convert))