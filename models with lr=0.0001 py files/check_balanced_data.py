import os
import matplotlib.pyplot as plt

# Define the root directories to check
directories = [
    '/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_training/',
    '/content/drive/MyDrive/sipakmed/sipakmed/'
]

# Function to count BMP files recursively in a directory
def count_bmp_files_recursive(root_dir):
    count = 0
    for root, dirs, files in os.walk(root_dir):
        count += sum(1 for file in files if file.endswith('.bmp'))
    return count

def check_balanced_data():
    # Iterate over the directories and count the files
    counts = []
    dir_names = []

    for directory in directories:
        file_count = count_bmp_files_recursive(directory)
        counts.append(file_count)
        dir_names.append(directory)
    
    # Print the counts for the specified directories
    for name, count in zip(dir_names, counts):
        print(f"Directory: {name}, BMP File Count: {count}")

    # Count BMP files in all directories inside both root directories
    original_count = count_bmp_files_recursive('/content/drive/MyDrive/sipakmed/sipakmed/')
    training_count = count_bmp_files_recursive('/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_training/')

    print(f"Total BMP File Count in '/content/drive/MyDrive/sipakmed/sipakmed/': {original_count}")
    print(f"Total BMP File Count in '/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_training/': {training_count}")

    # Create a bar plot
    plt.figure(figsize=(10, 6))
    plt.bar(dir_names + ['Total Original', 'Total Training'], counts + [original_count, training_count], color='skyblue')
    plt.xlabel('Directories')
    plt.ylabel('BMP File Count')
    plt.title('BMP File Counts in Specified Directories')
    plt.xticks(rotation=45, ha='right')

    # Show the plot
    plt.tight_layout()
    plt.show()
