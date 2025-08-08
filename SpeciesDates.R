library(readr)
library(dplyr)
library(lubridate)
library(stringr)
library(tidyr)

# ==== INPUT ====
input_file <- "combined_records.csv"   # change this to your input file
output_file <- "species_date_summary.csv"

# ==== LOAD DATA ====
df <- read_csv(input_file, col_types = cols(
  Species = col_character(),
  Date = col_date(format = ""),
  Count = col_character()
))

# ==== CLEAN SPECIES COLUMN ====
df <- df %>%
  filter(
    !str_detect(Species, "^Unidentified"),   # 1. Remove 'Unidentified...'
    !str_detect(Species, "/"),               # 3. Remove records with '/'
    !str_detect(Species, "^Domestic"),       # 4. Remove 'Domestic...'
    !str_detect(Species, "\\s+x\\s+")        # 5. Remove hybrids with ' x '
  ) %>%
  mutate(
    Species = str_trim(str_remove(Species, "\\s*\\([^)]*\\)$")) # 2. Remove brackets at end
  )

# ==== CLEAN COUNT COLUMN ====
df <- df %>%
  mutate(Count = case_when(
    str_to_lower(Count) == "present" ~ "1",
    TRUE ~ Count
  ),
  Count = str_remove_all(Count, "^c"),
  Count = str_remove_all(Count, "\\+$"),
  Count = as.numeric(Count)
  ) %>%
  mutate(
    Month = month(Date, label = TRUE, abbr = TRUE),
    DOY = yday(Date)
  )

# ==== EARLIEST & LATEST (seasonal extremes, with year) ====
date_summary <- df %>%
  group_by(Species) %>%
  summarise(
    EarliestDOY = min(DOY, na.rm = TRUE),
    LatestDOY = max(DOY, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  rowwise() %>%
  mutate(
    Earliest = df %>% filter(Species == Species, DOY == EarliestDOY) %>% arrange(Date) %>% slice(1) %>% pull(Date),
    Latest   = df %>% filter(Species == Species, DOY == LatestDOY) %>% arrange(desc(Date)) %>% slice(1) %>% pull(Date)
  ) %>%
  ungroup() %>%
  select(Species, Earliest, Latest)

# ==== MAX COUNT PER MONTH WITH DATE ====
monthly_max <- df %>%
  group_by(Species, Month) %>%
  filter(!is.na(Count)) %>%
  summarise(
    MaxCount = max(Count, na.rm = TRUE),
    MaxDate = Date[which.max(Count)],
    .groups = "drop"
  ) %>%
  mutate(
    Month = factor(Month, levels = month.abb),
    CountDate = paste0(MaxCount, " (", MaxDate, ")")
  ) %>%
  select(Species, Month, CountDate) %>%
  pivot_wider(
    names_from = Month,
    values_from = CountDate,
    values_fill = "0"
  )

# ==== COMBINE EVERYTHING ====
final <- date_summary %>%
  left_join(monthly_max, by = "Species") %>%
  select(Species, Earliest, Latest, all_of(month.abb)) %>%
  arrange(Species)

# ==== WRITE TO CSV ====
write_csv(final, output_file)

cat("Summary saved to:", output_file, "\n")