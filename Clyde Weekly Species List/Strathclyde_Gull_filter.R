library(dplyr)
combined_records <- read.csv('Clyde Records 2012 - 2014.csv')
strathclyde_records <- combined_records[grep('Strathclyde', combined_records$Place), ]
strathclyde_gull_records <- strathclyde_records[grep('Gull', strathclyde_records$Species), ]

# Print the resulting data frame
write.csv(strathclyde_gull_records, 'Strathclyde_gull_records.csv')
