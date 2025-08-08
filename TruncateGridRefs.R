# Load packages
library(readxl)
library(writexl)
library(stringr)

target_column <- "Abundance"

# Function to convert to 4-figure grid ref
convert_to_4_fig <- function(grid_ref) {
  grid_ref <- toupper(str_replace_all(grid_ref, "\\s+", ""))  # Remove spaces and uppercase
  
  if (nchar(grid_ref) < 4) return(NA)  # Too short to be valid
  
  prefix <- substr(grid_ref, 1, 2)
  digits <- substr(grid_ref, 3, nchar(grid_ref))
  
  if (nchar(digits) %% 2 != 0 || nchar(digits) == 0) return(NA)
  
  half_len <- nchar(digits) / 2
  easting <- substr(digits, 1, half_len)
  northing <- substr(digits, half_len + 1, nchar(digits))
  
  # Pad with zeros if shorter than 5 digits
  easting <- str_pad(easting, 5, side = "right", pad = "0")
  northing <- str_pad(northing, 5, side = "right", pad = "0")
  
  # Truncate to 1 digits each
  e4 <- substr(easting, 1, 2)
  n4 <- substr(northing, 1, 2)
  
  return(paste0(prefix, e4,n4))
}

# Function to extract only the number at the start
extract_leading_number <- function(x) {
  matches <- regmatches(x, regexpr("^\\d+", x))
  return(ifelse(length(matches) > 0, matches, NA))
}

# === Step 1: Load Excel file ===
input_path <- '/Users/Tony/Downloads/RW-July2025.xlsx'       # <- Change this to your file name
sheet_name <- 'R6_birds'                         # Or specify sheet, e.g., "Sheet1"

# Read the spreadsheet
df <- read_excel(input_path, sheet = sheet_name)
names(df)[names(df) == "Spatial Ref"] <- "SpatialRef"

# === Step 2: Convert grid references ===
# Assume the column is named "GridRef" (adjust if different)
df$SpatialRef_4fig <- sapply(df$SpatialRef, convert_to_4_fig)

# Apply the function to the target column
df[[target_column]] <- sapply(df[[target_column]], extract_leading_number)

# === Step 3: Write output to new Excel file ===
output_path <- '/Users/Tony/Downloads/RW_July2025_converted.xlsx'
write_xlsx(df, output_path)

cat("✅ Conversion complete. Output saved to:", output_path, "\n")