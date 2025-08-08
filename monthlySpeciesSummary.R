# Load required libraries
library(dplyr)
library(lubridate)
library(readr)
library(tidyr)
library(stringr)

# --- Step 1: Load and prepare the data ---
input_file <- "combined_records.csv"  # Update as needed

df <- read_csv(input_file, show_col_types = FALSE) %>%
  mutate(
    Date = as.Date(Date),
    Month = month(Date),
    Year = year(Date)
  )

# --- Step 2: Clean species names and filter unwanted records ---
df <- df %>%
  mutate(
    Species = gsub("\\s*\\([^\\)]+\\)$", "", Species),  # remove trailing (text)
    Species = trimws(Species)
  ) %>%
  filter(
    !grepl("^Unidentified", Species),  # remove "Unidentified..."
    !grepl("/", Species),              # remove slashes
    !grepl(" x ", Species),            # remove hybrids
    !grepl("^Domestic", Species)       # remove domestics
  )

# --- Step 3: Clean the Count column ---
df <- df %>%
  mutate(
    Count = str_to_lower(as.character(Count)),                # handle text like "PRESENT"
    Count = ifelse(Count == "present", "1", Count),           # convert "present" to 1
    Count = gsub("^c", "", Count),                            # remove leading "c"
    Count = gsub("\\+$", "", Count),                          # remove trailing "+"
    Count_numeric = suppressWarnings(as.numeric(Count))       # convert to numeric safely
  )

# --- Step 4: Report any non-numeric Count values (after cleaning) ---
non_numeric_counts <- df %>%
  filter(is.na(Count_numeric)) %>%
  distinct(Species, Count) %>%
  arrange(Species)

if (nrow(non_numeric_counts) > 0) {
  cat("⚠️ Warning: The following Count values could not be converted to numeric:\n")
  print(non_numeric_counts)
}

# --- Step 5: Aggregate by species, year, and month ---
df_clean <- df %>%
  filter(!is.na(Count_numeric)) %>%
  group_by(Species, Year, Month) %>%
  summarise(
    Observations = n(),
    MaxCount = max(Count_numeric, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    MonthDate = as.Date(sprintf("%04d-%02d-01", Year, Month)),
    MonthLabel = format(MonthDate, "%Y-%m"),
    Summary = paste0(Observations, " (", MaxCount, ")")
  )

# --- Step 6: Pivot to wide format with columns ordered by date ---
# Create month label and a true date value for sorting
df_clean <- df_clean %>%
  mutate(
    MonthDate = as.Date(sprintf("%04d-%02d-01", Year, Month)),
    MonthLabel = format(MonthDate, "%Y-%m"),
    Summary = paste0(Observations, " (", MaxCount, ")")
  )

# Pivot to wide format (note: order not guaranteed yet)
wide_data <- df_clean %>%
  select(Species, MonthLabel, Summary) %>%
  pivot_wider(names_from = MonthLabel, values_from = Summary)

# Get the month columns and sort them correctly
month_cols <- sort(unique(df_clean$MonthLabel))
month_cols_ordered <- month_cols[order(as.Date(paste0(month_cols, "-01")))]

# Reorder columns: keep 'Species' first, then sorted month columns
output_data <- wide_data %>%
  select(Species, all_of(month_cols_ordered)) %>%
  arrange(Species)

# --- Step 7: Write output CSV ---
output_file <- "species_monthly_summary.csv"
write_csv(output_data, output_file)
cat("✅ Output written to:", output_file, "\n")