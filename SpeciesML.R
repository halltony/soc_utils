# === Load libraries ===
library(dplyr)
library(lubridate)
library(tidyr)
library(rpart)
library(rpart.plot)
library(readr)
library(sf)
library(stringr)

# === Load and clean data ===
obs_data <- read_csv("combined_records.csv")         # Expected: Species, Date, Count, Lat, Long
species_labels <- read_csv("species_categories.csv") # Expected: Species, Category

# === Clean data ===
obs_data <- obs_data %>%
  mutate(
    Count = str_replace_all(Count, "^c", ""),        # Remove 'c' prefix
    Count = str_replace_all(Count, "\\+$", ""),      # Remove '+' suffix
    Count = ifelse(tolower(Count) == "present", "1", Count),  # Replace 'Present' with '1'
    Count = as.numeric(Count)                        # Convert to numeric
  ) %>%
  filter(!str_starts(Species, "Unidentified")) %>%   # Remove 'Unidentified...' species
  filter(!str_starts(Species, "Hybrid")) %>%         # ❗ NEW: Remove 'Hybrid...' species
  filter(!str_detect(Species, "/")) %>%              # Remove species with slashes
  mutate(Species = str_trim(str_remove(Species, "\\s*\\([^)]*\\)$"))) # Remove final bracketed word

# === Preprocess ===
obs_data <- obs_data %>%
  mutate(Date = as.Date(Date),
         Year = year(Date),
         Month = month(Date)) %>%
  filter(Year >= max(Year) - 9)

# === Ensure all species/month combinations exist
all_months <- expand.grid(
  Species = unique(obs_data$Species),
  Month = 1:12
)

monthly_presence <- obs_data %>%
  mutate(Present = 1) %>%
  group_by(Species, Year, Month) %>%
  summarise(Present = 1, .groups = "drop")

presence_matrix <- all_months %>%
  left_join(
    monthly_presence %>%
      group_by(Species, Month) %>%
      summarise(YearsPresent = n(), .groups = "drop"),
    by = c("Species", "Month")
  ) %>%
  mutate(YearsPresent = replace_na(YearsPresent, 0)) %>%
  pivot_wider(names_from = Month, values_from = YearsPresent, values_fill = 0)

# === Total years per species
total_years <- monthly_presence %>%
  group_by(Species) %>%
  summarise(TotalYears = n_distinct(Year), .groups = "drop")

# === Calculate monthly ratio
presence_matrix <- presence_matrix %>%
  left_join(total_years, by = "Species") %>%
  mutate(across(`1`:`12`, ~ ./TotalYears, .names = "Month{.col}_Ratio"))

# === Mean first and last month seen
first_last_months <- monthly_presence %>%
  group_by(Species, Year) %>%
  summarise(FirstMonth = min(Month),
            LastMonth = max(Month), .groups = "drop") %>%
  group_by(Species) %>%
  summarise(MeanFirstMonth = round(mean(FirstMonth)),
            MeanLastMonth = round(mean(LastMonth)), .groups = "drop")

# === Full feature matrix
feature_matrix <- presence_matrix %>%
  select(Species, TotalYears, starts_with("Month")) %>%
  left_join(first_last_months, by = "Species")

# === Train classification model
training_data <- feature_matrix %>%
  inner_join(species_labels, by = "Species")

tree_model <- rpart(Category ~ ., data = training_data %>% select(-Species), method = "class")
rpart.plot(tree_model)

# === Observation spread summary
summary_features <- obs_data %>%
  group_by(Species, Year) %>%
  summarise(MonthsSeen = n_distinct(Month), .groups = "drop") %>%
  group_by(Species) %>%
  summarise(
    YearsObserved = n_distinct(Year),
    MeanMonthsPerYear = mean(MonthsSeen),
    .groups = "drop"
  )

# === Convert Lat/Long to OS Grid Squares
sf_points <- obs_data %>%
  filter(!is.na(Lat), !is.na(Long)) %>%
  st_as_sf(coords = c("Long", "Lat"), crs = 4326, remove = FALSE) %>%
  st_transform(crs = 27700)

coords <- st_coordinates(sf_points)
sf_points$Easting <- floor(coords[, "X"] / 1000) * 1000
sf_points$Northing <- floor(coords[, "Y"] / 1000) * 1000

