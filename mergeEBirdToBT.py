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
import time
start_time = time.time()

parser = argparse.ArgumentParser(description="Merge eBird extract into BirdTrack export",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-e", "--ebird_file_path", type=str, required=True, 
                    help='Filepath to the eBird export csv file to be merged from')

parser.add_argument("-b", "--birdtrack_file_path", type=str, required=True, 
                    help='Filepath to the BirdTrack export Excel file to be merged into')

parser.add_argument("-o", "--birdtrack_bou_order_file_path", type=str, required=True, 
                    help='Filepath to the BirdTrack BOU order csv file')

args = parser.parse_args()
config = vars(args)

# Save a backup of the original file
backup = args.birdtrack_file_path.replace('.xlsx', '.bak')
shutil.copyfile(args.birdtrack_file_path, backup)
print('Backup copy of input BirdTrack data saved as {}'.format(backup))

# Open the files
eBird_df = pd.read_csv(args.ebird_file_path, converters= {'Date': pd.to_datetime,})
print('eBird file contains {} records'.format(len(eBird_df)))

#Drop all rows where eBird category is not species'
filtered_df = eBird_df.query("eBird_category == 'species' | eBird_category.isnull()", engine='python')
print('eBird file contains {} species records'.format(len(filtered_df)))


bouOrder_df = pd.read_csv(args.birdtrack_bou_order_file_path)
print('Birdtrack BOU Sequence file read')

sheetname = 'Records#1'
birdTrack_df = pd.read_excel(args.birdtrack_file_path, sheet_name=sheetname, converters= {'Date': pd.to_datetime, 'dayfirst': True})
print('Birdtrack export file to be merged into already contains {} records'.format(len(birdTrack_df)))

btoSpeciesCode = ''
uncertaintyRadius = ''
geometryType = ''
pinpoint = ''
userId = 'eBird'
userName = 'eBird'
endTime = ''
plumage = ''
breedingCodeDict = {'NY' : '13',
                    'NE' : '15',
                    'FS' : '14',
                    'FY' : '14',
                    'CF' : '14',
                    'FL' : '12',
                    'ON' : '13',
                    'UN' : '11',
                    'DD' : '07',
                    'NB' : '09',
                    'CN' : '09',
                    'PE' : '08',
                    'B' : '09',
                    'A' : '07',
                    'N' : '06',
                    'C' : '05',
                    'T' : '04',
                    'P' : '03',
                    'M' : '02',
                    'S7' : '02',
                    'S' : '02',
                    'H' : '03',
                    'F' : '00'}
breedingDetails = ''
remarkable = ''
habitatNotes = ''
flight = ''
activity = ''
source = 'eBird'
createdDate = ''
obsID = ''
completeList = 'N'
geometry = ''

# Loop through the eBird dataframe extracting required data and add rows to the BirdTrack dataframe
for index, row in filtered_df.iterrows():
    print('Processing ebird row {}'.format(index + 1), end='\r')
    scientificName = row['scientific_name']

    # Lookup BOU Order
    bou_row = bouOrder_df.query("LATIN_NAME == @scientificName")
    if  len(bou_row) > 0:
        bouOrder = bou_row.iloc[0]['BOU_ORDER']
    else:
        print('Cannot find BOU Order for scientific name {}'.format(scientificName))
    # Change X to Present
    if row['observation_count'] == 'X':
       count = 'Present'
    else:
        count = row['observation_count']
    
    # Convert start date string to datetime
    obsDate = datetime.strptime(row['observation_date'], '%Y/%m/%d')

    # Strip seconds from the time string
    if pd.isna(row['time_observations_started']):
        startTime = ''
    else:
        timeTokens = str(row['time_observations_started']).split(':')
        startTime = timeTokens[0] + ':' + timeTokens[1]

    # Concatenate any values in behaviour code and age/sex into comments
    if pd.isna(row['species_comments']):
        comment = ''
    elif row['species_comments'].isnumeric():
        comment = str(row['species_comments'])
    else:
        comment = row['species_comments']
    if pd.notna(row['behavior_code']):
        if comment:
            comment += '; '
        comment += 'Behaviour Code={}'.format(row['behavior_code'])
    if pd.notna(row['age_sex']):
        if comment:
            comment += '; '
        comment += 'Age/Sex={}'.format(row['age_sex'])

    # Translate breeding code
    if pd.notna(row['breeding_code']):
        breedingCode = str(row['breeding_code']).translate(breedingCodeDict)
    else:
        breedingCode = ''

    # use BBRC in eBird as a proxy for sensitive
    if row['BBRC_species'] == True:
        sensitive = 'Y'
    else:
        sensitive = ''
    
    birdTrack_df.loc[len(birdTrack_df.index)] = [btoSpeciesCode, bouOrder, row['species'], row['scientific_name'],
                                                 row['locality'], row['os1km'], uncertaintyRadius, geometryType,
                                                 row['latitude'], row['longitude'], pinpoint, row['full_name'],
                                                 userId, userName, obsDate, startTime,
                                                 endTime, count, comment, plumage, breedingCode, breedingDetails,
                                                 sensitive, remarkable, habitatNotes, flight, activity, source,
                                                 createdDate, obsID, completeList, geometry]

print('Updated BirdTrack export file now contains {} records'.format(len(birdTrack_df)))
# Overwrite the sheet  
with pd.ExcelWriter(args.birdtrack_file_path, engine="openpyxl", mode="a", if_sheet_exists="replace", 
                    date_format='DD/MM/YYYY', datetime_format='HH:MM') as writer:
    birdTrack_df.to_excel(writer, 'Records#1', index=False)

runTime = time.time() - start_time
convert = time.strftime("%H:%M:%S", time.gmtime(runTime))
print('Execution took {}'.format(convert))