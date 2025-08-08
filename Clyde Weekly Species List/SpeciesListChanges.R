# Load necessary library
library(dplyr)

# Set the file paths (update these to match your file locations)
file1 <- '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Weekly Lists/Jan-2025_species_list.csv'
file2 <- '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Weekly Lists/Feb-2025_species_list.csv'

# Load the data
data1 <- read.csv(file1, stringsAsFactors = FALSE)
data2 <- read.csv(file2, stringsAsFactors = FALSE)

# Assuming both CSVs have the same column structure and a unique identifier
# Adjust "id" to match your unique identifier column name
unique_column <- "Selected_Species"

# Records in data1 but not in data2
only_in_data1 <- anti_join(data1, data2, by = unique_column)

# Records in data2 but not in data1
only_in_data2 <- anti_join(data2, data1, by = unique_column)

# Output the results
cat("Records in the first file but not the second:\n")
print(only_in_data1)

cat("\nRecords in the second file but not the first:\n")
print(only_in_data2)

# Optionally write the results to CSV files
write.csv(only_in_data1, "only_in_data1.csv", row.names = FALSE)
write.csv(only_in_data2, "only_in_data2.csv", row.names = FALSE)