library(dplyr)
combined_records <- read.csv('combined_records.csv')
ardochrig_records <- combined_records[grep('Ardochrig', combined_records$Place), ]
species <- unique(ardochrig_records[['Species']])
value_counts <- table(ardochrig_records[['Species']])

# Sort values in descending order
sorted_values <- sort(value_counts, decreasing = TRUE)

# Convert the table to a data frame
df <- as.data.frame(sorted_values)

# Print the resulting data frame
write.csv(df, 'Ardochrig_species_counts.csv')
