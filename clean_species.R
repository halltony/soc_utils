# Load required libraries
library(readr)
library(dplyr)
library(stringr)

# --- Get input file from command line ---
if (interactive()) {
  args <- c('merged_output.csv')
} else {
  args <- commandArgs(trailingOnly = TRUE)
}

if (length(args) != 1) {
  stop("Usage: Rscript clean_species.R <input_file.csv>")
}

input_file <- args[1]

# --- Read data ---
df <- read_csv(input_file, show_col_types = FALSE)

if (!"Species" %in% names(df)) {
  stop("Input file must contain a column named 'Species'")
}

# --- Initial row count ---
initial_rows <- nrow(df)

# --- Define filtering conditions ---
filter_unidentified <- str_starts(df$Species, "Unidentified")
filter_slash <- str_detect(df$Species, "/")
filter_x_between_words <- str_detect(df$Species, "\\b[xX]\\b")
filter_hybrid <- str_starts(df$Species, "Hybrid")
filter_domestic <- str_starts(df$Species, "Domestic")
filter_muscovy <- str_starts(df$Species, "Muscovy")

# --- Combine all filters ---
rows_to_remove <- filter_unidentified | filter_slash | filter_x_between_words |
  filter_hybrid | filter_domestic | filter_muscovy

removed_rows <- sum(rows_to_remove)

# --- Remove unwanted rows ---
df_cleaned <- df[!rows_to_remove, ]

# --- Remove trailing text in parentheses ---
species_before <- df_cleaned$Species
# df_cleaned$Species <- str_replace(df_cleaned$Species, " \\([^()]*\\)$", "")

# --- Update 'Night-heron' to 'Night Heron' ---
df_cleaned$Species <- str_replace_all(df_cleaned$Species, "Night-heron", "Night Heron")

# --- Count updates ---
updated_rows <- sum(species_before != df_cleaned$Species)

# --- Final row count ---
final_rows <- nrow(df_cleaned)

# --- Write output ---
output_file <- "cleaned_output.csv"
write_csv(df_cleaned, output_file)

# --- Report ---
cat("✅ Cleaning complete\n")
cat("📉 Rows removed:", removed_rows, "\n")
cat("✏️ Rows updated (text cleanup and Night-heron fix):", updated_rows, "\n")
cat("📄 Output written to:", output_file, "\n")