# Load required packages
library(dplyr)
library(lubridate)
library(readr)
library(tidyr)

# Load and prepare data
input_file <- "combined_records.csv"  # update if needed
df <- read_csv(input_file) %>%
  mutate(
    Date = as.Date(Date),
    Month = month(Date),
    Year = year(Date),
    DayOfYear = yday(Date)
  ) %>%
  filter(Date >= as.Date("2020-01-01"))  # <-- Drop all pre-2020 rows here

# Clean species names and filter unwanted records
df <- df %>%
  mutate(Species = gsub("\\s*\\([^\\)]+\\)$", "", Species),
         Species = trimws(Species)) %>%
  filter(
    !grepl("^Unidentified", Species),
    !grepl("/", Species),
    !grepl(" x ", Species),
    !grepl("^Domestic", Species)
  )

# Function to calculate seasonal flags with updated Resident logic
get_flags <- function(months_seen_by_year) {
  years_with_full_coverage <- sum(sapply(months_seen_by_year, function(months) all(1:12 %in% months)))
  total_years <- length(months_seen_by_year)
  resident_flag <- if (total_years > 0) (years_with_full_coverage / total_years) >= 0.8 else FALSE
  
  # Flatten all months across all years for other flags
  all_months_seen <- sort(unique(unlist(months_seen_by_year)))
  
  list(
    Resident = resident_flag,
    summer.visitor = all(all_months_seen %in% 3:10) &&
      all(c(5,6,7) %in% all_months_seen),
    winter.visitor = all(all_months_seen %in% c(9:12, 1:5)) &&
      all(c(10,11,12,1,2) %in% all_months_seen),
    spring.passage.migrant = any(all_months_seen %in% 3:5) && !any(all_months_seen %in% 6:7),
    autumn.passage.migrant = any(all_months_seen %in% 8:10) && !any(all_months_seen %in% 6:7)
  )
}

# Compute months seen per year for each species
months_by_species_year <- df %>%
  group_by(Species, Year) %>%
  summarise(Months = list(unique(Month)), .groups = "drop") %>%
  group_by(Species) %>%
  summarise(MonthsByYear = list(setNames(Months, Year)), .groups = "drop")

# Get first and last calendar dates (ignoring year)
first_last_dates <- df %>%
  group_by(Species) %>%
  summarise(
    first.observation.date = format(Date[which.min(DayOfYear)], "%m-%d"),
    last.observation.date = format(Date[which.max(DayOfYear)], "%m-%d"),
    .groups = "drop"
  )

# Compute seasonal flags
seasonal_summary <- months_by_species_year %>%
  rowwise() %>%
  mutate(flags = list(get_flags(MonthsByYear))) %>%
  unnest_wider(flags) %>%
  left_join(first_last_dates, by = "Species")

# Get list of all years in the dataset
all_years <- unique(df$Year)

# Compute vagrant status
vagrant_status <- df %>%
  group_by(Species, Year) %>%
  summarise(yearly_count = n(), .groups = "drop") %>%
  group_by(Species) %>%
  summarise(
    years_present = list(unique(Year)),
    vagrant_condition_1 = any(yearly_count < 20),
    .groups = "drop"
  ) %>%
  mutate(
    missing_years = sapply(years_present, function(yrs) !all(all_years %in% yrs)),
    .groups = "drop"
  ) %>%
  left_join(
    df %>%
      group_by(Species) %>%
      summarise(max_count = max(Count, na.rm = TRUE)),
    by = "Species"
  ) %>%
  mutate(
    vagrant = (vagrant_condition_1 & (max_count < 2)) | missing_years
  ) %>%
  select(Species, vagrant)

# Combine everything
final_summary <- seasonal_summary %>%
  left_join(vagrant_status, by = "Species") %>%
  select(Species, Resident, summer.visitor, winter.visitor,
         spring.passage.migrant, autumn.passage.migrant,
         vagrant,
         first.observation.date, last.observation.date)

# Save output
write_csv(final_summary, "species_seasonal_summary.csv")

# Notify user
cat("Output written to 'species_seasonal_summary.csv'\n")