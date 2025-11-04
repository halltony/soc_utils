library(dplyr)
library(readr)
library(lubridate)
library(tidyr)
library(stringr)

# ---- CONFIG ----
input_file  <- "combined_records.csv"
output_file <- "earliest_species_records_wide.csv"

target_species <- c(
  "Arctic Tern","Blackcap","Blackcap (atricapilla)","Chiffchaff","Common Sandpiper",
  "Common Tern","Cuckoo","Dotterel","Gannet","Garden Warbler","Garganey",
  "Grasshopper Warbler","House Martin","Lesser Whitethroat","Little Ringed Plover",
  "Manx Shearwater","Marsh Harrier","Osprey","Pied Flycatcher","Quail","Redstart",
  "Reed Warbler","Ring Ouzel","Sand Martin","Sandwich Tern","Sedge Warbler",
  "Spotted Crake","Spotted Flycatcher","Swallow","Swift","Tree Pipit","Wheatear",
  "Wheatear (Greenland - leucorhoa)","Whimbrel","Whinchat","White Wagtail",
  "Whitethroat","Willow Warbler","Willow Warbler (trochilus)","Wood Sandpiper",
  "Wood Warbler","Yellow Wagtail","Yellow Wagtail (British - flavissima)"
)

target_years <- c(2021, 2022, 2023, 2024)

# ---- LOAD & CLEAN ----
df <- read_csv(input_file, show_col_types = FALSE) %>%
  mutate(
    Species = str_squish(as.character(Species)),
    Date_raw = as.character(Date),
    Date_parsed = parse_date_time(Date_raw, orders = c("dmy","ymd","mdy"), tz = "UTC"),
    Date_parsed = as_date(Date_parsed),
    Year = year(Date_parsed)
  )

# ---- EARLIEST RECORDS ----
earliest_records <- df %>%
  filter(Species %in% target_species, Year %in% target_years) %>%
  group_by(Species, Year) %>%
  summarise(
    Earliest_Date = {
      tmp <- Date_parsed[!is.na(Date_parsed)]
      if (length(tmp) == 0) as.Date(NA) else min(tmp)
    },
    .groups = "drop"
  )

# ---- WIDE FORMAT ----
species_year_grid <- expand.grid(Species = target_species, Year = target_years, stringsAsFactors = FALSE)

earliest_wide <- species_year_grid %>%
  left_join(earliest_records, by = c("Species", "Year")) %>%
  pivot_wider(names_from = Year, values_from = Earliest_Date, names_prefix = "Year_") %>%
  arrange(Species)

# ---- FORMAT DATES AS dd/mm/yyyy ----
earliest_wide <- earliest_wide %>%
  mutate(across(starts_with("Year_"), ~ ifelse(is.na(.), NA, format(., "%d/%m/%Y"))))

# ---- SAVE ----
write_csv(earliest_wide, output_file)
print(earliest_wide)
