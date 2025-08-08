# Load necessary libraries
library(readxl)
library(dplyr)
library(stringr)

# Function to combine sheets with 'Records#' in their name
combine_sheets_to_csv <- function(excel_file_path, output_csv_path) {
  # Get all sheet names in the Excel file
  sheet_names <- excel_sheets(excel_file_path)
  
  # Filter sheet names containing 'Records#'
  target_sheets <- sheet_names[str_detect(sheet_names, "Records#")]
  
  # Read and combine all target sheets into a single dataframe
  combined_data <- bind_rows(lapply(target_sheets, function(sheet) {
    read_excel(excel_file_path, sheet = sheet)
  }))
  
  # Write the combined dataframe to a CSV file
  write.csv(combined_data, output_csv_path, row.names = FALSE)
}

# Example usage
excel_file <- '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Weekly Lists/Previous Years Data/Clyde BirdTrack 01-01-2015 to 31-12-204.xlsx'  # Path to your Excel file
output_csv <- "combined_records.csv"  # Path for the output CSV file

combine_sheets_to_csv(excel_file, output_csv)

cat("Data has been successfully combined and saved to", output_csv)