import os
import shutil
import random
import imports  # Ensure this module contains all necessary libraries like torch, PIL.Image, etc.

# Constants
IMAGE_HEIGHT = 125
IMAGE_WIDTH = 125
BASE_PATH = "/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_training/"
DATA_PATH = os.path.join(BASE_PATH, "train")
SAVE_PATH = os.path.join(BASE_PATH, "preprocessed_classified/")

# Helper functions

# Helper functions

def get_processed_files(original_files, save_path):
    processed_files = []
    for orig in original_files:
        processed = get_processed_path(orig, save_path)
        if os.path.exists(processed):
            processed_files.append(processed)
    return processed_files

def get_processed_path(orig_path, save_path):
    filename = os.path.basename(orig_path)
    processed_name = f"{filename.replace('.bmp', '_processed.pt')}"
    return os.path.join(save_path, processed_name)

def is_bmp_file(filepath):
    return filepath.lower().endswith('.bmp')

def load_processed_images(processed_paths):
    X = []
    for p in processed_paths:
        img = torch.load(p)
        X.append(img)
    return torch.stack(X)

def load_and_process_images(original_files, data_path, transform, save_path):
    X_normal = []
    X_atypical = []

    for orig in original_files:
        if not is_bmp_file(orig):
            continue  # Skip non-BMP files

        img = Image.open(orig)
        img = transform(img)
        save_name = get_processed_path(orig, save_path)

        # Classify based on the subfolder
        class_label = "normal" if "normal" in orig else "atypical"
        class_save_path = os.path.join(save_path, class_label)

        os.makedirs(class_save_path, exist_ok=True)
        torch.save(img, os.path.join(class_save_path, os.path.basename(save_name)))

        # Append to the respective lists
        if class_label == "normal":
            X_normal.append(img)
        else:
            X_atypical.append(img)

    return torch.stack(X_normal), torch.stack(X_atypical)
# Check for subfolders "Normal" and "Atypical" inside "train"
if not (os.path.exists(os.path.join(DATA_PATH, "normal")) and os.path.exists(os.path.join(DATA_PATH, "atypical"))):
    print("Error: The 'train' directory does not contain the expected subfolders 'normal' and 'atypical'.")
    exit()

# Prompt to apply data processing
apply_processing = input("Do you want to apply data processing? (y/n): ").lower() == 'y'

if apply_processing:
    # Transform for data augmentation during processing
    transform = imports.transforms.Compose([
        imports.transforms.Resize((IMAGE_HEIGHT, IMAGE_WIDTH)),
        imports.transforms.RandomHorizontalFlip(),
        imports.transforms.RandomRotation(degrees=15),
        imports.transforms.ToTensor(),
        imports.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Get list of original image files
    original_files = []
    for root, dirs, files in os.walk(DATA_PATH):
        for filename in files:
            if filename.endswith(".bmp"):
                original_files.append(os.path.join(root, filename))

    # Print the number of original images
    print("Number of original images:", len(original_files))

    # Check for processed images
    processed_files = get_processed_files(original_files, SAVE_PATH)
    if len(processed_files) == len(original_files):
        print("Using existing processed images")
        augmentation_info = "with augmentation" if 'Random' in str(transform) else "without augmentation"
        print(f"Images were processed {augmentation_info}")
        X_train_normal, X_train_atypical = load_and_process_images(original_files, DATA_PATH, transform, SAVE_PATH)
    else:
        print("Processing images...")
        augmentation_info = "with augmentation" if 'Random' in str(transform) else "without augmentation"
        print(f"Images are being processed {augmentation_info}")
        X_train_normal, X_train_atypical = load_and_process_images(original_files, DATA_PATH, transform, SAVE_PATH)

        # Print the number of processed images
        print("Number of processed images (normal):", len(X_train_normal))
        print("Number of processed images (atypical):", len(X_train_atypical))

        if len(X_train_normal) + len(X_train_atypical) != len(original_files):
            print("Error: Mismatch between the number of processed and original images.")
else:
    print("Data processing skipped.")

# Print the number of images in each class after moving
normal_dir = os.path.join(SAVE_PATH, "normal")
atypical_dir = os.path.join(SAVE_PATH, "atypical")
print("Number of images in 'normal' class:", len(os.listdir(normal_dir)))
print("Number of images in 'atypical' class:", len(os.listdir(atypical_dir)))
