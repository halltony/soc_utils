#!/Users/Tony/.pyenv/shims/python

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil
import re
from OSGridConverter import latlong2grid
import xlsxwriter


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

def removeDuplicates(df):
    #Find the duplicate rows
    all_duplicates_df = df[df.duplicated(['Species', 'Place', 'Date'])]

    # Get a list of unique species
    speciesList = all_duplicates_df.Species.unique()
    # For each species find rows with duplicate dates and places
    for species in speciesList:
        # Create a df containing just the rows for that species
        species_df = all_duplicates_df[all_duplicates_df['Species'] == species]
        # Get a list of unique places
        placesList = species_df.Place.unique()
        # For each place get a list of rows with duplicated dates
        for place in placesList:
            # create a df containing just the rows for that place
            place_df = species_df(species_df['Place'] == place)
            # get a list of dates for that place
            dateList = place_df.Date.unique()
            for date in dateList:
                # create a df containing just the rows for that date
                date_df = place_df[place_df['Date'] == date]
                max_count
                #     Store the count value for the row with the highest count

    # Create a string that contains '; including {count value} ' ' {comment} 
    #   for rows that do not have the highest count but contain a comment
    # Delete the rows that do not have the higher count
    # Append the comment data from those rows to the comment on the highest count row
    # Return the dataframe

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
             'Pheasant', 'Pied Wagtail', 'Raven', 'Redshank', 'Reed Bunting', 'Robin', 'Shoveler', 'Siskin',
             'Skylark', 'Snipe', 'Song Thrush', 'Sparrowhawk', 'Starling', 'Stonechat', 'Tawny Owl', 'Teal', 'Treecreeper',
             'Tufted Duck', 'Water Rail', 'Wigeon', 'Woodcock', 'Woodpigeon', 'Wren']
migrants = ['Blackcap', 'Chiffchaff', 'Common Sandpiper', 'Cuckoo', 'Garden Warbler', 'Grasshopper Warbler', 'Little Ringed Plover',
            'Pied Flycatcher', 'Redstart', 'Sand Martin', 'Sedge Warbler', 'Spotted Crake', 'Spotted Flycatcher', 'Swallow', 'Tree Pipit', 'Whitethroat',
             'Willow Warbler', 'Wood Warbler']

for index, row in input_df.iterrows():

    # Count and Date
    if 'ARM Species Records' in row['Dataset']:
        count = processARMRowCount(row)
        if row['Common Name'] in residents:
            rowDate = datetime.strptime('15/04/2022', '%d/%m/%Y').date()
        elif row['Common Name'] in migrants:
            rowDate = datetime.strptime('01/06/2022', '%d/%m/%Y').date()
        else:
            print('Error - ARM record species {} not in residents or migrants').format(row['Common Name'])
    else:
        count = processIncidentalRowCount(row)
        rowDate = datetime.strptime(row['Start Date'].strftime("%d/%m/%Y"), '%d/%m/%Y').date()

    # Place
    place = re.search(r',?\s*([\w\']*\s*\w*\sRSPB)', row['Dataset']).group(1)
    if 'ARM Species Records' not in row['Dataset']:    
        if pd.notna(row['Feature']) and not re.match(r'^\d+[a-z]?$', row['Feature']):
            place += ', ' + row['Feature']
        if pd.notna(row['Location']):
            place += ', ' + row['Location']

    # Grid Ref
    if (row['Grid Ref']):
        if len(row['Grid Ref']) > 6:
            gridRef = truncateGridRef(row['Grid Ref'])
        else:
            gridRef = row['Grid Ref']
    elif pd.notna(row['Latitude']):
        gridRef = truncateGridRef(str(latlong2grid(row['Latitude'], row['Longitude'])))
    else:
        print('ERROR - Observation Id {} does not contain either Grid Ref or Latitude'.format(row['Observation Id']))

    # Comment
    comments = []
    if 'ARM Species Records' in row['Dataset']:
        if row['Primary Count Unit'] == 'Pair':
            if row['Primary Count'] == '1':
                comments.append(row['Primary Count'] + ' ' + row['Primary Count Unit'])
            else:
                comments.append(row['Primary Count'] + ' ' + row['Primary Count Unit'] + 's')
        else:
            if pd.notna(row['Status']) and row['Status'] != 'Unknown':
                comments.append(row['Status'])
    else:
        if pd.notna(row['Primary Count Comment']):
            comments.append(row['Primary Count Comment'])
        if pd.notna(row['Status']) and row['Status'] != 'Unknown':
            comments.append(row['Status'])
    if pd.notna(row['Comments']):
        comments.append(row['Comments'])
    if pd.notna(row['Activity']) and \
       row['Activity'] != 'Not recorded':
        comments.append(row['Activity'])
    if pd.notna(row['Chicks Min']):
        comments.append('Chicks Min: {}'.format(row['Chicks Min']))
    if pd.notna(row['Chicks Max']):
        comments.append('Chicks Max: {}'.format(row['Chicks Max']))
    if pd.notna(row['Chicks Present']):
        comments.append('Chicks Present: {}'.format(row['Chicks Present']))
    if pd.notna(row['Fledged Min']):
        comments.append('Fledged Min: {}'.format(row['Fledged Min']))
    if pd.notna(row['Fledged Max']):
        comments.append('Fledged Max: {}'.format(row['Fledged Max'])) 
    if pd.notna(row['Fledged Present']):
        comments.append('Fledged Present: {}'.format(row['Fledged Present']))
    if pd.notna(row['AssCount Count Unit']):
        comments.append('AssCount Count: {} = {}'.format(row['AssCount Count Unit'], row['AssCount Count Value']))
    if pd.notna(row['AssCount Breeding Status Code']):
        comments.append('AssCount Breeding Status Code: {}'.format(row['AssCount Breeding Status Code']))
    if pd.notna(row['AssCount Activity Type Code']) and \
       row['AssCount Activity Type Code'] != 'Not recorded':
        comments.append('AssCount Activity Type Code: {}'.format(row['AssCount Activity Type Code']))
    if pd.notna(row['AssCount Comment']):
        comments.append('AssCount Comment: {}'.format(row['AssCount Comment']))
    comment = '; '.join(comments)

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
        
# Address duplicates for species, place and date in both dataframes
removeDuplicates(arm_output_df)
removeDuplicates(non_arm_output_df)

# Write the output file
arm_output_file_path = 'ARM_' + args.output_file_path
non_arm_output_file_path = 'Non_ARM_' + args.output_file_path

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer1 = pd.ExcelWriter(arm_output_file_path, engine="xlsxwriter", date_format='DD/MM/YYYY')
writer2 = pd.ExcelWriter(non_arm_output_file_path, engine="xlsxwriter", date_format='DD/MM/YYYY')

# Convert the dataframe to an XlsxWriter Excel object.
arm_output_df.to_excel(writer1, sheet_name="Sheet1", index=False)
non_arm_output_df.to_excel(writer2, sheet_name="Sheet1", index=False)

# Get the xlsxwriter workbook and worksheet objects.
workbook1 = writer1.book
workbook2 = writer2.book

worksheet1 = writer1.sheets["Sheet1"]
worksheet2 = writer2.sheets["Sheet1"]

# Close the Pandas Excel writer and output the Excel file.
writer1.close()
writer2.close()