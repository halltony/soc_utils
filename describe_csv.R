# Load required library
library(readr)

# Get command line arguments
if (interactive()) {
  args <- c('/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/2023/eBird/Clipped and Cleaned Files/EBird-2023Corrigenda(removalofspeciesetc).csv')
} else {
  args <- commandArgs(trailingOnly = TRUE)
}

if (length(args) != 1) {
  stop("Usage: Rscript describe_csv.R <input_file.csv>")
}

input_file <- args[1]

# Read CSV file
df <- read_csv(input_file, show_col_types = FALSE)

# Describe columns
cat("📄 Summary of", input_file, "\n\n")
for (col in names(df)) {
  cat("🔹 Column:", col, "\n")
  cat("   - Type:", class(df[[col]])[1], "\n")
  cat("   - Example values:", paste(head(unique(df[[col]]), 5), collapse = ", "), "\n\n")
}