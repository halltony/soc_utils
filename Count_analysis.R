# Bird Observation Count Analysis
# This script cleans count data and calculates per-species statistics

# Load required libraries
library(dplyr)
library(tidyr)

# Read the CSV file
# Replace 'your_file.csv' with your actual file path
file_path <- 'cleaned_output.csv'
bird_data <- read.csv(file_path, stringsAsFactors = FALSE)

# Display original data structure
cat("Original data structure:\n")
print(head(bird_data))
cat("\n")

# Clean the count column and add season
# Assuming the count column is named 'Count' and date column is 'Date' - adjust if needed
bird_data_clean <- bird_data %>%
  mutate(
    Count_Original = Count,  # Keep original for reference
    Count_Clean = as.character(Count),  # Convert to character for manipulation
    Count_Clean = case_when(
      # Replace 'Present' with '1'
      toupper(trimws(Count_Clean)) == "PRESENT" ~ "1",
      # For all other values, keep as is
      TRUE ~ Count_Clean
    ),
    # Remove 'c' or 'C' prefix
    Count_Clean = gsub("^[cC]", "", Count_Clean),
    # Remove '+' suffix
    Count_Clean = gsub("\\+$", "", Count_Clean),
    # Remove any remaining whitespace
    Count_Clean = trimws(Count_Clean),
    # Convert to numeric
    Count_Numeric = as.numeric(Count_Clean),
    # Convert Date to Date format (adjust format if needed, e.g., "%d/%m/%Y" for day/month/year)
    Date_Parsed = as.Date(Date),
    # Extract month and day for season assignment
    Month = as.numeric(format(Date_Parsed, "%m")),
    Day = as.numeric(format(Date_Parsed, "%d")),
    # Assign season based on date ranges
    Season = case_when(
      # Winter/Spring: Jan 1 to Apr 15
      (Month == 1) | (Month == 2) | (Month == 3) | (Month == 4 & Day <= 15) ~ "Winter/Spring",
      # Summer: Apr 16 to Jul 31
      (Month == 4 & Day >= 16) | (Month == 5) | (Month == 6) | (Month == 7) ~ "Summer",
      # Autumn/Winter: Aug 1 to Dec 31
      (Month == 8) | (Month == 9) | (Month == 10) | (Month == 11) | (Month == 12) ~ "Autumn/Winter",
      TRUE ~ NA_character_
    )
  )

# Check for any values that couldn't be converted to numeric
problematic_values <- bird_data_clean %>%
  filter(is.na(Count_Numeric) & !is.na(Count_Original)) %>%
  select(Count_Original, Count_Clean)

if (nrow(problematic_values) > 0) {
  cat("Warning: The following values could not be converted to numeric:\n")
  print(unique(problematic_values))
  cat("\n")
}

# Calculate statistics per species
# Assuming the species column is named 'Species' - adjust if needed
species_stats <- bird_data_clean %>%
  filter(!is.na(Count_Numeric)) %>%
  group_by(Species) %>%
  summarise(
    Total_Records = n(),
    Max_Count = max(Count_Numeric, na.rm = TRUE),
    Percentile_95 = quantile(Count_Numeric, probs = 0.95, na.rm = TRUE),
    Records_in_Top_5_Percent = sum(Count_Numeric >= quantile(Count_Numeric, probs = 0.95, na.rm = TRUE)),
    .groups = 'drop'
  ) %>%
  arrange(desc(Max_Count))

# Display results
cat("Species Statistics:\n")
cat("==================\n\n")
print(species_stats, n = Inf)

# Calculate statistics per species and season
species_season_stats <- bird_data_clean %>%
  filter(!is.na(Count_Numeric) & !is.na(Season)) %>%
  group_by(Species, Season) %>%
  summarise(
    Total_Records = n(),
    Max_Count = max(Count_Numeric, na.rm = TRUE),
    Percentile_95 = quantile(Count_Numeric, probs = 0.95, na.rm = TRUE),
    Records_in_Top_5_Percent = sum(Count_Numeric >= quantile(Count_Numeric, probs = 0.95, na.rm = TRUE)),
    .groups = 'drop'
  ) %>%
  # Order seasons chronologically
  mutate(Season = factor(Season, levels = c("Winter/Spring", "Summer", "Autumn/Winter"))) %>%
  arrange(Species, Season)

# Display season results by species
cat("\n\nSpecies x Season Statistics:\n")
cat("============================\n\n")
print(species_season_stats, n = Inf)

# Save season results to CSV
season_output_file <- "bird_species_season_analysis.csv"
write.csv(species_season_stats, season_output_file, row.names = FALSE)
cat("\nSpecies x Season results saved to:", season_output_file, "\n")

# Save results to CSV
output_file <- "bird_species_analysis.csv"
write.csv(species_stats, output_file, row.names = FALSE)
cat("\nResults saved to:", output_file, "\n")

# Optional: Create a summary report
cat("\n\nSummary Report:\n")
cat("===============\n")
cat("Total species analyzed:", nrow(species_stats), "\n")
cat("Total records with valid counts:", sum(species_stats$Total_Records), "\n")
cat("\nTop 5 species by maximum count:\n")
print(head(species_stats %>% select(Species, Max_Count, Percentile_95, Records_in_Top_5_Percent), 5))

cat("\n\nSpecies x Season Breakdown:\n")
cat("Total species-season combinations:", nrow(species_season_stats), "\n")
cat("\nExample - First few species-season combinations:\n")
print(head(species_season_stats, 10))