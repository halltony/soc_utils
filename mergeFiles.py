#!/Users/Tony/.pyenv/shims/python

import argparse
import pandas as pd
import shutil
import os
from string import digits
import re

parser = argparse.ArgumentParser(description="Merge Annual Report Word Files into BTO Annual Report Packs",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-b", "--bto_species_folder_path", type=str, required=True, help='Filepath to the species folder in to BTO Annual Report Pack')

parser.add_argument("-o", "--annual_report_output_folder_path", type=str, required=True, help='Filepath to the species folder in to BTO Annual Report Pack')

args = parser.parse_args()
config = vars(args)

bto_directory = os.fsencode(args.bto_species_folder_path)
output_directory = os.listdir(args.annual_report_output_folder_path)

for fname in output_directory:
    species_name = fname.rsplit( ".", 1 )[ 0 ]
    species_name = re.sub(r'\(.*\)', '', species_name)
    species_name = species_name.lstrip(digits)
    species_name = species_name.lstrip('-')
    species_name = species_name.replace('_', ' ')
    species_name = species_name.rstrip(' ')
    if species_name:
        match_found = False
        for file in os.listdir(bto_directory):
            bto_filename = os.fsdecode(file)
            if species_name in bto_filename:
                match_found = True
                # print(species_name + ' is in ' + bto_filename)
        if not match_found:
            print(species_name)