get_grid_square <- function(easting, northing) {
  e100k <- floor(easting / 100000)
  n100k <- floor(northing / 100000)
  
  letters <- matrix(c(
    "SV", "SW", "SX", "SY", "SZ", "TV", "TW",
    "SQ", "SR", "SS", "ST", "SU", "TQ", "TR",
    "SL", "SM", "SN", "SO", "SP", "TL", "TM",
    "SF", "SG", "SH", "SJ", "SK", "TF", "TG",
    "SA", "SB", "SC", "SD", "SE", "TA", "TB",
    "NV", "NW", "NX", "NY", "NZ", "OV", "OW",
    "NQ", "NR", "NS", "NT", "NU", "OQ", "OR",
    "NL", "NM", "NN", "NO", "NP", "OL", "OM",
    "NF", "NG", "NH", "NJ", "NK", "OF", "OG",
    "NA", "NB", "NC", "ND", "NE", "OA", "OB"
  ), nrow = 10, byrow = TRUE)
  
  if (n100k >= 0 && n100k < 10 && e100k >= 0 && e100k < 7) {
    letters[n100k + 1, e100k + 1]
  } else {
    NA_character_
  }
}

sf_points$GridRef1km <- mapply(function(e, n) {
  square <- get_grid_square(e, n)
  if (!is.na(square)) {
    x1km <- (e %% 100000) %/% 1000
    y1km <- (n %% 100000) %/% 1000
    paste0(square, sprintf("%02d%02d", x1km, y1km))
  } else {
    NA_character_
  }
}, sf_points$Easting, sf_points$Northing)

grid_square_counts <- sf_points %>%
  st_drop_geometry() %>%
  group_by(Species) %>%
  summarise(Unique1kmSquares = n_distinct(GridRef1km), .groups = "drop")

# === Abundance & Distribution classification
abundance_data <- obs_data %>%
  group_by(Species) %>%
  summarise(
    TotalObservations = n(),
    MaxCount = max(Count, na.rm = TRUE),
    MeanCount = mean(Count, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  left_join(grid_square_counts, by = "Species") %>%
  mutate(
    AbundanceCategory = case_when(
      TotalObservations > 1000 | MaxCount > 50 ~ "Abundant",
      TotalObservations > 200 ~ "Common",
      TotalObservations > 20 ~ "Scarce",
      TRUE ~ "Very Rare"
    ),
    DistributionCategory = case_when(
      Unique1kmSquares > 30 ~ "Widespread",
      Unique1kmSquares > 10 ~ "Moderately Localised",
      Unique1kmSquares > 2 ~ "Localised",
      TRUE ~ "Site-Specific"
    )
  )

# === Predict unclassified species
classified_species <- feature_matrix %>%
  filter(!Species %in% species_labels$Species) %>%
  mutate(PredictedCategory = predict(tree_model, newdata = ., type = "class")) %>%
  left_join(summary_features, by = "Species") %>%
  left_join(abundance_data, by = "Species")

# === Ensure required ratio columns are present
required_ratios <- c("Month4_Ratio", "Month6_Ratio", "Month7_Ratio", "Month12_Ratio")
missing <- setdiff(required_ratios, names(classified_species))
if (length(missing) > 0) stop(paste("❌ Missing ratio columns:", paste(missing, collapse = ", ")))

# === Rule-based classification
classified_species <- classified_species %>%
  mutate(FinalCategory = case_when(
    YearsObserved <= 2 & MeanMonthsPerYear <= 2 ~ "Rare Vagrant",
    MeanFirstMonth <= 4 & MeanLastMonth <= 6 &
      Month7_Ratio < 0.2 & Month12_Ratio < 0.2 & MeanMonthsPerYear <= 3 ~ "Spring Passage Migrant",
    MeanFirstMonth >= 7 & MeanLastMonth >= 9 &
      Month4_Ratio < 0.2 & Month6_Ratio < 0.2 & MeanMonthsPerYear <= 3 ~ "Autumn Passage Migrant",
    TRUE ~ as.character(PredictedCategory)
  )) %>%
  mutate(UncertaintyFlag = case_when(
    YearsObserved <= 4 & MeanMonthsPerYear <= 4 &
      rowSums(across(starts_with("Month"), ~ .x < 0.2)) >= 10 ~ "Uncertain",
    TRUE ~ ""
  ))

# === Export final result
write_csv(
  classified_species %>%
    select(Species, FinalCategory, UncertaintyFlag, AbundanceCategory,
           DistributionCategory, Unique1kmSquares, TotalObservations,
           MaxCount, starts_with("Month"), MeanFirstMonth, MeanLastMonth,
           YearsObserved, MeanMonthsPerYear),
  "final_species_classification.csv"
)

cat("✅ Classification complete. Output saved to: final_species_classification.csv\n")