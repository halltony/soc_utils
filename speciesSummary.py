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
                   'Domestic Mallard',
                   "Harris's Hawk",
                   'Hybrid duck',
                   'Hybrid goose',
                   'Indian Peafowl',
                   'Long-eared/Short-eared Owl',
                   'Muscovy Duck',
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

# AKA Summer Visitors
summerVisitors = ['Arctic Tern', 'Blackcap', 'Blackcap (atricapilla)', 'Chiffchaff',
                  'Common Sandpiper', 'Common Tern', 'Cuckoo', 'Dotterel', 'Gannet',
                  'Garden Warbler', 'Garganey', 'Grasshopper Warbler', 'House Martin',
                  'Lesser Whitethroat', 'Little Ringed Plover', 'Manx Shearwater',
                  'Marsh Harrier', 'Osprey', 'Pied Flycatcher', 'Quail', 'Redstart',
                  'Reed Warbler', 'Ring Ouzel', 'Sand Martin', 'Sandwich Tern',
                  'Sedge Warbler', 'Spotted Crake', 'Spotted Flycatcher', 'Swallow',
                  'Swift', 'Tree Pipit', 'Wheatear', 'Wheatear (Greenland - leucorhoa)',
                  'Whimbrel', 'Whinchat', 'White Wagtail', 'Whitethroat', 'Willow Warbler',
                  'Willow Warbler (trochilus)', 'Wood Sandpiper', 'Wood Warbler',
                  'Yellow Wagtail', 'Yellow Wagtail (British - flavissima)']

winterVisitors = ['Barnacle Goose', "Bewick's Swan", 'Brambling', 'Brent Goose',
                  'Brent Goose (Light-bellied - hrota)', 'Chiffchaff (Siberian - tristis)',
                  'Fieldfare', 'Glaucous Gull  ', 'Goldeneye', 'Great Grey Shrike',
                  'Greenshank', 'Iceland Gull', 'Jack Snipe', 'Long-tailed Duck',
                  'Pink-footed Goose', 'Pintail', 'Redwing', 'Slavonian Grebe', 'Smew',
                  'Snow Bunting', 'Taiga Bean Goose', 'Taiga/Tundra Bean Goose',
                  'Tundra Bean Goose', 'Turnstone', 'Waxwing', 'White Wagtail (alba)',
                  'White-fronted Goose', 'White-fronted Goose (European - albifrons)',
                  'White-fronted Goose (Greenland - flavirostris)', 'Whooper Swan']

def transformSpecies(species):
    if species in speciesToChange:
        return speciesToChange[species]
    else:
        return species

start_time = time.time()

