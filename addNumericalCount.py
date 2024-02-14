# This script takes as input a csv or Excel file and creates a new column called
# Numerical count.  This ensures that arithmetic operations sum as summing can be
# performed on all rows that contain count data.  The following transformations are
# made on the count column which is left unchanged:
# - any space characters are removed
# - any trailing plus characters are removed
# - any leading c characters are removed
# - the word 'Present' in any case or an empty or all spaces value is converted to 1
# It requires as arguments the file path to the input file, for Excel files, 
# the sheet name to be updated and the column that contains the count value.
# The original file is overwritten.

import argparse
import pandas as pd
import pathlib
import sys

#defining function
def fix_count(count):
    if not str(count).isnumeric():
    # Strip out any space characters
        count= count.replace(' ','')
    # Strip out any terminating plus signs
        count = count.rstrip('+')
    # Strip out any leading c characters
        count = count.lstrip('c')
    # If the column is empty, contains only spaces or the word present then set count to 1
        if (len(count) == 0 or count.lower() == 'present'):
            count = 1
    return int(count)

parser = argparse.ArgumentParser(description="convert contents of count column in a CSV file to number",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the csv or Excel file to be processed')
parser.add_argument("-s", "--sheet_name", type=str, required=False, help='name of the sheet to be updated')
parser.add_argument("-c", "--count_column", type=str, required=True, help="column containing the count")

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

print('Creating Numerical Column column from {}'.format(args.count_column))

df['Numerical count'] = df[args.count_column].apply(fix_count)

if pathlib.Path(args.file_path).suffix == '.csv':
    df.to_csv(args.file_path, index=False)
elif pathlib.Path(args.file_path).suffix == '.xlsx':
    with pd.ExcelWriter(args.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace", 
                    date_format='DD MMM', datetime_format='HH:MM') as writer:
        df.to_excel(writer, args.sheet_name, index=False)