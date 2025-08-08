# Load necessary library
library(readr)
library(dplyr)

# Get command line argument
if (interactive()) {
  args <- c('cleaned_output.csv')
} else {
  args <- commandArgs(trailingOnly = TRUE)
}

if (length(args) != 1) {
  stop("Usage: Rscript count_species.R <input_file.csv>")
}

input_file <- args[1]

# Read CSV
df <- read_csv(input_file, show_col_types = FALSE)

# Check for the Species column
if (!"Species" %in% names(df)) {
  stop("The input file must contain a column named 'Species'")
}

# Count and sort species by ascending order
species_counts <- df %>%
  group_by(Species) %>%
  summarise(Count = n(), .groups = "drop") %>%
  arrange(Count)  # Ascending order

# Print result
print(species_counts)

# Write to file
write_csv(species_counts, "species_counts.csv")

cat("✅ Output written to 'species_counts.csv' (sorted by ascending count)\n")