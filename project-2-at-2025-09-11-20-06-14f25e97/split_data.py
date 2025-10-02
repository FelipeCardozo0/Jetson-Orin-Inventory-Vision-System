import os
import random
import shutil

# --- CONFIGURATION ---
# Path to the folder containing the original 'images' and 'labels' folders.
# Since the script is in the same folder, '.' means 'the current folder'.
SOURCE_DIR = '.' 

# Path for the new directory where the split dataset will be saved.
OUTPUT_DIR = './pokebowl_dataset'

# Percentage of data to use for validation (0.2 means 20%).
VAL_SPLIT_RATIO = 0.2
# ---------------------

def get_image_extension(image_dir, filename_no_ext):
    """Finds the correct image extension (.jpg, .png, etc.)."""
    for ext in ['.jpg', '.jpeg', '.png']:
        if os.path.exists(os.path.join(image_dir, filename_no_ext + ext)):
            return ext
    return None

def split_dataset():
    """
    Splits the dataset into training and validation sets and organizes
    them into the required YOLOv8 folder structure.
    """
    print("Starting dataset split...")

    images_source_path = os.path.join(SOURCE_DIR, 'images')
    labels_source_path = os.path.join(SOURCE_DIR, 'labels')

    # Get a list of all image filenames (without extension)
    all_filenames = [os.path.splitext(f)[0] for f in os.listdir(images_source_path)]
    random.shuffle(all_filenames)

    # Calculate the split index
    split_index = int(len(all_filenames) * VAL_SPLIT_RATIO)
    
    # Divide the filenames
    val_filenames = all_filenames[:split_index]
    train_filenames = all_filenames[split_index:]

    print(f"Total images: {len(all_filenames)}")
    print(f"Training images: {len(train_filenames)}")
    print(f"Validation images: {len(val_filenames)}")

    # Create the new directory structure
    for folder in ['train', 'val']:
        os.makedirs(os.path.join(OUTPUT_DIR, 'images', folder), exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_DIR, 'labels', folder), exist_ok=True)

    # Function to copy files
    def copy_files(filenames, set_type):
        for filename in filenames:
            ext = get_image_extension(images_source_path, filename)
            if ext is None:
                print(f"Warning: Could not find image for label '{filename}.txt'. Skipping.")
                continue

            # Copy image file
            shutil.copy(
                os.path.join(images_source_path, filename + ext),
                os.path.join(OUTPUT_DIR, 'images', set_type, filename + ext)
            )
            # Copy label file
            shutil.copy(
                os.path.join(labels_source_path, filename + '.txt'),
                os.path.join(OUTPUT_DIR, 'labels', set_type, filename + '.txt')
            )

    # Copy files to their new homes
    print("\nCopying training files...")
    copy_files(train_filenames, 'train')
    
    print("Copying validation files...")
    copy_files(val_filenames, 'val')

    print("\n-------------------------")
    print("Dataset split complete!")
    print(f"New dataset created at: {os.path.abspath(OUTPUT_DIR)}")
    print("-------------------------")


if __name__ == '__main__':
    split_dataset()