# Load required packages
library(readxl)
library(writexl)
library(dplyr)
library(tcltk)  # For file dialogs

# Prompt user to select Clyde species file
clyde_file <- tk_choose.files(caption = "Select the Clyde species Excel file")

# Prompt user to select BBRC status file
bbrc_file <- tk_choose.files(caption = "Select the BBRC species status Excel file")

# Read in the Excel files
clyde_data <- read_excel(clyde_file)
bbrc_data <- read_excel(bbrc_file)

# Standardize column names for joining
colnames(clyde_data)[colnames(clyde_data) == "Scientific name"] <- "Scientific_Name"
colnames(bbrc_data)[colnames(bbrc_data) == "Scientific Name"] <- "Scientific_Name"

# Perform a left join to add BBRC Status
merged_data <- left_join(
  clyde_data,
  bbrc_data %>% select(Scientific_Name, `BBRC Status`),
  by = "Scientific_Name"
)

# Ask user where to save the output
output_file <- tk_choose.files(caption = "Select location and name for output file", multi = FALSE)
if (file.exists(output_file)) file.remove(output_file)  # Overwrite if file exists
write_xlsx(merged_data, output_file)

cat("Merged file saved to:", output_file, "\n")