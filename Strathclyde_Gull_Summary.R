library(dplyr)
library(readr)
library(lubridate)
library(tidyr)
library(stringr)

# Read CSV
data <- read_csv("Strathclyde_gull_records.csv")

# Convert Date
data <- data %>%
  mutate(Date = as.Date(Date, format = "%d/%m/%Y"))

# Clean Count
data <- data %>%
  mutate(
    Count = str_replace_all(Count, regex("^present$", ignore_case = TRUE), "1"),
    Count = str_extract(Count, "\\d+"),
    Count = as.numeric(Count)
  )

# Extract Year
data <- data %>%
  mutate(Year = year(Date))

# Full set of years
all_years <- sort(unique(data$Year))

# Find max per species per year
gull_max <- data %>%
  group_by(Species, Year) %>%
  summarise(MaxCount = max(Count, na.rm = TRUE), .groups = "drop")

# Pivot — no aggregation, just reshape
gull_wide <- gull_max %>%
  pivot_wider(
    names_from = Year,
    values_from = MaxCount,
    values_fill = NA
  )

# Order columns chronologically
gull_wide <- gull_wide %>%
  select(Species, all_of(as.character(all_years))) %>%
  arrange(Species)

# Write output
write_csv(gull_wide, "Strathclyde_gull_summary.csv")