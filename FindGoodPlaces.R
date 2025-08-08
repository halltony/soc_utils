library(tidyverse)
library(readxl)
library(Hmisc)
library(psych)
library(dplyr)                                                 
library(plyr)                                                  
library(readr)   
# create df and csv from contenation of 2nd and 3rd sheets of Excel exported from BirdTrack
read_then_csv <- function(sheet, path) {
  pathbase <- path %>%
    basename() %>%
    tools::file_path_sans_ext()
  path %>%
    read_excel(sheet = sheet) %>% 
    write_csv(paste0(pathbase, "-", sheet, ".csv"))
}

path = '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/All years/All records extracted 2 Nov 23.xlsx'

# This creates the csv files for each sheet in the spreadsheet
path %>%
  excel_sheets() %>%
  set_names() %>%
  map(read_then_csv, path = path)

allRecs <- list.files(path='/Users/Tony',
                      pattern = '*.csv',
                      full.names = TRUE) %>%
  lapply(read_csv) %>%
  bind_rows()

sort(table(allRecs$Place), decreasing = TRUE)[1:50]      

allRecs %>% 
  dplyr::group_by(Place) %>% 
  dplyr::summarize(speciesCount = n_distinct(Species)) %>%
  dplyr::arrange(desc(speciesCount)) %>%
  write_csv(file = 'good_places.csv')
  
