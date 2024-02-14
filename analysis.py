#!/Users/Tony/.pyenv/shims/python

import argparse
import pandas as pd
import datetime
from datetime import date, datetime

parser = argparse.ArgumentParser(description="Analyse Birdtrack and eBird Data for Annual Report",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='Filepath to the Excel file to be processed')


args = parser.parse_args()
config = vars(args)

df = pd.read_excel(args.file_path, converters= {'Date': pd.to_datetime})

print('Number of species recorded: ' + str(df['Species'].nunique()))

print('Total number of records: ' + str(df.shape[0]))

pd.set_option('display.max_rows', 300)
print('Number of records by Species')
print( df['Species'].value_counts() )