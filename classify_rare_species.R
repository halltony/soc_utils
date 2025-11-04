# ==========================================
# Classify species by rarity based on annual occurrence patterns
# ==========================================
# Input: combined_records_clean.csv
# Outputs:
#   scarce_species.csv
#   rare_species.csv
#   very_rare_species.csv
#   species_classification_summary.csv
# ==========================================

library(tidyverse)
library(lubridate)

# ---- CONFIGURATION ----
input_file <- "combined_records_clean.csv"
output_scarce <- "scarce_species.csv"
output_rare <- "rare_species.csv"
output_very_rare <- "very_rare_species.csv"
output_summary <- "species_classification_summary.csv"

# Define what "small count" means for scarce species (tune as needed)
scarce_threshold <- 10   # e.g. fewer than 10 records per year on average

# ---- LOAD DATA ----
data <- read_csv(input_file, show_col_types = FALSE)

# Check columns
if (!"Species" %in% names(data) || !"Date" %in% names(data)) {
  stop("Input file must contain 'Species' and 'Date' columns.")
}

# Extract Year
data <- data %>%
  mutate(Year = year(as.Date(Date))) %>%
  filter(!is.na(Year))

# ---- SUMMARISE BY SPECIES ----
species_summary <- data %>%
  group_by(Species, Year) %>%
  summarise(Records = n(), .groups = "drop_last") %>%
  summarise(
    YearsPresent = n_distinct(Year),
    MeanRecordsPerYear = mean(Records),
    TotalRecords = sum(Records),
    .groups = "drop"
  )

# Determine dataset range
total_years <- n_distinct(data$Year)
message("Total years in dataset: ", total_years)

# ---- CLASSIFY SPECIES ----
species_classified <- species_summary %>%
  mutate(
    Category = case_when(
      YearsPresent == total_years & MeanRecordsPerYear <= scarce_threshold ~ "Scarce",
      YearsPresent < total_years & YearsPresent > 2 ~ "Rare",
      YearsPresent <= 2 ~ "Very rare",
      TRUE ~ "Other"
    )
  ) %>%
  arrange(Category, Species)

# ---- SPLIT RECORDS INTO FILES ----
scarce_species <- species_classified %>% filter(Category == "Scarce") %>% pull(Species)
rare_species <- species_classified %>% filter(Category == "Rare") %>% pull(Species)
very_rare_species <- species_classified %>% filter(Category == "Very rare") %>% pull(Species)

# Filter full dataset for each group
scarce_data <- data %>% filter(Species %in% scarce_species)
rare_data <- data %>% filter(Species %in% rare_species)
very_rare_data <- data %>% filter(Species %in% very_rare_species)

# ---- WRITE OUTPUT FILES ----
write_csv(scarce_data, output_scarce)
write_csv(rare_data, output_rare)
write_csv(very_rare_data, output_very_rare)
write_csv(species_classified, output_summary)

# ---- SUMMARY ----
message("✅ Classification complete")
message("  Scarce species: ", length(scarce_species), " → ", output_scarce)
message("  Rare species: ", length(rare_species), " → ", output_rare)
message("  Very rare species: ", length(very_rare_species), " → ", output_very_rare)
message("  Full summary table written to: ", output_summary)