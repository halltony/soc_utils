#!/Users/Tony/.pyenv/shims/python

# TODO

from docx import Document
from docx.shared import Inches
from docx.shared import RGBColor

import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description="Create Bird Report species headings from a reformated Birdtrack export",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='Filepath to the Excel file to be processed')
parser.add_argument("-d", "--data_file_path", type=str, required=True, help='Filepath to the csv file containing reference data')

args = parser.parse_args()
config = vars(args)

document = Document()

df = pd.read_excel(args.file_path).fillna(value = 0)
reference_df = pd.read_csv(args.data_file_path)

#get the list of species in the report
speciesList = df.Species.unique()

for species in speciesList:
    print(species)
    species_df = df[df['Species'] == species]
    scientificName = species_df['Scientific name'].unique()
    row = reference_df.query("Scientific_name == @scientificName[0]")
    if  len(row) > 0:
        bou_cat = row.iloc[0]['BOU_category']
        bto_code = row.iloc[0]['BTO_Code']
        cons_stat = row.iloc[0]['Scotland']
        p = document.add_paragraph('')
        p.add_run(species).bold = True
        p.add_run(' ')
        p.add_run(scientificName).italic = True
        p.add_run('\t\t')
        p.add_run(bou_cat)
        p.add_run('/')
        p.add_run(bto_code)
        p.add_run('/')
        if 'Green' in cons_stat:
            p.add_run(cons_stat).font.color.rgb = RGBColor(0, 128, 0)
        elif 'Amber' in cons_stat:
            p.add_run(cons_stat).font.color.rgb = RGBColor(255, 165, 0)
        elif 'Red' in cons_stat:
            p.add_run(cons_stat).font.color.rgb = RGBColor(255, 0, 0)
        else:
            p.add_run(cons_stat)

document.save('demo.docx')