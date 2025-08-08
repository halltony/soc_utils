# Load necessary library
library(dplyr)

# Define the path to the CSV file
csv_file <- "/Users/Tony/Desktop/clippedAndCleanedEBirdClydeRAData.csv"  # Replace with your actual file path

# Read the CSV file
data <- read.csv(csv_file, stringsAsFactors = FALSE)

# Specify the column to work with
target_column <- "Species"  # Replace with the actual column name

# Trim whitespace in the target column
data[[target_column]] <- trimws(data[[target_column]])

# Build a combined logical condition for filtering
filter_condition <- !(
  grepl("sp\\.", data[[target_column]], ignore.case = TRUE) |
    grepl("Black-headed/Mediterranean Gull", data[[target_column]], ignore.case = TRUE, fixed = TRUE) |
    grepl("/", data[[target_column]], fixed = TRUE) |
    grepl(" x ", data[[target_column]], fixed = TRUE)
)

# Apply the filtering
data_filtered <- data[filter_condition, ]

# Count how many 'Common Redpoll' replacements will be made
replacements <- sum(grepl("(?i)^Common Redpoll$", data_filtered[[target_column]], perl = TRUE))

# Replace 'Common Redpoll' with 'Redpoll'
data_filtered[[target_column]] <- gsub("(?i)^Common Redpoll$", "Redpoll", data_filtered[[target_column]], perl = TRUE)

# Overwrite the original CSV file
write.csv(data_filtered, csv_file, row.names = FALSE)

cat("Filtered rows removed if they contained: 'sp.', '/', ' x ', or 'Black-headed/Mediterranean Gull'\n")
cat("Replacements made: ", replacements, " ('Common Redpoll' → 'Redpoll')\n")