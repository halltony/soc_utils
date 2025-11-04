# ==========================================
# Bird Records Data Cleanser
# ==========================================
# Input: combined_records.csv
# Cleansing rules:
#   1. Remove rows where Species begins with "Unidentified"
#   2. Remove trailing bracketed terms (e.g. "Blackbird (male)" → "Blackbird")
#   3. Remove rows where Species contains a "/" character
# Output: combined_records_clean.csv
# ------------------------------------------

library(tidyverse)

# ---- CONFIGURATION ----
input_file <- "combined_records.csv"
output_file <- "combined_records_clean.csv"
species_column <- "Species"

# ---- LOAD DATA ----
data <- read_csv(input_file, show_col_types = FALSE)

# ---- STEP 1: Remove "Unidentified" species ----
cleaned <- data %>%
  filter(!str_starts(.data[[species_column]], regex("^Unidentified", ignore_case = TRUE)))

# ---- STEP 2: Remove "Domestic" species ----
cleaned <- cleaned %>%
  filter(!str_starts(.data[[species_column]], regex("^Domestic", ignore_case = TRUE)))

# ---- STEP 3: Remove trailing bracketed terms ----
# e.g. "Blackbird (male)" → "Blackbird"
cleaned <- cleaned %>%
  mutate(
    !!species_column := str_trim(str_remove(.data[[species_column]], "\\s*\\([^)]*\\)$"))
  )

# ---- STEP 4: Remove rows containing "/" in the species name ----
cleaned <- cleaned %>%
  filter(!str_detect(.data[[species_column]], "/"))

# ---- STEP 5: Remove rows containing " x " in the species name ----
cleaned <- cleaned %>%
  filter(!str_detect(.data[[species_column]], " x "))

# ---- SAVE CLEANED DATA ----
write_csv(cleaned, output_file)

message("✅ Cleaned data saved to: ", output_file)
message("Original rows: ", nrow(data), " | Cleaned rows: ", nrow(cleaned))