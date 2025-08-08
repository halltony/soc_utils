# Compare the structure and data types of two CSV files

# Load required packages
# install.packages("readr") # Uncomment if needed
library(readr)

# Define paths to your CSV files
file1_path <- '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/2023/BirdTrack/All 2023 recs extracted 26 May 2025.csv'
file2_path <- '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/2023/eBird/Clipped and Cleaned Files/EBird-2023Corrigenda(removalofspeciesetc).csv'

# Get column specs (names and types)
spec_file1 <- spec(read_csv(file1_path, n_max = 100))  # Read small sample to infer types
spec_file2 <- spec(read_csv(file2_path, n_max = 100))

columns_file1 <- names(spec_file1$cols)
columns_file2 <- names(spec_file2$cols)

# Compare column names
only_in_file1 <- setdiff(columns_file1, columns_file2)
only_in_file2 <- setdiff(columns_file2, columns_file1)
in_both_files <- intersect(columns_file1, columns_file2)

# Compare types for shared columns
type_differences <- lapply(in_both_files, function(col) {
  type1 <- class(spec_file1$cols[[col]])[1]
  type2 <- class(spec_file2$cols[[col]])[1]
  if (type1 != type2) {
    return(data.frame(Column = col, Type_in_File1 = type1, Type_in_File2 = type2))
  } else {
    return(NULL)
  }
})
type_differences <- do.call(rbind, type_differences)

# Print results
cat("=== Columns in File 1 but NOT in File 2 ===\n")
print(only_in_file1)

cat("\n=== Columns in File 2 but NOT in File 1 ===\n")
print(only_in_file2)

cat("\n=== Columns in BOTH files ===\n")
print(in_both_files)

cat("\n=== Data Type Differences in Shared Columns ===\n")
if (!is.null(type_differences)) {
  print(type_differences)
} else {
  cat("No data type differences found in shared columns.\n")
}