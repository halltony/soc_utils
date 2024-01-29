# This script takes an eBird extract in csv formatthat has been cleaned using the utility at
# https://dbradnum.shinyapps.io/eBirdCountyExtractor/
# It merges the data into a BirdTrack export Excel spreadsheet mapping fields according to the
# specification in 'Mapping eBird to BirdTrack.xlsx'
# The command takes two arguments a file path to the cleaned eBird extract and a file path to
# the BirdTrack Excel Spreadsheet.
# It overwrites the BirdTrack Excel spreadsheet but saves a backup of the original with a suffix .bak
# NB it does not tolerate file paths containing spaces

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

parser = argparse.ArgumentParser(description="Merge eBird extract into BirdTrack export",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-e", "--ebird_file_path", type=str, required=True, 
                    help='Filepath to the eBird export csv file to be merged from')

parser.add_argument("-b", "--birdtrack_file_path", type=str, required=True, 
                    help='Filepath to the BirdTrack export Excel file to be merged into')

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