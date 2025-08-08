# Load necessary libraries
library(dplyr)
library(lubridate)
library(tidyr)

BT_data_for_last_10_years <- read.csv('combined_records.csv')

# Function to create the desired dataframe
generate_species_week_dataframe <- function(df, species_column, date_column) {
  # Ensure the required columns exist
  if (!all(c(species_column, date_column) %in% names(df))) {
    stop("The specified columns are not present in the dataframe.")
  }
  
  # Convert the date column to Date format and calculate week number and year
  df <- df %>%
    mutate(
      Date = as.Date(.data[[date_column]], format = "%Y-%m-%d"),
      Week_Number = isoweek(Date),
      Year = year(Date)
    )
  
  # Find the latest year for each species and week number
  summary_df <- df %>%
    group_by(across(all_of(species_column)), Week_Number) %>%
    summarize(Latest_Year = max(Year), .groups = "drop")
  
  # Reshape the data into a wide format with week numbers as columns
  result_df <- summary_df %>%
    pivot_wider(
      names_from = Week_Number,
      values_from = Latest_Year,
      names_prefix = "Week_"
    ) %>%
    arrange(across(all_of(species_column)))
  
  # Order columns sequentially by increasing numerical week number
  week_columns <- grep("^Week_", names(result_df), value = TRUE)
  week_columns <- week_columns[order(as.numeric(sub("Week_", "", week_columns)))]
  ordered_columns <- c(species_column, week_columns)
  result_df <- result_df[, ordered_columns]
  
  return(result_df)
}

# Create the new dataframe
output_data <- generate_species_week_dataframe(BT_data_for_last_10_years, "Species", "Date")

# Print the result
print(output_data)

write.csv(output_data, 'latest_year_summary.csv')