parser = argparse.ArgumentParser(description='Generate summary information from Bird Observations files',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-i', '--input_file_path', type=str, required=True, help='filepath to the csv or Excel file to be processed')
parser.add_argument('-s', '--sheet_name', type=str, required=False, default='Records#1', help='name of the sheet to be updated')
parser.add_argument('-u', '--bouOrder_column', type=str, required=False, default='BOU order', help='column containing the BOU Order for each species')
parser.add_argument('-n', '--speciesName_column', type=str, required=False, default='Species', help='column containing the species name')
parser.add_argument('-p', '--place_column', type=str, required=False, default='Place', help='column containing the place name')
parser.add_argument('-o', '--observer_column', type=str, required=False, default='Observer name', help='column containing the observer name')
parser.add_argument('-d', '--date_column', type=str, required=False, default='Date', help='column containing the date')
parser.add_argument('-c', '--count_column', type=str, required=False, default='Numerical count', help='column containing the numerical count')
parser.add_argument('-g', '--gridRef_column', type=str, required=False, default='1km Grid Ref', help='column containing the 1km grid ref')
parser.add_argument('-b', '--breedingCode_column', type=str, required=False, default='Decoded Breeding Status', help='column containing the decoded breeding code')
parser.add_argument('-t', '--total_squares', type=str, required=True, help='total number of 1km squares for the area the records relate to')
parser.add_argument('-f', '--output_file_path', type=str, required=False, default='speciesSummary.xlsx', help='filepath for output Excel file')

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
df = df[~(df['Species'].isin(speciesToIgnore))]

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
df.sort_values(by=[args.bouOrder_column, args.date_column], inplace=True)
print('Input file sorted')

# get the list of species in the report
speciesList = df.Species.unique()

# create the output dataframe
species_df = pd.DataFrame(columns=['Species', 'Records', 'Places', 'Observers', 'Days', 'Total count', '1km squares', '% 1km Squares'])
calendar_df = pd.DataFrame(columns=['Species', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
breeding_df = pd.DataFrame(columns=['Species', 'Possible Records', 'Possible Counts', 'Possible Squares', 'Possible Squares %', 'Earliest Possible', 'Latest Possible',
                                    'Probable Records', 'Probable Counts', 'Probable Squares', 'Probable Squares %', 'Earliest Probable', 'Latest Probable',
                                    'Confirmed Records', 'Confirmed Counts', 'Confirmed Squares', 'Confirmed Squares %', 'Earliest Confirmed', 'Latest Confirmed'])
breeding_df['Earliest Possible'] = pd.to_datetime(breeding_df['Earliest Possible'])
breeding_df['Earliest Probable'] = pd.to_datetime(breeding_df['Earliest Probable'])
breeding_df['Earliest Confirmed'] = pd.to_datetime(breeding_df['Earliest Confirmed'])
breeding_df['Latest Possible'] = pd.to_datetime(breeding_df['Latest Possible'])
breeding_df['Latest Probable'] = pd.to_datetime(breeding_df['Latest Probable'])
breeding_df['Latest Confirmed'] = pd.to_datetime(breeding_df['Latest Confirmed'])

summerVistors_df = pd.DataFrame(columns=['Species', 'Earliest', 'Latest'])
winterVisitors_df = pd.DataFrame(columns=['Species', 'Earliest', 'Latest'])
breederIndex = 0
summerVisitorIndex = 0
winterVisitorIndex = 0

for index in range(len(speciesList)):
    print('Processing {}'.format(speciesList[index]))
    # extract the records for that Species
    species_extract_df = df[df[args.speciesName_column] == speciesList[index]]
    species_df.loc[index] = {'Species'      : speciesList[index],
                             'Records'      : len(species_extract_df),
                             'Places'       : species_extract_df[args.place_column].nunique(),
                             'Observers'    : species_extract_df[args.observer_column].nunique(),
                             'Days'         : species_extract_df[args.date_column].nunique(),
                             'Total count'  : species_extract_df[args.count_column].sum(),
                             '1km squares'  : species_extract_df[args.gridRef_column].nunique(),
                             '% 1km Squares': '{:.2f}'.format(species_extract_df[args.gridRef_column].nunique()/totalSquares*100)}
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
    breedingMatches = ['Possible breeder', 'Probable breeding', 'Confirmed breeding']
    if any(x in species_extract_df[args.breedingCode_column].values.tolist() for x in breedingMatches):
        print('Species has breeding data')
        possibleRecords = possibleCounts = possibleSquares = possibleSquaresPcent = 0
        earliestPossible = latestPossible = date.min
        probableRecords = probableCounts = probableSquares = probableSquaresPcent= 0
        earliestProbable = latestProbable = date.min
        confirmedRecords = confirmedCounts = confirmedSquares = confirmnedSquaresPcent= 0
        earliestConfirmed = latestConfirmed = date.min
        breeding_df.loc[breederIndex] = {'Species': speciesList[index]}
        if 'Possible breeder' in species_extract_df[args.breedingCode_column].values.tolist():
            possibleBreeder_df = species_extract_df[species_extract_df[args.breedingCode_column] == 'Possible breeder']
            possibleRecords = len(possibleBreeder_df)
            possibleCounts = possibleBreeder_df[args.count_column].sum()
            possibleSquares = possibleBreeder_df[args.gridRef_column].nunique()
            possibleSquaresPcent = possibleBreeder_df[args.gridRef_column].nunique() / totalSquares * 100
            earliestPossible = possibleBreeder_df[args.date_column].min()
            latestPossible = possibleBreeder_df[args.date_column].max()
        if 'Probable breeding' in species_extract_df[args.breedingCode_column].values.tolist():
            probableBreeder_df = species_extract_df[species_extract_df[args.breedingCode_column] == 'Probable breeding']  
            probableRecords = len(probableBreeder_df)
            probableCounts = probableBreeder_df[args.count_column].sum()
            probableSquares = probableBreeder_df[args.gridRef_column].nunique()
            probableSquaresPcent = probableBreeder_df[args.gridRef_column].nunique() / totalSquares * 100
            earliestProbable = probableBreeder_df[args.date_column].min()
            latestProbable = probableBreeder_df[args.date_column].max()
        if 'Confirmed breeding' in species_extract_df[args.breedingCode_column].values.tolist():
            confirmedBreeder_df = species_extract_df[species_extract_df[args.breedingCode_column] == 'Confirmed breeding']  
            confirmedRecords = len(confirmedBreeder_df)
            confirmedCounts = confirmedBreeder_df[args.count_column].sum()
            confirmedSquares = confirmedBreeder_df[args.gridRef_column].nunique()
            confirmnedSquaresPcent = confirmedBreeder_df[args.gridRef_column].nunique() / totalSquares * 100
            earliestConfirmed = confirmedBreeder_df[args.date_column].min()
            latestConfirmed = confirmedBreeder_df[args.date_column].max()        
        breeding_df.loc[breederIndex] = {'Species'              : speciesList[index],
                                         'Possible Records'     : possibleRecords,
                                         'Possible Counts'      : possibleCounts,
                                         'Possible Squares'     : possibleSquares,
                                         'Possible Squares %'   : possibleSquaresPcent,
                                         'Earliest Possible'    : earliestPossible,
                                         'Latest Possible'      : latestPossible,
                                         'Probable Records'     : probableRecords,
                                         'Probable Counts'      : probableCounts,
                                         'Probable Squares'     : probableSquares,
                                         'Probable Squares %'   : probableSquaresPcent,
                                         'Earliest Probable'    : earliestProbable,
                                         'Latest Probable'      : latestProbable,
                                         'Confirmed Records'    : confirmedRecords,
                                         'Confirmed Counts'     : confirmedCounts,
                                         'Confirmed Squares'    : confirmedSquares,
                                         'Confirmed Squares %'  : confirmnedSquaresPcent,
                                         'Earliest Confirmed'   : earliestConfirmed,
                                         'Latest Confirmed'     : latestConfirmed}
        breederIndex += 1

    # populate the summer visitors dataframe
    if speciesList[index] in summerVisitors:
        summerVistors_df.loc[summerVisitorIndex] = {'Species' : speciesList[index],
                                                    'Earliest' : species_extract_df[args.date_column].min(),
                                                    'Latest'   : species_extract_df[args.date_column].max()}
        summerVisitorIndex += 1
    if speciesList[index] in winterVisitors:
        janToJun_df = species_extract_df[species_extract_df[args.date_column].dt.month < 7]
        julToDec_df = species_extract_df[species_extract_df[args.date_column].dt.month > 6]
        if len(julToDec_df) > 0:
            earliestWinter = julToDec_df[args.date_column].min()
        else:
            earliestWinter = date.min
        if len(janToJun_df) > 0:
            latestWinter = janToJun_df[args.date_column].max()
        else:
            latestWinter = date.min
        winterVisitors_df.loc[winterVisitorIndex] = {'Species' : speciesList[index],
                                                    'Earliest' : earliestWinter,
                                                    'Latest'   : latestWinter}
        winterVisitorIndex += 1

with pd.ExcelWriter(args.output_file_path, engine='openpyxl', 
                    date_format='DD/MM/YYYY') as writer:
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    species_df.to_excel(writer, sheet_name='Species', index=False)
    calendar_df.to_excel(writer, sheet_name='Calendar', index=False)
    breeding_df.to_excel(writer, sheet_name='Breeding', index=False)
    summerVistors_df.to_excel(writer, sheet_name='Summer Visitors', index=False)
    winterVisitors_df.to_excel(writer, sheet_name='Winter Visitors', index=False)

runTime = time.time() - start_time
convert = time.strftime('%H:%M:%S', time.gmtime(runTime))
print('Execution took {}'.format(convert))