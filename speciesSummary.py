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
import re

speciesToIgnore = ['Chiffchaff/Willow Warbler',
                   'Common/Arctic Tern',
                   'Common/Lesser Redpoll',
                   'Domestic Greylag Goose',
                   "Harris's Hawk",
                   'Indian Peafowl',
                   'Long-eared/Short-eared Owl',
                   'Domestic Mallard',
                   'Ruddy Shelduck',
                   'South African Shelduck']
# Will also ignore Unidentified anything!

speciesToChange = {
    'Black Guillemot (arcticus)'            :   'Black Guillemot',
    'Black-tailed Godwit (islandica)'       :	'Black-tailed Godwit',
    'Blackbird (merula)'                    :	'Blackbird',
    'Blue Tit (obscurus)'                   :	'Blue Tit',
    'Brent Goose (Light-bellied - hrota)'   :	'Brent Goose',
    'Bullfinch (pyrrhula)'                  :	'Bullfinch',
    'Buzzard (buteo)'                       :	'Buzzard',
    'Carrion Crow (corone)'                 :	'Carrion Crow',
    'Chaffinch (coelebs)'                   :	'Chaffinch',
    'Chaffinch (gengleri)'                  :	'Chaffinch',
    'Common Crossbill (curvirostra)'        :	'Common Crossbill',
    'Common Gull (canus)'                   :	'Common Gull',
    'Coot (atra)'                           :	'Coot',
    'Cormorant (Continental - sinensis)'    :	'Cormorant',
    'Cormorant (Nominate - carbo)'          :	'Cormorant',
    'Cuckoo (canorus)'                      :	'Cuckoo',
    'Dunlin (alpina)'                       :	'Dunlin',
    'Dunnock (occidentalis)'                :	'Dunnock',
    'Eider (mollissima)'                    :	'Eider',
    'Garden Warbler (borin)'                :	'Garden Warbler',
    'Goldeneye (clangula)'                  :	'Goldeneye',
    'Goldfinch (britannica)'                :	'Goldfinch',
    'Goosander (merganser)'                 :	'Goosander',
    'Great Spotted Woodpecker (anglicus)'   :	'Great Spotted Woodpecker',
    'Great Tit (newtoni)'                   :	'Great Tit',
    'Grey Heron (cinerea)'                  :	'Grey Heron',
    'Greylag Goose (anser)'                 :	'Greylag Goose',
    'House Sparrow (domesticus)'            :	'House Sparrow',
    'Jackdaw (spermologus)'                 :	'Jackdaw',
    'Kestrel (tinnunculus)'                 :	'Kestrel',
    'Lesser Black-backed Gull (graellsii)'  :	'Lesser Black-backed Gull',
    'Linnet (cannabina)'                    :	'Linnet',
    'Long-tailed Tit (rosaceus)'            :	'Long-tailed Tit',
    'Magpie (pica)'                         :	'Magpie',
    'Mallard (platyrhynchos)'               :	'Mallard',
    'Moorhen (chloropus)'                   :	'Moorhen',
    'Nuthatch (caesia)'                     :	'Nuthatch',
    'Oystercatcher (ostralegus)'            :	'Oystercatcher',
    'Peregrine (peregrinus)'                :	'Peregrine',
    'Red Grouse (scotica)'                  :	'Red Grouse',
    'Robin (melophilus)'                    :	'Robin',
    'Rock Dove'                             :	'Feral Pigeon',
    'Rook (frugilegus)'                     :	'Rook',
    'Sand Martin (riparia)'                 :	'Sand Martin',
    'Shag (aristotelis)'                    :	'Shag',
    'Snipe (gallinago)'                     :	'Snipe',
    'Starling (vulgaris)'                   :	'Starling',
    'Swallow (rustica)'                     :	'Swallow',
    'Swift (apus)'                          :	'Swift',
    'Treecreeper (britannica)'              :	'Treecreeper',
    'Willow Warbler (trochilus)'            :	'Willow Warbler',
    'Woodpigeon (palumbus)'                 :	'Woodpigeon',
    'Yellow-legged Gull (michahellis)'      :	'Yellow-legged Gull'}

