# Load required libraries
library(readr)
library(dplyr)
library(lubridate)

# Get command line argument
if (interactive()) {
  args <- c('cleaned_output.csv')
} else {
  args <- commandArgs(trailingOnly = TRUE)
}

if (length(args) != 1) {
  stop("Usage: Rscript add_season.R <input_file.csv>")
}

input_file <- args[1]

# Read CSV
df <- read_csv(input_file, show_col_types = FALSE)

# Check for Date column
if (!"Date" %in% names(df)) {
  stop("Input file must contain a column named 'Date'")
}

# Convert to Date type
df <- df %>% mutate(Date = as.Date(Date))

# Add Season column based on custom rule
df <- df %>%
  mutate(
    Season = case_when(
      Date <= as.Date(paste0(year(Date), "-04-15"))                    ~ "Winter/Spring",
      Date >  as.Date(paste0(year(Date), "-04-15")) & 
        Date <  as.Date(paste0(year(Date), "-08-01"))                    ~ "Summer",
      Date >= as.Date(paste0(year(Date), "-08-01"))                   ~ "Autumn/Winter",
      TRUE                                                            ~ NA_character_
    )
  )

# Write output
output_file <- "with_season.csv"
write_csv(df, output_file)

# Report
cat("✅ 'Season' column added based on custom date ranges.\n")
cat("📄 Output written to:", output_file, "\n")