# Install these packages if you haven't already
# install.packages(c("rvest", "dplyr", "readr"))

library(rvest)
library(dplyr)
library(readr)

# Define the URL
url <- "https://www.the-soc.org.uk/pages/the-scottish-list"

# Read the HTML from the webpage
page <- read_html(url)

# Extract all tables
tables <- page %>% html_table(fill = TRUE)

# Review tables to find the correct one
# View(tables[[1]]) etc. if unsure
# Assuming the Systematic List is the first or among first tables
systematic_list <- tables[[1]]  # or tables[[2]] depending on position

# Optional: clean up column names
colnames(systematic_list) <- make.names(colnames(systematic_list), unique = TRUE)

# Save as CSV
write_csv(systematic_list, "scottish_list_systematic.csv")

cat("Saved to scottish_list_systematic.csv\n")