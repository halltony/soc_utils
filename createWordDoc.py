#!/Users/Tony/.pyenv/shims/python

# TODO
# Use Excel as Input
# Loop through all species
# Add Scientific Name to Species Section
# Add BOU Category, BTO short code and Conservation Status to species header
# Break observations into 3 seasonal sections
# ?Reformat as paragraph rather than table - without comments
# ?Sumarise low counts at end of seasonal section

from docx import Document
from docx.shared import Inches
import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description="Create Bird Report from Birdtrack export",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", "--file_path", type=str, required=True, help='Filepath to the Excel file to be processed')


args = parser.parse_args()
config = vars(args)

document = Document()

document.add_picture('soc-logo.png', width=Inches(1.25))

document.add_heading('SOC Clyde Annual Bird Report 2023', 0)

document.add_heading('Area covered:', level=1)
p = document.add_paragraph('The Clyde area is defined as: South Lanarkshire, '
                           'North Lanarkshire, City of Glasgow, East Renfrewshire, '
                           'Renfrewshire, Inverclyde, East Dunbartonshire, '
                           'West Dunbartonshire, Stirlingshire (Clyde/Loch '
                           'Lomond drainage areas, the Campsie Fells, and '
                           'Carron Valley Reservoir), Argyll & Bute (former '
                           'Dunbartonshire part, i.e. Loch Lomond/Clyde drainage '
                           'including east side of Loch Long to Arrochar (then '
                           'Loin Water as boundary).')

document.add_heading('Local Recorders:', level=1)
p = document.add_paragraph('''Email:    clyderecorder@the-soc.org.uk

Recorder - John Simpson 

Assistant  Recorders - Val Wilson and John Sweeney''')

df = pd.read_csv(args.file_path).fillna(value = 0)

document.add_heading('Bar Tailed Godwit:', level=2)

# Filter out the rows for Bar Tailed Godwit
# TODO replace this with loop through all discrete values in species column
btg_df = df[df['Species'] == 'Bar-tailed Godwit']

# Drop the species column
btg_df = btg_df.drop(columns=['Species'])

# Get the column names as a list
column_names_list = btg_df.columns.values.tolist()

# Create the table headings
table = document.add_table(rows=1, cols=4)
hdr_cells = table.rows[0].cells
hdr_cells[0].text = column_names_list[2]
hdr_cells[1].text = column_names_list[0]
hdr_cells[2].text = column_names_list[1]
hdr_cells[3].text = column_names_list[3]

for index, row in btg_df.iterrows():
    row_cells = table.add_row().cells
    row_cells[0].text = row['Date']
    row_cells[1].text = row['Count']
    row_cells[2].text = row['Place']
    if row['Comment'] != 0:
        row_cells[3].text = row['Comment']

document.add_page_break()

document.save('demo.docx')