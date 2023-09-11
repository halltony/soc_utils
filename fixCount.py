import argparse
import pandas as pd

#defining function
def fix_count(count_str):
# Strip out any space characters
    count_str = count_str.replace(' ','')
# Strip out any terminating plus signs
    count_str = count_str.rstrip('+')
# Strip out any leading c characters
    count_str = count_str.lstrip('c')
# If the column is empty, contains only spaces or the word present then set count to 1
    if (len(count_str) == 0 or count_str.lower() == 'present'):
        count = 1
# Otherwise convert nuumeric string to a number
    else:
        count = int(count_str)
    return count

parser = argparse.ArgumentParser(description="convert contents of count column in a CSV file to number",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='filepath to the csv to be processed')
parser.add_argument("-c", "--count_column", type=str, required=True, help="column containing the count")

args = parser.parse_args()
config = vars(args)

df = pd.read_csv(args.file_path)
df[args.count_column] = df[args.count_column].map(fix_count)
df.to_csv(args.file_path, index=False)