# soc_utils
Utility scripts for manipulating bird observation data

1.  addSeason.py - this will take as input a csv filepath and column name that contains a date string in the format DD/MM/CCYY.  It will insert a column after the supplied column contain a season name based on the astronomically defined seasons using the pyephem package.

2.  reformatBirdtrack.py - this takes as input an excel spreadsheet that has been exported from BirdTrack.  The script creates a backup copy of the file and then reformats it to remove columns that are not needed and adds a Season column.  The amended file can be used as input to the createARFiles.py script below.

3.  createARFiles.py - this takes as input a reformated Birdtrack export in excel format and a reference file containing BOU Categories, BTO Species Codes and Scottish Conservation statuses.  It produces a file for each discrete species in an output folder that contains a formated header for the species and seasonal observation tables constructed from the Birdtrack data.

4.  addYear.py - a simple utility to add a year column to a csv file based on the value in a specified date column.

5.  analysis.py - can be used to provide some summary information on a Birtdtrack export in excel format.  It provides the total number of species, the total number of records for all species and then the number of records for each species present.

6. createWordDoc.py - original standalone logic to create individual seasonal observation tables for each species.  This has been merged with createSpeciesHeadings.py to create createARFiles.py

7.  dropColumn.py -  a standalone utility that can be used to remove unrequired columns from arbitrary csv filers

8. fixCount.py - a standalone utility that can be used to ensure that the count field in an observation spreadsheet contains a numerical value.  i.e. convert N+, Present cN to a numeric.

9.  reformatRSPB.py - a standalone script to reformat observation data provided by the RSPB for the Clyde region into a format that can be imported to Birdtrack retaining as much useful data as is possible.

10.  mergeFiles.py - a script that takes the output from createARFiles.py and identifies matches between the word documents and the folder structure provided by the BTO.  The script takes as input two paths - the first is the location of the BTO output species folder amd the second is the location of the output from the createARFiles script.  Currently it simply outputs any files that cannot be matched to a folder in the BTO annual report pack.  NB it assumes uncommon subspecies i.e. species containing a genus in brackets should be associated with the more common sub species folder in the BTO annual report pack
