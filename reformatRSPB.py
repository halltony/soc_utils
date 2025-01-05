# Update for 2023 AssCount Comment seems to have been removed from the source Excel

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil
import re
from OSGridConverter import latlong2grid

def processIncidentalRowCount(row):
    count = ''
    # update Y to count of 1.  All examples seen are for count type of individual, present or other singular category
    if row['Primary Count'] == 'Y':
        row['Primary Count'] = 1
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

def getDuplicates(df):
    #Find the duplicate rows
    all_duplicates_df = df[df.duplicated(subset = ['Species', 'Place', 'Date'], keep=False)]
    return all_duplicates_df

def removeDuplicates(df):
    # Append the Observer ID to the place name to make multiple counts for the same species
    # on the same data at the same place unique.
    # Find the duplicate rows
    df.sort_values(by = ['Species', 'Place', 'Date'])
    all_duplicates_df = df[df.duplicated(subset = ['Species', 'Place', 'Date', 'Observer'], keep=False)]
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
            place_df = species_df[species_df['Place'] == place]
            # get a list of dates for that place
            dateList = place_df.Date.unique()
            for date in dateList:
                # create a df containing just the rows for that date
                date_df = place_df[place_df['Date'] == date]
                # get a list of observers for that date
                observerList = date_df.Observer.unique()
                for observer in observerList:
                    # create a df containing just the rows for that observer
                    observer_df = date_df[date_df['Observer'] == observer]
                    for row in observer_df:
                        duplicate_filter = (df['Species'] == species) & (df['Place'] == place) & (df['Date'] == date) & (df['Observer'] == observer)
                        df.loc[duplicate_filter, 'Place'] = df.loc[duplicate_filter, 'Place'] + ' - ' + df.loc[duplicate_filter, 'ObsId']
    return df

def setBreeding(row):
    breeding = ''
    if pd.notna(row['Fledged Max']) and row['Fledged Max'] > 0:
        breeding = '12'
    elif pd.notna(row['Chicks Max']) and row['Chicks Max'] > 0:
        breeding = '16'
    else:
        if 'ARM Species Records' in row['Dataset']:
            if pd.notna(row['Primary Count Unit']):
                if row['Primary Count Unit'] == 'Singing/Displaying male':
                    breeding = '02'
                elif row['Primary Count Unit'] == 'Pair':
                    breeding = '03'
                elif row['Primary Count Unit'] == 'Recently hatched chick' or \
                    row['Primary Count Unit'] == 'Adult(s) with brood' or \
                    row['Primary Count Unit'] == 'Chick' or \
                    row['Primary Count Unit'] == 'Part grown chick':
                    breeding = '16'
                elif row['Primary Count Unit'] == 'Apparently occupied territory':
                    breeding = '04'
                elif row['Primary Count Unit'] == 'Apparently occupied burrow' or \
                    row['Primary Count Unit'] == 'Apparently occupied nest':
                    breeding = '13'
        else:
            # (breeding) Activity populated in incidental records
            if pd.notna(row['Activity']):
                if row['Activity'] == 'Singing':
                    breeding = '02'
                elif row['Activity'] == 'Adults carrying faecal sac or food for young':
                    breeding = '14'
                elif row['Activity'] == 'Nest under construction' or row['Activity'] == 'Nest building or excavating':
                    breeding = '09'
                elif row['Activity'] == 'Visiting nest site':
                    breeding = '06'
                elif row['Activity'] == 'Mating' or row['Activity'] == 'Displaying':
                    breeding = '05'
                elif row['Activity'] == 'Family party':
                    breeding = '12'
                elif row['Activity'] == 'Apparently incubating':
                    breeding = '15'
                elif row['Activity'] == 'Adult observed incubating eggs/chicks':
                    breeding = '16'
    return breeding

def setActivity(row):
    activity = ''
    if pd.notna(row['Activity']):
        if row['Activity'] == 'Feeding/Drinking' or \
           row['Activity'] == 'Hunting':
           activity = '1'
        elif row['Activity'] == 'In flight':
           activity = '2'
        elif row['Activity'] == 'At roost':
           activity = '4'
        elif row['Activity'] == 'Apparently incubating' or \
             row['Activity'] == 'Adult observed incubating eggs/chicks':
             activity = '7'
    return activity


