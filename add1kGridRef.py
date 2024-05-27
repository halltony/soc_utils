# This script takes as input a csv or Excel file and creates a new column called
# 1km Grid Ref.  This will enable analysis of species distribution in an area 
# such as the Clyde. 
# It requires as arguments the file path to the input file, for Excel files, 
# the sheet name to be updated and the columns that contains the latitude and
# longitude values.
# The original file is overwritten.

import argparse
import pandas as pd
import pathlib
import sys
from OSGridConverter import latlong2grid

#defining function
def calculate1kmGR(row):
    gridRef=latlong2grid(row[args.lat_column], row[args.long_column])
    # convert to string like TG 51408 13177
    gridRefString = str(gridRef)
    #reformat to string like TG5113
    oneKmGridRefString = gridRefString[:2] + gridRefString[3:5] + gridRefString[9:11]
    return oneKmGridRefString

parser = argparse.ArgumentParser(description="convert contents of count column in a CSV file to number",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the csv or Excel file to be processed')
parser.add_argument("-s", "--sheet_name", type=str, default='Records#1', required=False, help='name of the sheet to be updated')
parser.add_argument("-n", "--lat_column", type=str, default='Lat', required=False, help="column containing the latitude")
parser.add_argument("-e", "--long_column", type=str, default='Long', required=False, help="column containing the longitude")

args = parser.parse_args()
config = vars(args)

if pathlib.Path(args.file_path).suffix == '.csv':
    print('Processing a csv file {}'.format(args.file_path))
    df = pd.read_csv(args.file_path)
elif pathlib.Path(args.file_path).suffix == '.xlsx':
    print('Processing sheet {} in Excel file {}'.format(args.sheet_name, args.file_path))
    df = pd.read_excel(args.file_path, sheet_name=args.sheet_name)
else:
    sys.exit('Invalid file type {}'.format(args.file_path))

print('Input file contains {} records'.format(len(df)))

print('Creating 1km Grid Ref column from {} and {} columns'.format(args.lat_column, args.long_column))

df['1km Grid Ref'] = df.apply(calculate1kmGR, axis=1)

if pathlib.Path(args.file_path).suffix == '.csv':
    df.to_csv(args.file_path, index=False)
elif pathlib.Path(args.file_path).suffix == '.xlsx':
    with pd.ExcelWriter(args.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace", 
                    date_format='DD MMM', datetime_format='HH:MM') as writer:
        df.to_excel(writer, sheet_name=args.sheet_name, index=False)