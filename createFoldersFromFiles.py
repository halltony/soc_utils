import os
import shutil

def organize_files_by_prefix(directory):
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return
    
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    prefix_dict = {}
    
    for file in files:
        prefix = file.split('.')[0]  # Extract prefix before the first period
        if prefix not in prefix_dict:
            prefix_dict[prefix] = []
        prefix_dict[prefix].append(file)
    
    for prefix, files in prefix_dict.items():
        folder_path = os.path.join(directory, prefix)
        os.makedirs(folder_path, exist_ok=True)
        
        for file in files:
            src = os.path.join(directory, file)
            dest = os.path.join(folder_path, file)
            shutil.move(src, dest)
    
    print("Files organized successfully.")

# Example usage
directory = '/Users/Tony/Library/CloudStorage/GoogleDrive-clydesocdiscussion@gmail.com/My Drive/SOC Where to Watch Birds/Shape files/Clyde SSSIs'  # Change this to your target folder
organize_files_by_prefix(directory)
