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

def processIncidentalRowCount(row):
    count = ''
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
    return count

def processARMRowCount(row):
    if row['Primary Count'] == 'Y':
        count = '2+'
    else:
        count = row['Primary Count'] + '+'
    return count

parser = argparse.ArgumentParser(description="Reformat RSPB Data for Birdtrack upload",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-i", "--input_file_path", type=str, required=True, help='Filepath to the RSPB Excel file to be processed')
parser.add_argument("-o", "--output_file_path", type=str, required=True, help='Filepath to the Birdtrack upload Excel file to be created')


args = parser.parse_args()
config = vars(args)

input_df = pd.read_excel(args.input_file_path, sheet_name='Export')

arm_output_df = pd.DataFrame(columns=['Species', 'Count', 'Place', 'Gridref', 'Date', 'Breeding', 'Comment', 'Observer', 'Sensitive'])
non_arm_output_df = pd.DataFrame(columns=['Species', 'Count', 'Place', 'Gridref', 'Date', 'Breeding', 'Comment', 'Observer', 'Sensitive'])

residents = ['Black Grouse', 'Black-headed Gull', 'Blackbird', 'Blue Tit', 'Bullfinch', 'Buzzard', 'Canada Goose', 'Carrion Crow',
             'Chaffinch', 'Coal Tit', 'Collared Dove', 'Coot', 'Dipper', 'Dunnock', 'Gadwall', 'Goldcrest', 'Goldeneye',
             'Goldfinch', 'Goosander', 'Great Crested Grebe', 'Great Spotted Woodpecker', 'Great Tit', 'Greenfinch', 'Greylag Goose',
             'House Sparrow', 'Jackdaw', 'Jay', 'Kestrel', 'Kingfisher', 'Lapwing', 'Lesser Redpoll', 'Little Grebe', 'Long-tailed Tit',
             'Magpie', 'Mallard', 'Meadow Pipit', 'Mistle Thrush', 'Moorhen', 'Mute Swan', 'Nuthatch', 'Oystercatcher', 'Peregrine',
             'Pheasant', 'Pied Wagtail', 'Raven', 'Redshank', 'Reed Bunting', 'Robin', 'Sedge Warbler', 'Shoveler', 'Siskin',
             'Skylark', 'Snipe', 'Song Thrush', 'Sparrowhawk', 'Starling', 'Stonechat', 'Tawny Owl', 'Teal', 'Treecreeper',
             'Tufted Duck', 'Water Rail', 'Wigeon', 'Woodcock', 'Woodpigeon', 'Wren']
migrants = ['Blackcap', 'Chiffchaff', 'Common Sandpiper', 'Cuckoo', 'Garden Warbler', 'Grasshopper Warbler', 'Little Ringed Plover',
            'Pied Flycatcher', 'Redstart', 'Sand Martin', 'Spotted Crake', 'Spotted Flycatcher', 'Swallow', 'Tree Pipit', 'Whitethroat',
             'Willow Warbler', 'Wood Warbler']

for index, row in input_df.iterrows():

    # Count and Date
    if 'ARM Species Records' in row['Dataset']:
        count = processARMRowCount(row)
        if row['Common Name'] in residents:
            rowDate = '15/04/2022'
        elif row['Common Name'] in migrants:
            rowDate = '01/06/2022'
        else:
            print('Error - ARM record species {} not in residents or migrants').format(row['Common Name'])
    else:
        count = processIncidentalRowCount(row)
        rowDate = row['Start Date'].strftime('%d/%m/%Y')

    # Place
    place = re.search(r',?\s*([\w\']*\s*\w*\sRSPB)', row['Dataset']).group(1)
    if 'ARM Species Records' not in row['Dataset']:    
        if pd.notna(row['Feature']) and not re.match(r'^\d+[a-z]?$', row['Feature']):
            place += ', ' + row['Feature']
        if pd.notna(row['Location']):
            place += ', ' + row['Location']

    # Grid Ref
    if pd.notna(row['Grid Ref']):
        if len(row['Grid Ref']) > 6:
            gridRef = truncateGridRef(row['Grid Ref'])
        else:
            gridRef = row['Grid Ref']
    elif pd.notna(row['Latitude']):
        gridRef = truncateGridRef(str(latlong2grid(row['Latitude'], row['Longitude'])))
    else:
        print('ERROR - Observation Id {} does not contain either Grid Ref or Latitude'.format(row['Observation Id']))

    # Comment
    comment = ''
    if 'ARM Species Records' in row['Dataset']:
        if row['Primary Count Unit'] == 'Pair':
            comment = row['Primary Count'] + ' ' + row['Primary Count Unit'] + 's; '
    else:
        if pd.notna(row['Primary Count Comment']):
            comment += '{}; '.format(row['Primary Count Comment'])
    if pd.notna(row['Comments']):
        comment = '{}; '.format(row['Comments'])
    if pd.notna(row['Activity']) and \
       row['Activity'] != 'Not recorded':
        comment += '{}; '.format(row['Activity'])
    if pd.notna(row['Status']) and \
       row['Status'] != 'Unknown':
        comment += '{}; '.format(row['Status'])
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

    # Observer
    if row['Observer'] == 'Visitor' or \
       row['Observer'] == 'Unknown' or \
       row['Observer'].startswith('RSPB'):
        observer = 'RSPB'
    else:
        observer = row['Observer']

    # Sensitive 
    if row['Sensitivity'] == 'RESTRICTED' or \
       row['Sensitivity'] == 'SENSITIVE':
        sensitive = 'Y'
    else:
        sensitive = ''

    # Write to the output DF
    if 'ARM Species Records' in row['Dataset']:
        arm_output_df.loc[index] = {'Species'   : row['Common Name'],
                                    'Count'     : count,
                                    'Place'     : place,
                                    'Gridref'   : gridRef,
                                    'Date'      : rowDate,
                                    'Comment'   : comment,
                                    'Observer'  : observer,
                                    'Sensitive' : sensitive}
    else:
        non_arm_output_df.loc[index] = {'Species'   : row['Common Name'],
                                        'Count'     : count,
                                        'Place'     : place,
                                        'Gridref'   : gridRef,
                                        'Date'      : rowDate,
                                        'Comment'   : comment,
                                        'Observer'  : observer,
                                        'Sensitive' : sensitive}

# Write the output file
arm_output_file_path = 'ARM_' + args.output_file_path
non_arm_output_file_path = 'Non_ARM_' + args.output_file_path
arm_output_df.to_excel(arm_output_file_path, index=False)
non_arm_output_df.to_excel(non_arm_output_file_path, index=False)