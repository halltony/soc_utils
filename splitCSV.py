import pandas as pd

# Load the large CSV file
df = pd.read_csv('/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/2024/RSPB 2024-2025/Non_ARM_2024_BirdTrack_Import.csv')

# Set the number of rows per file
chunk_size = 1000

# Loop and save chunks
for i, chunk in enumerate(pd.read_csv('/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/Clyde Bird Reports/2024/RSPB 2024-2025/Non_ARM_2024_BirdTrack_Import.csv', chunksize=chunk_size)):
  chunk.to_csv(f"output_part_{i+1}.csv", index=False)
