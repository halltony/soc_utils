# ==============================================================================
# combine_excel_to_csv.R
#
# Combines all Excel spreadsheets (.xlsx / .xls) in a folder into a single CSV.
# Data tables are expected to start on ROW 2 (row 1 is the header).
#
# Requirements:
#   install.packages(c("readxl", "dplyr", "readr"))
# ==============================================================================

library(readxl)
library(dplyr)
library(readr)

# ------------------------------------------------------------------------------
# CONFIGURATION — edit these as needed
# ------------------------------------------------------------------------------

INPUT_FOLDER  <- "/Users/Tony/Desktop/CBRP"   # Folder containing .xlsx/.xls files
OUTPUT_FILE   <- "/Users/Tony/Desktop/CBRP/combined_output.csv"          # Name/path of the output CSV
SHEET_INDEX   <- 1                              # Which sheet to read (1 = first sheet)
# Use a sheet name string if preferred, e.g. "Sheet1"

# Set to TRUE to add a column recording the source filename for each row
ADD_SOURCE_COLUMN <- TRUE

# ------------------------------------------------------------------------------
# MAIN SCRIPT
# ------------------------------------------------------------------------------

# Find all Excel files in the folder
excel_files <- list.files(
  path       = INPUT_FOLDER,
  pattern    = "\\.(xlsx|xls)$",
  full.names = TRUE,
  ignore.case = TRUE
)

if (length(excel_files) == 0) {
  stop("No Excel files found in: ", INPUT_FOLDER)
}

message("Found ", length(excel_files), " Excel file(s). Starting import...\n")

# Read each file and collect into a list
all_tables <- lapply(excel_files, function(file_path) {
  
  file_name <- basename(file_path)
  message("  Reading: ", file_name)
  
  tryCatch({
    df <- read_excel(
      path  = file_path,
      sheet = SHEET_INDEX,
      skip  = 1,          # Skip row 1; row 2 becomes the first data row
      col_names = TRUE    # Treat the first non-skipped row as column headers
    )
    
    # Optionally tag each row with its source file
    if (ADD_SOURCE_COLUMN) {
      df <- df %>% mutate(source_file = file_name, .before = 1)
    }
    
    df
    
  }, error = function(e) {
    warning("  Could not read '", file_name, "': ", conditionMessage(e))
    NULL   # Return NULL so this file is skipped gracefully
  })
})

# Remove any NULLs (files that failed to load)
all_tables <- Filter(Negate(is.null), all_tables)

if (length(all_tables) == 0) {
  stop("No data could be loaded from the Excel files.")
}

# Normalize column types before combining:
# Different files may read the same column as different types (e.g. character vs double).
# Strategy: coerce every column to character first, bind, then convert columns
# that look fully numeric back to numeric.
all_tables <- lapply(all_tables, function(df) {
  df %>% mutate(across(everything(), as.character))
})

combined_df <- bind_rows(all_tables)

# Restore numeric columns: if every non-NA value in a column can be parsed as a
# number, convert it back to double.
combined_df <- combined_df %>%
  mutate(across(
    everything(),
    ~ if (all(is.na(.) | !is.na(suppressWarnings(as.numeric(.))))) {
      suppressWarnings(as.numeric(.))
    } else {
      .
    }
  ))

message("\nCombined table dimensions: ",
        nrow(combined_df), " rows x ", ncol(combined_df), " columns")

# Write to CSV
write_csv(combined_df, OUTPUT_FILE)

message("Output saved to: ", normalizePath(OUTPUT_FILE, mustWork = FALSE))