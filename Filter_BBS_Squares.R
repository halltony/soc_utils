# Load necessary libraries
library(sf)
library(dplyr)

# Load the shapefile (replace 'shapefile_path' with the actual path to your shapefile)
shapefile_path <- '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/QGIS Files/ZulClydeRA/ClydeRA.shp'
shapefile <- st_read(shapefile_path)

# Ensure the shapefile's CRS is set
shapefile <- st_transform(shapefile, crs = 4326) # Assuming WGS84 CRS

# Sample data frame with longitude and latitude
# data <- data.frame(
#   id = 1:5,
#   longitude = c(-122.4194, -123.1207, -121.4944, -120.7401, -123.3656),
#   latitude = c(37.7749, 49.2827, 38.5816, 37.4419, 48.4284)
# )

# BBS data on grid
data <- read.csv('/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/All years/BBS/14161736/grid_square_coordinates_lookup.csv')

# Convert the data frame to an sf object
data_sf <- st_as_sf(data, coords = c("ETRS89Long", "ETRS89Lat"), crs = 4326)

# Perform spatial filtering: keep only rows within the shapefile
filtered_data <- data_sf %>%
  st_filter(shapefile)

# Print the filtered data
print(filtered_data)

# If you want the result as a standard data frame
filtered_data_df <- st_drop_geometry(filtered_data)
print(filtered_data_df)

#Write the list of squares to a csv
write.csv(filtered_data_df, file = '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/All years/BBS/14161736/clyde_grid_squares.csv')

bbs_full_df <- read.csv('/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/All years/BBS/14161736/BBS_bird_dataset.csv')

# Filter bbs_full_df based on the gridrefs present in filtered_data
filtered_df <- bbs_full_df %>%
  filter(square %in% filtered_data$square)

# Add a column to decode the BTO species codes
lookup_df <- read.csv('/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/All years/BBS/14161736/species_lookup.csv')
# Join the main data frame with the lookup data frame to decode values
result_df <- filtered_df %>%
  left_join(lookup_df, by = 'species_code')

# Print the filtered data frame
print(result_df)