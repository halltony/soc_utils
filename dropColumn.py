import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Remove a column from a CSV file",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the csv to be processed')
parser.add_argument("-c", "--column", type=str, required=True, help="name of the column to be removed")

args = parser.parse_args()
config = vars(args)

df = pd.read_csv(args.file_path)
df = df.drop(columns=[args.column])
df.to_csv(args.file_path, index=False)