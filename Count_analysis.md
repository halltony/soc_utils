# Bird Observation Count Analysis

An R script for cleaning and analyzing bird observation count data with per-species and seasonal statistics.

## Overview

This script processes bird observation data from a CSV file, cleans count values, assigns seasonal categories, and generates comprehensive statistics for each species across different seasons.

## Requirements

### R Packages
- `dplyr` - for data manipulation
- `tidyr` - for data tidying

### Installation
```r
install.packages(c("dplyr", "tidyr"))
```

## Input Data Format

Your CSV file should contain the following columns:
- **Species**: Bird species name
- **Count**: Observation count (can include special formats like "Present", "c50", "20+")
- **Date**: Observation date (in a standard date format like YYYY-MM-DD)

## Data Cleaning

The script performs the following cleaning operations on the Count column:

1. **"Present" values** → converted to `1`
2. **"c" prefix** → removed (e.g., "c50" becomes "50")
3. **"+" suffix** → removed (e.g., "20+" becomes "20")
4. **All values** → converted to numeric format

### Cleaning Examples
- `Present` → `1`
- `c25` → `25`
- `C100` → `100`
- `50+` → `50`
- `c30+` → `30`

## Season Definitions

The script creates a Season column based on the Date field:

| Season | Date Range |
|--------|------------|
| **Winter/Spring** | January 1 - April 15 |
| **Summer** | April 16 - July 31 |
| **Autumn/Winter** | August 1 - December 31 |

## Usage

### 1. Update File Path
Edit the script and update the `file_path` variable:
```r
file_path <- "your_file.csv"
```

### 2. Verify Column Names
Ensure your CSV columns match the expected names:
- `Species`
- `Count`
- `Date`

If your column names differ, update the script accordingly.

### 3. Run the Script
In RStudio or R console:
```r
source("bird_analysis.R")
```

## Output

### Console Output
The script displays three main sections:

1. **Species Statistics** - Overall statistics per species across all seasons
2. **Species x Season Statistics** - Detailed statistics for each species in each season
3. **Summary Report** - Overview of the analysis

### CSV Files Generated

1. **bird_species_analysis.csv**
   - Overall statistics per species
   - Columns: Species, Total_Records, Max_Count, Percentile_95, Records_in_Top_5_Percent

2. **bird_species_season_analysis.csv**
   - Statistics for each species x season combination
   - Columns: Species, Season, Total_Records, Max_Count, Percentile_95, Records_in_Top_5_Percent

### Statistics Explained

For each species (and season):

- **Total_Records**: Number of valid observations
- **Max_Count**: Highest count value recorded
- **Percentile_95**: The count threshold above which the top 5% of observations fall
- **Records_in_Top_5_Percent**: Number of observations in the top 5%

## Troubleshooting

### Date Format Issues
If dates aren't parsing correctly, the script uses R's `as.Date()` function which expects formats like:
- `YYYY-MM-DD` (e.g., 2024-03-15)
- `YYYY/MM/DD` (e.g., 2024/03/15)

For other formats (e.g., DD/MM/YYYY), modify the Date_Parsed line:
```r
Date_Parsed = as.Date(Date, format = "%d/%m/%Y")
```

### Column Name Mismatches
If you get errors about columns not being found, check your CSV column names and update these references in the script:
- `Count` → your count column name
- `Species` → your species column name
- `Date` → your date column name

### Non-Numeric Count Values
The script will report any values that couldn't be converted to numeric in the console output under "Warning: The following values could not be converted to numeric".

## Example Output

```
Species Statistics:
==================

# A tibble: 50 × 5
   Species              Total_Records Max_Count Percentile_95 Records_in_Top_5_Percent
   <chr>                        <int>     <dbl>         <dbl>                    <int>
 1 Great Blue Heron               120       85          75.0                        6
 2 American Robin                 200       50          45.0                       10
 ...

Species x Season Statistics:
============================

# A tibble: 150 × 6
   Species              Season        Total_Records Max_Count Percentile_95 Records_in_Top_5_Percent
   <chr>                <fct>                 <int>     <dbl>         <dbl>                    <int>
 1 American Robin       Winter/Spring            75       45          40.0                        4
 2 American Robin       Summer                   80       50          45.0                        4
 3 American Robin       Autumn/Winter            45       35          32.0                        2
 ...
```

## License

This script is provided as-is for bird observation data analysis.

## Support

For issues or questions about the script, please review the Troubleshooting section above or modify the script to suit your specific data format.
