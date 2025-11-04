# ==========================================
# Estimate number of individual birds per species per year
# Using spatio-temporal clustering
# Cleans Count column and uses max per cluster
# Output: summary table (one row per species, one column per year)
# ==========================================

library(tidyverse)
library(lubridate)
library(dbscan)
library(geosphere)

# ---- CONFIGURATION ----
input_file <- "scarce_species.csv"          # Input CSV
output_file <- "estimated_individuals_summary.csv"  # Output summary
distance_radius_m <- 8000   # ~5 miles
time_radius_days <- 5       # Same individual if within 5 days
min_records <- 1            # Minimum points per cluster
count_column <- "Count"     # Column containing number of birds per observation

# ---- LOAD DATA ----
data <- read_csv(input_file, show_col_types = FALSE)

# ---- CLEAN Count COLUMN ----
clean_count <- function(x) {
  x <- as.character(x)
  x <- str_remove_all(x, "^[cC]")       # remove leading c or C
  x <- str_remove_all(x, "\\+$")        # remove trailing +
  x <- ifelse(tolower(x) == "present", 1, x)  # replace Present/present with 1
  as.numeric(x)
}

if (!(count_column %in% names(data))) {
  stop(paste0("Input file must contain a '", count_column, "' column."))
}

data <- data %>%
  mutate(
    Count_clean = clean_count(.data[[count_column]]),
    Date = as.Date(Date),
    Year = year(Date),
    Date_num = as.numeric(Date)
  ) %>%
  filter(!is.na(Lat), !is.na(Long), !is.na(Date))

# ---- FUNCTION TO ESTIMATE INDIVIDUALS PER SPECIES-YEAR ----
estimate_for_species_year <- function(df, sp, yr) {
  if (nrow(df) == 0) return(tibble(Species = sp, Year = yr, Estimated_Individuals = 0, Records = 0))
  
  # Compute pairwise spatial distances (meters)
  spatial_dist <- distm(df[, c("Long", "Lat")])
  
  # Compute pairwise temporal distances (days)
  time_dist <- as.matrix(dist(df$Date_num))
  
  # Combine space and time
  combined_dist <- spatial_dist / distance_radius_m + time_dist / time_radius_days
  
  # DBSCAN clustering
  cl <- dbscan(as.dist(combined_dist), eps = 1, minPts = min_records)
  df$cluster <- cl$cluster
  
  # Calculate estimated individuals = sum of max Count per cluster
  est_ind <- df %>%
    filter(cluster > 0) %>%
    group_by(cluster) %>%
    summarise(MaxCount = max(Count_clean, na.rm = TRUE)) %>%
    summarise(Estimated_Individuals = sum(MaxCount)) %>%
    pull(Estimated_Individuals)
  
  if (length(est_ind) == 0) est_ind <- 0
  
  tibble(
    Species = sp,
    Year = yr,
    Estimated_Individuals = est_ind,
    Records = nrow(df)
  )
}

# ---- APPLY BY SPECIES-YEAR ----
results <- data %>%
  group_by(Species, Year) %>%
  group_modify(~ estimate_for_species_year(.x, unique(.x$Species), unique(.x$Year))) %>%
  ungroup()

# ---- CONVERT TO WIDE SUMMARY ----
results_wide <- results %>%
  mutate(Value = paste0(Estimated_Individuals, " (", Records, ")")) %>%
  select(Species, Year, Value) %>%
  pivot_wider(names_from = Year, values_from = Value)

# ---- ENSURE YEAR COLUMNS ASCENDING ----
year_cols <- sort(as.numeric(colnames(results_wide)[-1]))
results_wide <- results_wide %>%
  select(Species, all_of(as.character(year_cols)))

# ---- REPLACE NA WITH BLANK ----
results_wide[is.na(results_wide)] <- ""

# ---- SAVE OUTPUT ----
write_csv(results_wide, output_file)

message("✅ Saved multi-year summary to: ", output_file)
message("Columns: ", paste(colnames(results_wide), collapse = ", "))