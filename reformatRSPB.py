#!/Users/Tony/.pyenv/shims/python

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil
import re
from OSGridConverter import latlong2grid

def truncateGridRef(gridRef):
    gridRef = gridRef.replace(' ', '')
    if len(gridRef) > 6:
        letters, numbers  = gridRef[:2], gridRef[2:]
        half = int(len(numbers) / 2)
        eastings = numbers[:half]
        northings = numbers[half:]
        gridRef = letters + eastings[:2] + northings[:2]
        return gridRef
    else:
        return gridRef


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
            print('ERROR - Observation Id {} Unknown Count Type detected'.format(row['Observation Id']))

    place = re.search(r',?([\w\']*\s*\w*\sRSPB)', row['Dataset']).group(1)
    if pd.notna(row['Feature']) and not re.match(r'^\d+[a-z]?$', row['Feature']):
        place += ', ' + row['Feature']
    if pd.notna(row['Location']):
        place += ', ' + row['Location']

    if pd.notna(row['Grid Ref']):
        if len(row['Grid Ref']) > 6:
            gridRef = truncateGridRef(row['Grid Ref'])
        else:
            gridRef = row['Grid Ref']
    elif pd.notna(row['Latitude']):
        gridRef = truncateGridRef(str(latlong2grid(row['Latitude'], row['Longitude'])))
    else:
        print('ERROR - Observation Id {} does not contain either Grid Ref or Latitude'.format(row['Observation Id']))
    comment = ''
    if pd.notna(row['Comments']):
        comment = 'Comments: {}; '.format(row['Comments'])
    if pd.notna(row['Primary Count Comment']):
        comment += 'Primary Count Comment: {}; '.format(row['Primary Count Comment'])
    if pd.notna(row['Activity']) and \
       row['Activity'] != 'Not recorded':
        comment += 'Activity: {}; '.format(row['Activity'])
    if pd.notna(row['Status']) and \
       row['Status'] != 'Unknown':
        comment += 'Status: {}; '.format(row['Status'])
    if pd.notna(row['Chicks Min']):
        comment += 'Chicks Min: {}; '.format(row['Chicks Min'])
    if pd.notna(row['Chicks Max']):
        comment += 'Chicks Max: {}; '.format(row['Chicks Max'])   
    if pd.notna(row['Chicks Present']):
        comment += 'Chicks Present: {}; '.format(row['Chicks Present'])
    if pd.notna(row['Fledged Min']):
        comment += 'Fledged Min: {}; '.format(row['Fledged Min'])
    if pd.notna(row['Fledged Max']):
        comment += 'Fledged Max: {}; '.format(row['Fledged Max'])   
    if pd.notna(row['Fledged Present']):
        comment += 'Fledged Present: {}; '.format(row['Fledged Present'])
    if pd.notna(row['AssCount Count Unit']):
        comment += 'AssCount Count: {} = {}; '.format(row['AssCount Count Unit'], row['AssCount Count Value'])
    if pd.notna(row['AssCount Breeding Status Code']):
        comment += 'AssCount Breeding Status Code: {}; '.format(row['AssCount Breeding Status Code'])
    if pd.notna(row['AssCount Activity Type Code']) and \
       row['AssCount Activity Type Code'] != 'Not recorded':
        comment += 'AssCount Activity Type Code: {}; '.format(row['AssCount Activity Type Code'])
    if pd.notna(row['AssCount Comment']):
        comment += 'AssCount Comment: {}; '.format(row['AssCount Comment'])

    if row['Observer'] == 'Visitor' or \
       row['Observer'] == 'Unknown' or \
       row['Observer'].startswith('RSPB'):
        observer = 'RSPB'
    else:
        observer = row['Observer']
    
    if row['Sensitivity'] == 'RESTRICTED' or \
       row['Sensitivity'] == 'SENSITIVE':
        sensitive = 'Y'
    else:
        sensitive = ''

    output_df.loc[index] = {'Species'   : row['Common Name'],
                            'Count'     : count,
                            'Place'     : place,
                            'Gridref'   : gridRef,
                            'Date'      : row['Start Date'].strftime('%d/%m/%Y'),
                            'Comment'   : comment,
                            'Observer'  : observer,
                            'Sensitive' : sensitive}

# Write the output file
output_df.to_excel(args.output_file_path, index=False)