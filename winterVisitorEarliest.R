# Load required packages
library(dplyr)
library(lubridate)
library(tidyr)
library(janitor)

# ---- Parameters ----
input_file <- "migrant_first_dates.csv"   # input CSV file

# ---- Read data ----
df <- read.csv(input_file, stringsAsFactors = FALSE) %>%
  janitor::clean_names()   # standardize column names

print("Column names in the input:")
print(names(df))

# ---- Identify year columns (e.g., x1982, x1983 ...) ----
year_cols <- grep("^x[0-9]{4}$", names(df), value = TRUE)
if (length(year_cols) == 0) stop("No year columns found! Check your CSV header row.")

# ---- Reshape year columns to long format ----
df_long <- df %>%
  pivot_longer(
    cols = all_of(year_cols),
    names_to = "year",
    values_to = "date_raw"
  ) %>%
  mutate(
    year = as.integer(gsub("^x", "", year)),
    # parse date robustly and convert to Date
    date = as.Date(parse_date_time(date_raw, orders = c("dmy", "ymd"), exact = FALSE))
  ) %>%
  filter(!is.na(year), !is.na(date))

# ---- Calculate days after 31 May ----
df_long <- df_long %>%
  mutate(
    cutoff = as.Date(make_date(year, 5, 31)),  # convert cutoff to Date
    days_after = as.numeric(date - cutoff)
  ) %>%
  filter(days_after >= 0)

# ---- Find earliest date for each winter species ----
result <- df_long %>%
  mutate(winter_summer = trimws(tolower(winter_summer))) %>%
  filter(winter_summer == "w") %>%
  group_by(species = !!sym(names(df)[1])) %>%
  slice_min(days_after, n = 1, with_ties = FALSE) %>%
  ungroup() %>%
  mutate(date = format(date, "%d/%m/%Y")) %>%  # force DD/MM/YYYY output
  select(species, date)

# ---- Save output ----
write.csv(result, "winter_visitors_earliest_dates.csv", row.names = FALSE)

print("Final result:")
print(result)