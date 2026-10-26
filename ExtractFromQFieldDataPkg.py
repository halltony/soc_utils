import os
import geopandas as gpd
import pandas as pd

def extract_qfield_to_csv(input_folder, output_folder):
    """
    Scans a folder for QField GeoPackages, extracts layers, 
    and saves them as CSV files.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")

    # Find all GeoPackages in the input folder
    gpkg_files = [f for f in os.listdir(input_folder) if f.endswith('.gpkg')]
    
    if not gpkg_files:
        print("No .gpkg files found in the specified folder.")
        return

    for gpkg in gpkg_files:
        gpkg_path = os.path.join(input_folder, gpkg)
        print(f"\nProcessing database: {gpkg}")
        
        # 1. Discover all layers (spatial and non-spatial tables) inside the GPKG
        try:
            from pyogrio import list_layers
            layers = [name for name, geom_type in list_layers(gpkg_path)]
        except ImportError:
            # Fallback if fiona isn't directly accessible
            print("Ensure 'fiona' or 'pyogrio' is installed to list layers.")
            continue

        for layer_name in layers:
            print(f" -> Extracting layer: {layer_name}")
            
            try:
                # Read layer using GeoPandas
                gdf = gpd.read_file(gpkg_path, layer=layer_name)
                
                # Check if the layer actually has spatial geometry data
                if gdf.geometry.notnull().any():
                    # Extract X and Y coordinates explicitly for the CSV if points
                    if (gdf.geometry.geom_type == 'Point').all():
                        gdf['longitude'] = gdf.geometry.x
                        gdf['latitude'] = gdf.geometry.y
                    else:
                        # For lines/polygons, save WKT (Well-Known Text) string representation
                        gdf['wkt_geometry'] = gdf.geometry.apply(lambda geom: geom.wkt if geom else None)
                
                # Convert to a standard Pandas DataFrame and drop the active geometry object
                df = pd.DataFrame(gdf.drop(columns='geometry', errors='ignore'))
                
                # 2. Define the output CSV name
                csv_filename = f"{os.path.splitext(gpkg)[0]}_{layer_name}.csv"
                csv_path = os.path.join(output_folder, csv_filename)
                
                # Save to CSV
                df.to_csv(csv_path, index=False, encoding='utf-8')
                print(f"    Saved successfully to: {csv_filename}")
                
            except Exception as e:
                print(f"    Error processing layer {layer_name}: {e}")
                # Several layers in the VSAS data package error but are not part of the survey data and can be ignored.  

# --- CONFIGURATION & RUN ---
if __name__ == "__main__":
    # Replace these paths with your folder locations
    TRANSFER_FOLDER = r'/Users/Tony/Library/CloudStorage/GoogleDrive-ajhall42@gmail.com/My Drive/VSAS/Surveys/Oban to Colonsay 23102026'
    EXPORT_FOLDER = r'/Users/Tony/Desktop'
    
    extract_qfield_to_csv(TRANSFER_FOLDER, EXPORT_FOLDER)
