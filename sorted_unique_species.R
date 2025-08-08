library(readr)
library(dplyr)
library(stringr)

# --- User input ---
input_csv <- "with_season.csv"      # Your input CSV filename
output_csv <- "unique_species_sorted.csv"  # Output CSV filename

# --- Read the input CSV and rename column ---
data <- read_csv(input_csv) %>%
  rename(BOU_order = `BOU order`)

# --- Extract unique species and their BOU_order ---
unique_species <- data %>%
  select(Species, BOU_order) %>%
  mutate(Species_clean = str_to_lower(str_trim(Species))) %>%
  distinct(Species_clean, .keep_all = TRUE)

# --- Sort by BOU_order ---
sorted_species <- unique_species %>%
  arrange(BOU_order)

# --- Write output CSV with only Species column ---
write_csv(sorted_species %>% select(Species), output_csv)

cat("Unique species sorted by BOU_order saved to:", output_csv, "\n")