def transformSpecies(species):
    if species in speciesToChange:
        return speciesToChange[species]
    else:
        return species

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
parser.add_argument("-f", "--output_file_path", type=str, required=True, help='filepath for output Excel file')

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

# Remove non-species and change defined sub-species to main species
# Firstly drop all rows for species begining Unidentified
print('Removing Unidentified Species')
df = df.drop(df[df['Species'].str.startswith('Unidentified')].index)

# Then drop the species to ignore - generally unspecific ones
print('Removing unspecific species')
df = df[~(df["Species"].isin(speciesToIgnore))]

#Finally transform all rows for sub-species that should be consolidated with
# the main species
print('Fixing incorrect subspecies')
df['Species'] = df['Species'].map(transformSpecies)

# - Total number of records
totalRecords = len(df)
summary = {'Summary': ['Input file contains {} records'.format(totalRecords)]}

# - Total number of species observed
totalSpecies = df[args.speciesName_column].nunique()
summary['Summary'].append('{} unique species names (NB sub species will be counted as different species and includes species beginning unidentified)'.format(totalSpecies))

# - Total number of discrete place names where observations were made
totalPlaces = df[args.place_column].nunique()
summary['Summary'].append('{} unique place names'.format(totalPlaces))

# - Total number of observers
totalObservers = df[args.observer_column].nunique()
summary['Summary'].append('{} unique observers'.format(totalObservers))

# - Total number of days in the year when species observations were made
totalDays = df[args.date_column].nunique()
summary['Summary'].append('{} unique days on which observations were made'.format(totalDays))

# - Total count for all species
totalCount = df[args.count_column].sum()
summary['Summary'].append('{} individual birds (At least)'.format(totalCount))

# - Total number of 1km squares where observations were logged
totalSquares = df[args.gridRef_column].nunique()
summary['Summary'].append('In {} unique 1km squares'.format(totalSquares))

# - Overall % coverage of 1km squares
pcentCoverage = totalSquares/int(args.total_squares) * 100
summary['Summary'].append('Overall {}% of 1km squares had observations recorded in them'.format(pcentCoverage))

summary_df = pd.DataFrame(summary)

# sort the input file by Species and Date
df.sort_values(by=[args.speciesName_column, args.date_column], inplace=True)
print('Input file sorted')

# get the list of species in the report
speciesList = df.Species.unique()

# create the output dataframe
species_df = pd.DataFrame(columns=['Species', 'Records', 'Places', 'Observers', 'Days', 'Total count', '1km squares', '% 1km Squares'])
calendar_df = pd.DataFrame(columns=['Species', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

for index in range(len(speciesList)):
    print('Processing {}'.format(speciesList[index]), end='\x1b[1K\r')
    # extract the records for that Species
    species_extract_df = df[df[args.speciesName_column] == speciesList[index]]
    species_df.loc[index] = {'Species'      : speciesList[index],
                             'Records'      : len(species_extract_df),
                             'Places'       : species_extract_df[args.place_column].nunique(),
                             'Observers'    : species_extract_df[args.observer_column].nunique(),
                             'Days'         : species_extract_df[args.date_column].nunique(),
                             'Total count'  : species_extract_df[args.count_column].sum(),
                             '1km squares'  : species_extract_df[args.gridRef_column].nunique(),
                             '% 1km Squares': "{:.2f}".format(species_extract_df[args.gridRef_column].nunique()/totalSquares*100)}
    # create a dataframe that contains a count of records by month
    monthcount_df = species_extract_df.groupby(species_extract_df[args.date_column].dt.month).count().rename_axis(['Month'])[args.date_column].reset_index(name='Count')
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

    # - For summer/winter visitors earliest arrival and latest sighting
    # - For breeders number of confirmed/probable and possible breeding code observations and 
    #   number and % of 1km squares for this species in which these took place

with pd.ExcelWriter(args.output_file_path, engine="openpyxl", 
                    date_format='DD/MM/YYYY', datetime_format='HH:MM') as writer:
    summary_df.to_excel(writer, 'Summary', index=False)
    species_df.to_excel(writer, 'Species', index=False)
    calendar_df.to_excel(writer, 'Calendar', index=False)

runTime = time.time() - start_time
convert = time.strftime("%H:%M:%S", time.gmtime(runTime))
print('Execution took {}'.format(convert))