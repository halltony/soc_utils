# Load packages
library(readr)
library(dplyr)
library(tidyr)

# --- File paths ---
input_csv <- "combined_records.csv"        # Main input file
filter_csv <- "personal_clyde_list_jun25.csv"        # File containing 'Species' column
output_csv <- "species_max_counts.csv"         # Output file

# --- Read input data ---
data <- read_csv(input_csv) %>%
  rename(Numerical_count = `Numerical count`)

# --- Read species filter list ---
species_filter <- read_csv(filter_csv) %>%
  distinct(Species)

# --- Filter to only listed species ---
filtered_data <- data %>%
  semi_join(species_filter, by = "Species")

# --- Get top 10 counts per species and rank them ---
top_counts_long <- filtered_data %>%
  group_by(Species) %>%
  arrange(desc(Numerical_count)) %>%
  slice_head(n = 10) %>%
  mutate(
    Rank = paste0("Top", row_number()),
    Numerical_count = round(Numerical_count)
  ) %>%
  ungroup()

# --- Pivot to wide format: one row per species, columns for Top1 ... Top10 ---
top_counts_wide <- top_counts_long %>%
  select(Species, Rank, Numerical_count) %>%
  pivot_wider(names_from = Rank, values_from = Numerical_count)

# --- Write to CSV ---
write_csv(top_counts_wide, output_csv)

cat("✅ Top 10 values per species saved to:", output_csv, "\n")