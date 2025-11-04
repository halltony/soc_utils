# Load required packages
library(readxl)
library(dplyr)
library(stringr)
library(tidyr)

# List all Excel files in the working directory
files <- list.files(path = ".", pattern = "\\.xls[x]?$", full.names = TRUE)

# Function to read and clean one file
read_one <- function(file) {
  message("Reading: ", file)
  
  df <- read_excel(file, sheet = "data", col_types = "text")
  
  # Drop rows where all values are NA or empty string
  df <- df %>% filter(if_any(everything(), ~ !is.na(.) & . != ""))
  
  # Remove non-printable characters from all text columns
  df <- df %>% mutate(across(where(is.character), ~ str_replace_all(., "[^[:print:]]", "")))
  
  # Trim whitespace
  df <- df %>% mutate(across(where(is.character), str_trim))
  
  # Backfill SPECIES if needed (handles merged cells)
  if ("SPECIES" %in% names(df)) {
    df <- df %>% fill(SPECIES, .direction = "down")
  }
  
  # Remove rows where SPECIES begins with "No longer SBRC"
  df <- df %>% filter(!str_starts(SPECIES, "No longer SBRC"))
  
  # Add provenance
  df <- df %>% mutate(source_file = basename(file))
  
  return(df)
}

# Read and combine all files
all_data <- bind_rows(lapply(files, read_one))

# --- Keep only columns up to YEAR ---
if ("YEAR" %in% names(all_data)) {
  year_pos <- match("YEAR", names(all_data))
  all_data <- all_data[, 1:year_pos]
} else {
  stop("Column 'YEAR' not found in the data.")
}

# Drop any fully empty rows just in case
all_data <- all_data %>% filter(if_any(everything(), ~ !is.na(.) & . != ""))

# --- Keep only rows where REGION is 'clyde' or 'c-i' ---
if ("REGION" %in% names(all_data)) {
  all_data <- all_data %>% filter(tolower(REGION) %in% c("clyde", "c-i"))
} else {
  stop("Column 'REGION' not found in the data.")
}

# Write the consolidated data to CSV
write.csv(all_data, "consolidated_data.csv", row.names = FALSE)

message("Consolidation complete. Output saved to consolidated_data.csv")