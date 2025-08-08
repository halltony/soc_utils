library(tidyverse)
library(readxl)
library(Hmisc)
library(psych)
library(dplyr)                                                 
library(readr)   
# create df and csv from 1st sheet of Excel exported from BirdTrack
read_then_csv <- function(sheet, path) {
  pathbase <- path %>%
    basename() %>%
    tools::file_path_sans_ext()
  path %>%
    read_excel(sheet = sheet) %>% 
    write_csv(paste0(pathbase, "-", sheet, ".csv"))
}

path = '/Users/Tony/Downloads/bt.xlsx'

# This creates the csv files for each sheet in the spreadsheet
path %>%
  excel_sheets() %>%
  set_names() %>%
  map(read_then_csv, path = path)

# Load the csv created from the first sheet
species_df = read_csv('bt-Summary.csv')

# Drop all but the first column
species_df2 <- species_df[, -2:-10]

# Fix the column name
names(species_df2) <- str_replace_all(names(species_df2), c(' ' = '_'))

# Remove rows containing round or square braces
species_df3 <- subset(species_df2, !grepl('\\(', Selected_Species))
species_df4 <- subset(species_df3, !grepl('\\[', Selected_Species))
# write out the species list

write_csv(species_df4, file = 'species_list.csv', col_names = TRUE)
