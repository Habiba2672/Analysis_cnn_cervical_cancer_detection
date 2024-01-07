import os
import shutil
import random
# Define the subsets (train, validation, and test) and their ratios
subsets = ["train", "val", "test"]
split_ratios = [0.63, 0.14, 0.23]

# Define the class labels
classes = ["normal", "atypical"]

# Create output directories if they don't exist
output_dir = '/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_training'  # Set your desired output directory
for subset in subsets:
    for class_label in classes:
        subset_dir = os.path.join(output_dir, subset, class_label)
        os.makedirs(subset_dir, exist_ok=True)

# Function to check if a file has already been copied
def has_been_copied(file, destination_subset):
    class_name = "normal" if "normal" in file else "atypical"
    dest_path = os.path.join(output_dir, destination_subset, class_name, os.path.basename(file))
    return os.path.exists(dest_path)

# Function to record copied files
def record_copied_files(copied_files, destination_subset):
    with open(f'copied_files_{destination_subset}.txt', 'a') as file:
        for copied_file in copied_files:
            file.write(copied_file + '\n')

# Get a list of all image file paths
drive_path = '/content/drive/MyDrive/sipakmed/sipakmed/'  # Set your input directory containing image files
file_paths = []
for root, dirs, files in os.walk(drive_path):
    for file in files:
        if file.endswith('.bmp'):
            file_paths.append(os.path.join(root, file))

# Initialize empty lists for train, val, and test files
train_files = []
val_files = []
test_files = []

# Loop through each class, organize files, and split the data
for class_label in classes:
    class_dir = os.path.join(drive_path, class_label)
    file_list = [file for file in file_paths if class_label in file]

    # Shuffle the file list for random sampling
    random.shuffle(file_list)

    # Split the data based on the defined ratios
    num_files = len(file_list)
    split_points = [
        0,
        int(split_ratios[0] * num_files),
        int((split_ratios[0] + split_ratios[1]) * num_files),
        num_files,
    ]

    train_files += file_list[split_points[0]:split_points[1]]
    val_files += file_list[split_points[1]:split_points[2]]
    test_files += file_list[split_points[2]:split_points[3]]

def copy_files(source_files, destination_subset):
    copied_files = []
    for file in source_files:
        if not has_been_copied(file, destination_subset):
            class_name = "normal" if "normal" in file else "atypical"
            dest_path = os.path.join(output_dir, destination_subset, class_name, os.path.basename(file))
            if not os.path.exists(dest_path):
                shutil.copy(file, dest_path)
                copied_files.append(file)
                print(f"Copied {file} to {dest_path}")
            else:
                print(f"File {file} already exists in {destination_subset}")
        else:
            print(f"File {file} has already been copied to {destination_subset}")
    return copied_files





# Define the path to your original dataset directory
original_dataset_path = '/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_train/'

# Get a list of all image files in the original dataset directory and its subfolders
original_files = []
for root, dirs, files in os.walk(original_dataset_path):
    for filename in files:
        if filename.endswith('.bmp'):
            original_files.append(filename)

# Count the number of unique files in the original dataset
original_file_count = len(original_files)

# List files that are in the current dataset but not in the original
extra_files = []
current_dataset_path = '/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_training/'

for root, dirs, files in os.walk(current_dataset_path):
    for filename in files:
        if filename.endswith('.bmp') and filename not in original_files:
            extra_files.append(os.path.join(root, filename))

if extra_files:
    print("Number of extra files found in the current dataset:", len(extra_files))
    print("Duplicated files found in the current dataset:")
    for file in extra_files:
        print(file)

    # Prompt the user for confirmation before removal
    user_confirmation = input("Do you want to remove these duplicated files? (yes/no): ")

    if user_confirmation.lower() == "yes":
        # Remove the duplicated files
        for extra_file in extra_files:
            os.remove(extra_file)
        print("Duplicated files have been removed.")
    else:
        print("No files have been removed. Your dataset is safe.")
else:
    print("No duplicated files found in the current dataset.")
