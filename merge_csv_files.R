# Load required libraries
library(dplyr)
library(readr)

# --- Get command line arguments ---
if (interactive()) {
  args <- c('/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/2023/BirdTrack/All 2023 recs extracted 26 May 2025.csv', 
            '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/2023/eBird/Clipped and Cleaned Files/EBird-2023Corrigenda(removalofspeciesetc).csv', 
            "merge_columns.csv")
} else {
  args <- commandArgs(trailingOnly = TRUE)
}

if (length(args) != 3) {
  stop("Usage: Rscript merge_csv_files.R <data1.csv> <data2.csv> <merge_columns.csv>")
}

file1 <- args[1]
file2 <- args[2]
merge_map_file <- args[3]

# --- Read input files ---
df1 <- read_csv(file1, show_col_types = FALSE)
df2 <- read_csv(file2, show_col_types = FALSE)
merge_map <- read_csv(merge_map_file, show_col_types = FALSE)

# --- Validate merge map file ---
if (!all(c("birdtrack.column", "ebird.column") %in% names(merge_map))) {
  stop("Merge mapping file must have columns named 'birdtrack.column' and 'ebird.column'")
}

# --- Check for missing columns ---
missing_df1 <- setdiff(merge_map$file1, names(df1))
missing_df2 <- setdiff(merge_map$file2, names(df2))

if (length(missing_df1) > 0 || length(missing_df2) > 0) {
  stop("Missing merge columns:\n",
       if (length(missing_df1) > 0) paste("In file1:", paste(missing_df1, collapse = ", ")), "\n",
       if (length(missing_df2) > 0) paste("In file2:", paste(missing_df2, collapse = ", ")))
}

# --- Rename columns for alignment ---
df1_renamed <- df1 %>% rename_at(vars(merge_map$file1), ~merge_map$file1)
df2_renamed <- df2 %>% rename_at(vars(merge_map$file2), ~merge_map$file1)

# --- Add source file column ---
df1_renamed <- df1_renamed %>% mutate(SourceFile = basename(file1))
df2_renamed <- df2_renamed %>% mutate(SourceFile = basename(file2))

# --- Harmonize data types for merge columns ---
for (col in merge_map$file1) {
  if (!identical(class(df1_renamed[[col]]), class(df2_renamed[[col]]))) {
    df1_renamed[[col]] <- as.character(df1_renamed[[col]])
    df2_renamed[[col]] <- as.character(df2_renamed[[col]])
  }
}

# --- Full outer join ---
merged_df <- full_join(df1_renamed, df2_renamed, by = merge_map$file1, suffix = c(".file1", ".file2"))

# --- Write output ---
output_file <- "merged_output.csv"
write_csv(merged_df, output_file)

# --- Completion message ---
cat("✅ Merge complete. Output written to:", output_file, "\n")
cat("🔢 Total rows in merged file:", nrow(merged_df), "\n")