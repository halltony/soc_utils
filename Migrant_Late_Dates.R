library(dplyr)
library(readr)
library(lubridate)
library(tidyr)
library(stringr)

# ---- CONFIG ----
input_file  <- "winter_visitors_2006_to_2020.csv"
output_file <- "earliest_winter_visitors.csv"

target_species <- c(
  "Barnacle Goose",
  "Bewick's Swan",
  "Brambling",
  "Brent Goose",
  "Brent Goose (Light-bellied - hrota)",
  "Chiffchaff (Siberian - tristis)",
  "Fieldfare",
  "Glaucous Gull",
  "Goldeneye",
  "Great Grey Shrike",
  "Greenshank",
  "Iceland Gull",
  "Jack Snipe",
  "Long-tailed Duck",
  "Pink-footed Goose",
  "Pintail",
  "Redwing",
  "Slavonian Grebe",
  "Smew",
  "Snow Bunting",
  "Taiga Bean Goose",
  "Taiga/Tundra Bean Goose",
  "Tundra Bean Goose",
  "Turnstone",
  "Waxwing",
  "White Wagtail (alba)",
  "White-fronted Goose",
  "White-fronted Goose (European - albifrons)",
  "White-fronted Goose (Greenland - flavirostris)",
  "Whooper Swan"
)

# Winter seasons of interest (start years)
target_seasons <- c(2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017,
                    2018, 2019, 2020)

# ---- LOAD & CLEAN ----
df <- read_csv(input_file, show_col_types = FALSE) %>%
  mutate(
    Species = str_squish(as.character(Species)),
    Date_raw = as.character(Date),
    Date_parsed = parse_date_time(Date_raw, orders = c("dmy","ymd","mdy"), tz = "UTC"),
    Date_parsed = as_date(Date_parsed)
  )

# ---- ASSIGN WINTER SEASON (start year) ----
df <- df %>%
  mutate(
    Season = case_when(
      !is.na(Date_parsed) & month(Date_parsed) >= 6 ~ year(Date_parsed),       # June–Dec → same year
      !is.na(Date_parsed) & month(Date_parsed) <= 5 ~ year(Date_parsed) - 1,   # Jan–May → previous year
      TRUE ~ NA_integer_
    )
  )

# ---- EARLIEST RECORDS ----
earliest_records <- df %>%
  filter(Species %in% target_species, Season %in% target_seasons) %>%
  group_by(Species, Season) %>%
  summarise(
    Earliest_Date = {
      tmp <- Date_parsed[!is.na(Date_parsed)]
      if (length(tmp) == 0) as.Date(NA) else min(tmp)
    },
    .groups = "drop"
  )

# ---- PAD WITH FULL GRID ----
species_season_grid <- expand.grid(Species = target_species, Season = target_seasons, stringsAsFactors = FALSE)

earliest_full <- species_season_grid %>%
  left_join(earliest_records, by = c("Species", "Season")) %>%
  arrange(Species, Season)

# ---- WIDE FORMAT (species as rows, seasons as columns) ----
earliest_wide <- earliest_full %>%
  pivot_wider(names_from = Season, values_from = Earliest_Date, names_prefix = "Season_") %>%
  arrange(Species)

# ---- FORMAT DATES dd/mm/yyyy ----
earliest_wide <- earliest_wide %>%
  mutate(across(starts_with("Season_"), ~ ifelse(is.na(.), NA, format(., "%d/%m/%Y"))))

# ---- SAVE ----
write_csv(earliest_wide, output_file)
print(earliest_wide)
