import argparse
import pandas as pd
import datetime
from datetime import date, datetime

#defining function
def set_year(date_str):
  date_format = '%d/%m/%Y'
  date = datetime.strptime(date_str, date_format)
  return date.year

parser = argparse.ArgumentParser(description="Add a year column to a CSV file",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the csv to be processed')
parser.add_argument("-c", "--date_column", type=str, required=True, help="column containing the date")

args = parser.parse_args()
config = vars(args)

df = pd.read_csv(args.file_path)
df['Year'] = df[args.date_column].map(set_year)
df.to_csv(args.file_path, index=False)