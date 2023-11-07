#!/Users/Tony/.pyenv/shims/python

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil
import re

parser = argparse.ArgumentParser(description="Reformat RSPB Data for Birdtrack upload",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-i", "--input_file_path", type=str, required=True, help='Filepath to the RSPB Excel file to be processed')
parser.add_argument("-o", "--output_file_path", type=str, required=True, help='Filepath to the Birdtrack upload Excel file to be created')


args = parser.parse_args()
config = vars(args)

input_df = pd.read_excel(args.input_file_path, sheet_name='Export')

output_df = pd.DataFrame(columns=['Species', 'Count', 'Place', 'Gridref', 'Date', 'Breeding', 'Comment', 'Observer', 'Sensitive'])

for index, row in input_df.iterrows():
    match row['Primary Count Type']:
        case 'Number':
            count = row['Primary Count']
        case 'Estimate':
            count = 'c' + row['Primary Count']
        case 'Maximum count':
            count = 'c' + row['Primary Count']
        case 'Minimum count':
            count = row['Primary Count'] + '+'
        case 'Present':
            count = row['Primary Count']
        case _:
            print('ERROR - Unknown Count Type detected')
    place = re.search(r',?([\w\']*\s*\w*\sRSPB)', row['Dataset']).group(1)
    if pd.notna(row['Feature']):
        place += ', ' + row['Feature']
    if pd.notna(row['Location']):
        place += ', ' + row['Location']
    output_df.loc[index] = {'Species'   : row['Common Name'],
                            'Count'     : count,
                            'Place'     : place,
                            'Date'      : row['Start Date'].strftime('%d/%m/%Y')}

# Write the output file
output_df.to_excel(args.output_file_path, index=False)