# ==========================================
# Species Year-Month Grid Plotter (Final Version)
# ==========================================
# Input: combined_records.csv (must include "Species" and "Date" columns)
# Output: One PNG per species showing month/year presence
# ------------------------------------------

# Load libraries
library(tidyverse)
library(lubridate)
library(ggplot2)

# ---- CONFIGURATION ----
input_file <- "combined_records_clean.csv"   # Path to input CSV
output_dir <- "species_grids"          # Output folder for PNGs
date_column <- "Date"                  # Name of the date column
species_column <- "Species"            # Name of the species column

# ---- SETUP ----
if (!dir.exists(output_dir)) dir.create(output_dir)

# ---- LOAD DATA ----
data <- read_csv(input_file, show_col_types = FALSE)

# Convert date column to proper Date type and extract Year + Month
data <- data %>%
  mutate(
    Date = as.Date(.data[[date_column]]),
    Year = year(Date),
    Month = month(Date, label = TRUE, abbr = TRUE)
  ) %>%
  filter(!is.na(Year), !is.na(Month))

# ---- DEFINE GLOBAL YEAR RANGE ----
year_seq <- seq(min(data$Year), max(data$Year))  # full year range across all species
month_seq <- factor(month.abb, levels = month.abb, ordered = TRUE)

# ---- GENERATE PLOTS ----
species_list <- sort(unique(data[[species_column]]))

for (sp in species_list) {
  sp_data <- data %>% filter(.data[[species_column]] == sp)
  
  # Create full Year × Month grid for all possible years and months
  grid <- expand.grid(Year = year_seq, Month = month_seq, stringsAsFactors = FALSE)
  
  # Identify where species was recorded
  presence <- sp_data %>%
    distinct(Year, Month) %>%
    mutate(Present = TRUE)
  
  plot_data <- grid %>%
    left_join(presence, by = c("Year", "Month")) %>%
    mutate(Present = ifelse(is.na(Present), FALSE, Present))
  
  # ---- PLOT ----
  p <- ggplot(plot_data, aes(x = Month, y = factor(Year, levels = rev(year_seq)), fill = Present)) +
    geom_tile(color = "grey80") +
    scale_fill_manual(values = c("FALSE" = "white", "TRUE" = "#3c8dbc")) +
    scale_x_discrete(drop = FALSE) +
    labs(
      title = sp,
      x = "Month",
      y = "Year"
    ) +
    theme_minimal(base_size = 12) +
    theme(
      legend.position = "none",
      plot.title = element_text(face = "bold", hjust = 0.5),
      axis.text.x = element_text(angle = 45, hjust = 1),
      panel.grid = element_blank()
    )
  
  # ---- SAVE ----
  output_file <- file.path(output_dir, paste0(gsub("[^A-Za-z0-9_-]", "_", sp), ".png"))
  ggsave(output_file, plot = p, width = 6, height = 4, dpi = 150)
  
  message("✅ Saved: ", output_file)
}

message("All species grids created in folder: ", output_dir)