parser = argparse.ArgumentParser(description="Reformat RSPB Data for Birdtrack upload",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-i", "--input_file_path", type=str, required=True, help='Filepath to the RSPB Excel file to be processed')
parser.add_argument("-o", "--output_file_path", type=str, required=True, help='Filepath to the Birdtrack upload Excel file to be created')
parser.add_argument("-y", "--year", type=str, required=True, help='Year to be used for ARM dates spanning the whole year')


args = parser.parse_args()
config = vars(args)

input_df = pd.read_excel(args.input_file_path, sheet_name='Export')

# Make the Observation Id a string
input_df['Observation ID'] = input_df['Observation ID'].apply(str)

# Convert the eggs, chicks and fledged max fields to ints
input_df['Eggs Min'] = input_df['Eggs Min'].astype('Int16')
input_df['Eggs Max'] = input_df['Eggs Max'].astype('Int16')
input_df['Chicks Min'] = input_df['Chicks Min'].astype('Int16')
input_df['Chicks Max'] = input_df['Chicks Max'].astype('Int16')
input_df['Fledged Min'] = input_df['Fledged Min'].astype('Int16')
input_df['Fledged Max'] = input_df['Fledged Max'].astype('Int16')
input_df['AssCount Count Value'] = input_df['AssCount Count Value'].astype('Int16')



arm_output_df = pd.DataFrame(columns=['Species', 'Count', 'Place', 'Latitude', 'Longitude', 'Date', 'Breeding evidence', 'Comment', 'Observer',
                                      'Sensitive', 'Activity', 'Age_Sex_Plumage', 'Source', 'ObsId'])
non_arm_output_df = pd.DataFrame(columns=['Species', 'Count', 'Place', 'Latitude', 'Longitude', 'Date', 'Breeding evidence', 'Comment', 'Observer',
                                          'Sensitive', 'Activity', 'Age_Sex_Plumage', 'Source', 'ObsId'])

residents = ['Black Grouse', 'Black-headed Gull', 'Blackbird', 'Blue Tit', 'Bullfinch', 'Buzzard', 'Canada Goose', 'Carrion Crow',
             'Chaffinch', 'Coal Tit', 'Collared Dove', 'Coot', 'Dipper', 'Dunnock', 'Gadwall', 'Goldcrest', 'Goldeneye',
             'Goldfinch', 'Goosander', 'Great Crested Grebe', 'Great Spotted Woodpecker', 'Great Tit', 'Greenfinch', 'Greylag Goose',
             'House Sparrow', 'Jackdaw', 'Jay', 'Kestrel', 'Kingfisher', 'Lapwing', 'Lesser Redpoll', 'Little Grebe', 'Long-tailed Tit',
             'Magpie', 'Mallard', 'Meadow Pipit', 'Mistle Thrush', 'Moorhen', 'Mute Swan', 'Nuthatch', 'Oystercatcher', 'Peregrine',
             'Pheasant', 'Pied Wagtail', 'Raven', 'Redshank', 'Reed Bunting', 'Robin', 'Shoveler', 'Siskin',
             'Skylark', 'Snipe', 'Song Thrush', 'Sparrowhawk', 'Starling', 'Stonechat', 'Tawny Owl', 'Teal', 'Treecreeper',
             'Tufted Duck', 'Water Rail', 'Wigeon', 'Woodcock', 'Woodpigeon', 'Wren']
migrants = ['Blackcap', 'Chiffchaff', 'Common Sandpiper', 'Cuckoo', 'Garden Warbler', 'Grasshopper Warbler', 'Little Ringed Plover', 'Osprey',
            'Pied Flycatcher', 'Redstart', 'Sand Martin', 'Sedge Warbler', 'Spotted Crake', 'Spotted Flycatcher', 'Swallow', 'Tree Pipit', 'Whitethroat',
             'Willow Warbler', 'Wood Warbler']

dateForResidents = '15/04/{}'.format(args.year)
dateForMigrants = '01/06/{}'.format(args.year)

for index, row in input_df.iterrows():

    # Count and Date
    if 'ARM Species Records' in row['Dataset']:
        count = processARMRowCount(row)
        if row['Common Name'] in residents:
            rowDate = datetime.strptime(dateForResidents, '%d/%m/%Y').date()
        elif row['Common Name'] in migrants:
            rowDate = datetime.strptime(dateForMigrants, '%d/%m/%Y').date()
        else:
            print('Error - ARM record species {} not in residents or migrants'.format(row['Common Name']))
    else:
        count = processIncidentalRowCount(row)
        rowDate = datetime.strptime(row['Start Date'].strftime("%d/%m/%Y"), '%d/%m/%Y').date()

    # Place
    place = re.search(r',?\s*([\w\']*\s*\w*\sRSPB)', row['Dataset']).group(1)
    if 'ARM Species Records' not in row['Dataset']:    
        if pd.notna(row['Feature']) and not re.match(r'^\d+[a-z]?$', row['Feature']) and not row['Feature'] == 'DO NOT USE ':
            place += ', ' + row['Feature']
        if pd.notna(row['Location']):
            place += ', ' + row['Location']
    else:
        if pd.notna(row['Feature Types']):
            place += ' - ' +row['Feature Types']

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
    if row['Primary Count Unit'] == 'Adult Male' or row['Primary Count Unit'] == 'Adult Female':
        comments.append('Count is of {}'.format(row['Primary Count Unit']))
    # if pd.notna(row['AssCount Comment']):
    #     comments.append('AssCount Comment: {}'.format(row['AssCount Comment']))
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

    # Age and Plumage
    ageAndPlumage = ''
    if row['Primary Count Unit'] == 'Adult Male':
        ageAndPlumage = '[{{"SEX":"M","COUNT":"{}"}}]'.format(count)
    if row['Primary Count Unit'] == 'Adult Female':
        ageAndPlumage = '[{{"SEX":"F","COUNT":"{}"}}]'.format(count)

    # Breeding
    breeding = setBreeding(row)

    # Activity
    activity = setActivity(row)

    # Write to the output DF
    if 'ARM Species Records' in row['Dataset']:
        arm_output_df.loc[index] = {'Species'           : row['Common Name'],
                                    'Count'             : count,
                                    'Place'             : place,
                                    'Latitude'          : row['Latitude'],
                                    'Longitude'         : row['Longitude'],
                                    'Date'              : rowDate,
                                    'Comment'           : comment,
                                    'Observer'          : observer,
                                    'Sensitive'         : sensitive,
                                    'Source'            : 'RSPB',
                                    'ObsId'             : row['Observation ID'],
                                    'Age and plumage'   : ageAndPlumage,
                                    'Breeding evidence' : breeding,
                                    'Activity'          : activity}
    else:
        non_arm_output_df.loc[index] = {'Species'           : row['Common Name'],
                                        'Count'             : count,
                                        'Place'             : place,
                                        'Latitude'          : row['Latitude'],
                                        'Longitude'         : row['Longitude'],
                                        'Date'              : rowDate,
                                        'Comment'           : comment,
                                        'Observer'          : observer,
                                        'Sensitive'         : sensitive,
                                        'Source'            : 'RSPB',
                                        'ObsId'             : row['Observation ID'],
                                        'Age and plumage'   : ageAndPlumage,
                                        'Breeding evidence' : breeding,
                                        'Activity'          : activity}

# Now remove the duplicates by appending the RSPB observation id to the place name
arm_output_df = removeDuplicates(arm_output_df)
non_arm_output_df = removeDuplicates(non_arm_output_df)
# Drop the observation column as it's not needed any more
arm_output_df = arm_output_df.drop('ObsId', axis=1)
non_arm_output_df = non_arm_output_df.drop('ObsId', axis=1)

# Report any remaining duplicates
arm_duplicate_count = len(arm_output_df[arm_output_df.duplicated(subset = ['Species', 'Place', 'Date','Observer'], keep=False)])
non_arm_duplicate_count = len(non_arm_output_df[non_arm_output_df.duplicated(subset = ['Species', 'Place', 'Date', 'Observer'], keep=False)])

print('There are {} duplicates remaining in the arm output'.format(arm_duplicate_count))
print('There are {} duplicates remaining in the non-arm output'.format(non_arm_duplicate_count))

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