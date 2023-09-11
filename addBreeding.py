import argparse
import pandas as pd
import numpy as np
import datetime
from datetime import date, datetime

#defining function
def set_breeding_status(breeding_code_str):
#     # Assumes the column will either be empty or contains an integer
    breeding_code = float(breeding_code_str)
    if pd.isna(breeding_code):
        breeding_status = 'Unknown'
    elif breeding_code == 0:
        breeding_status = 'Non-breeding'
    elif 0 < breeding_code < 3:
        breeding_status = 'Possible breeder'
    elif 2 < breeding_code < 10:
        breeding_status = 'Probable breeding'
    elif 9 < breeding_code < 17:
        breeding_status = 'Confirmed breeding'
    else:
        breeding_status = 'Invalid'
    return breeding_status

parser = argparse.ArgumentParser(description="Add a breeding status column to a CSV file",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the csv to be processed')
parser.add_argument("-b", "--breeding_code_column", type=str, required=True, help="column containing the breeding code")

args = parser.parse_args()
config = vars(args)

df = pd.read_csv(args.file_path, dtype=str)
df['Decoded Breeding Status'] = df[args.breeding_code_column].map(set_breeding_status)
df.to_csv(args.file_path, index=False)