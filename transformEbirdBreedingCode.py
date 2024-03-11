# take an input spreadsheet that contains eBird data with untransformed breeding codes 
# and transform them to BirdTrack breeding codes

import argparse
import pandas as pd
import datetime
from datetime import date, datetime
import shutil
import time

breedingCodeDict = {'NY' : '16',
                    'NE' : '15',
                    'FS' : '14',
                    'FY' : '14',
                    'CF' : '14',
                    'FL' : '12',
                    'ON' : '13',
                    'UN' : '11',
                    'DD' : '09',
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

eBirdCodes = ['NY', 'NE', 'FS', 'FY', 'CF', 'FL', 'ON', 'UN', 'DD',
             'NB', 'CN', 'PE', 'B', 'A', 'N', 'C', 'T', 'P', 'M', 'S7', 'S', 'H', 'F']

def transformCode(breedingCode):
    if breedingCode in eBirdCodes:
        return breedingCodeDict[breedingCode]

start_time = time.time()

parser = argparse.ArgumentParser(description="Transform eBird breeding codes to BirdTrack codes",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, 
                    help='Filepath to the input Excel file to be updated')

args = parser.parse_args()
config = vars(args)

# Save a backup of the original file
backup = args.file_path.replace('.xlsx', '.bak')
shutil.copyfile(args.file_path, backup)
print('Backup copy of input data saved as {}'.format(backup))

sheetname = 'Records#1'
df = pd.read_excel(args.file_path, sheet_name=sheetname, converters= {'Date': pd.to_datetime, 'dayfirst': True})

df['Breeding status'] = df['Breeding status'].map(transformCode)

# Overwrite the sheet  
with pd.ExcelWriter(args.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace", 
                    date_format='DD/MM/YYYY', datetime_format='HH:MM') as writer:
    df.to_excel(writer, 'Records#1', index=False)

runTime = time.time() - start_time
convert = time.strftime("%H:%M:%S", time.gmtime(runTime))
print('Execution took {}'.format(convert))