# This script takes as input a csv file or Excel spreadsheet containing data 
# exported from eBird and/or BirdTrack and outputs the following summary data:
#
# - Total number of records (species observations)
# - Total number of species observed (NB this is unique species name so sub species will be counted seperately)
# - Total number of discrete place names where observations were made (NB the same
#   place could be called multiple different things)
# - Total number of observers
# - Total number of days in the year when observations were made
# - Total count for all species (NB the same bird could be counted multiple times 
#   by different observers)
# - Total number of 1km squares where observations were logged
# 
# Then for each species the following data is output (See above for qualifications on
# places and counts):
#
# - Total number of records
# - Total number of discrete places where observations were made and % of all places
# - Total number of observers and % of all observers
# - Total number of days in the year when species observations were made and % of days for all species
# - Total count for all observations of the species and % of total count for all species
# - Total and % of observed 1km squares
# - For summer/winter visitors earliest arrival and latest sighting
# - For breeders number of confirmed/probable and possible breeding code observations and 
#   number and % of 1km squares for this species in which these took place
#
# As input the script can take the following arguments - mandatory unless stated:
#
# - The file path to the input file
# - The name of the sheet containing the data (Excel files only)
# - The column containing the Species name
# - The column containing the Place name
# - The column containing the observer name
# - The column containing the date the observation was made
# - The column containing the count as a number
# - The column containing the 1km Grid Reference
# - The column containing the BirdTrack breeding code
# - The total number of 1km squares for the area the records relate to (optional)

# TODO investigate why there are fewer 1km squares identified by Python than the QGIS Biological Reporting Tool

import argparse
import pandas as pd
from datetime import date, datetime as dt
import pathlib
import sys
import time

start_time = time.time()

parser = argparse.ArgumentParser(description="Generate summary information from Bird Observations files",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-i", "--input_file_path", type=str, required=True, help='filepath to the csv or Excel file to be processed')
parser.add_argument("-s", "--sheet_name", type=str, required=False, help='name of the sheet to be updated')
parser.add_argument("-n", "--speciesName_column", type=str, required=True, help="column containing the species name")
parser.add_argument("-p", "--place_column", type=str, required=True, help="column containing the place name")
parser.add_argument("-o", "--observer_column", type=str, required=True, help="column containing the observer name")
parser.add_argument("-d", "--date_column", type=str, required=True, help="column containing the date")
parser.add_argument("-c", "--count_column", type=str, required=True, help="column containing the numerical count")
parser.add_argument("-g", "--gridRef_column", type=str, required=True, help="column containing the 1km grid ref")
parser.add_argument("-b", "--breedingCode_column", type=str, required=True, help="column containing the breeding code")
parser.add_argument("-t", "--total_squares", type=str, required=False, help='total number of 1km squares for the area the records relate to')
parser.add_argument("-f", "--output_file_path", type=str, required=True, help='filepath for output csv or Excel file')

args = parser.parse_args()
config = vars(args)

if pathlib.Path(args.input_file_path).suffix == '.csv':
    print('Processing a csv file {}'.format(args.file_path))
    df = pd.read_csv(args.input_file_path, converters= {args.date_column: pd.to_datetime})
elif pathlib.Path(args.input_file_path).suffix == '.xlsx':
    print('Processing sheet {} in Excel file {}'.format(args.sheet_name, args.input_file_path))
    df = pd.read_excel(args.input_file_path, converters= {args.date_column: pd.to_datetime}, sheet_name=args.sheet_name)
else:
    sys.exit('Invalid file type {}'.format(args.input_file_path))

# - Total number of records
totalRecords = len(df)
print('Input file contains {} records'.format(totalRecords))

# - Total number of species observed
totalSpecies = df[args.speciesName_column].nunique()
print('{} unique species names (NB sub species will be counted as different species and includes species beginning unidentified)'.format(totalSpecies))

# - Total number of discrete place names where observations were made
totalPlaces = df[args.place_column].nunique()
print('{} unique place names'.format(totalPlaces))

# - Total number of observers
totalObservers = df[args.observer_column].nunique()
print('{} unique observers'.format(totalObservers))

# - Total number of days in the year when species observations were made
totalDays = df[args.date_column].nunique()
print('{} unique days on which observations were made'.format(totalDays))

# - Total count for all species
totalCount = df[args.count_column].sum()
print('{} individual birds (At least)'.format(totalCount))

# - Total number of 1km squares where observations were logged
totalSquares = df[args.gridRef_column].nunique()
print('In {} unique 1km squares'.format(totalSquares))

# - Overall % coverage of 1km squares
pcentCoverage = totalSquares/int(args.total_squares) * 100
print('Overall {}% of 1km squares had observations recorded in them'.format(pcentCoverage))

# sort the input file by Species and Date
df.sort_values(by=[args.speciesName_column, args.date_column], inplace=True)
print('Input file sorted')

# get the list of species in the report
speciesList = df.Species.unique()

# remove any species starting with Unidentified
speciesList = [x for x in speciesList if not x.startswith('Unidentified')]

# create the output dataframe
summary_df = pd.DataFrame(columns=['Species', 'Records', 'Places', 'Observers', 'Days', 'Total count', '1km squares', '% 1km Squares'])
calendar_df = pd.DataFrame(columns=['Species', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

for index in range(len(speciesList)):
    print('Processing {}'.format(speciesList[index]), end='\x1b[1K\r')
    # extract the records for that Species
    species_df = df[df[args.speciesName_column] == speciesList[index]]
    summary_df.loc[index] = {'Species'      : speciesList[index],
                             'Records'      : len(species_df),
                             'Places'       : species_df[args.place_column].nunique(),
                             'Observers'    : species_df[args.observer_column].nunique(),
                             'Days'         : species_df[args.date_column].nunique(),
                             'Total count'  : species_df[args.count_column].sum(),
                             '1km squares'  : species_df[args.gridRef_column].nunique(),
                             '% 1km Squares': "{:.2f}".format(species_df[args.gridRef_column].nunique()/totalSquares*100)}
    # create a dataframe that contains a count of records by month
    monthcount_df = species_df.groupby(species_df[args.date_column].dt.month).count().rename_axis(['Month'])[args.date_column].reset_index(name='Count')
    monthArray = []
    for monthInt in range(1,13):
        if monthcount_df.loc[monthcount_df.Month == monthInt].empty:
            count = 0
        else:
            count = monthcount_df.loc[monthcount_df.Month == monthInt].Count.item()
        monthArray.append(count)
    
    calendar_df.loc[index] = {'Species': speciesList[index],
                              'Jan'    : monthArray[0],
                              'Feb'    : monthArray[1],
                              'Mar'    : monthArray[2],
                              'Apr'    : monthArray[3],
                              'May'    : monthArray[4],
                              'Jun'    : monthArray[5],
                              'Jul'    : monthArray[6],
                              'Aug'    : monthArray[7],
                              'Sep'    : monthArray[8],
                              'Oct'    : monthArray[9],
                              'Nov'    : monthArray[10],
                              'Dec'    : monthArray[11]}
    
print(calendar_df)
 

    # - For summer/winter visitors earliest arrival and latest sighting
    # - For breeders number of confirmed/probable and possible breeding code observations and 
    #   number and % of 1km squares for this species in which these took place

# summary_df.to_csv(args.output_file_path, index=False)

runTime = time.time() - start_time
convert = time.strftime("%H:%M:%S", time.gmtime(runTime))
print('Execution took {}'.format(convert))