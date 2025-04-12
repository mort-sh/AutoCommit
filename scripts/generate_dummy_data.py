import os
import random
import string
import datetime

DUMMY_DATA_DIR = "dummy_test_data"
MAX_FILES = 10
MAX_LINES_PER_FILE = 200
MAX_LINE_LENGTH = 80

def get_random_string(length):
    """Generates a random string of fixed length."""
    letters = string.ascii_lowercase + string.digits + " " * 10 # More spaces
    return ''.join(random.choice(letters) for i in range(length))

def create_dummy_file(dir_path):
    """Creates a new dummy file with random content."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")

    existing_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    if len(existing_files) >= MAX_FILES:
        print("Max number of dummy files reached. Skipping creation.")
        return

    file_number = 1
    while True:
        filename = f"dummy_file_{file_number}.txt"
        filepath = os.path.join(dir_path, filename)
        if not os.path.exists(filepath):
            break
        file_number += 1

    num_lines = random.randint(5, MAX_LINES_PER_FILE)
    timestamp = datetime.datetime.now().isoformat()
    content = [f"# Created: {timestamp}\n"]
    for _ in range(num_lines):
        line_len = random.randint(10, MAX_LINE_LENGTH)
        content.append(get_random_string(line_len) + "\n")

    try:
        with open(filepath, "w") as f:
            f.writelines(content)
        print(f"Created dummy file: {filepath}")
    except IOError as e:
        print(f"Error creating file {filepath}: {e}")


def modify_dummy_file(dir_path):
    """Modifies an existing dummy file by appending random content."""
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} does not exist. Cannot modify files.")
        return

    dummy_files = [f for f in os.listdir(dir_path) if f.startswith("dummy_file_") and f.endswith(".txt")]
    if not dummy_files:
        print("No dummy files found to modify.")
        # Maybe create one instead?
        print("Attempting to create a file instead.")
        create_dummy_file(dir_path)
        return

    file_to_modify = random.choice(dummy_files)
    filepath = os.path.join(dir_path, file_to_modify)
    timestamp = datetime.datetime.now().isoformat()
    num_lines_to_add = random.randint(1, 10)
    content_to_add = [f"\n# Modified: {timestamp}\n"]
    for _ in range(num_lines_to_add):
        line_len = random.randint(10, MAX_LINE_LENGTH)
        content_to_add.append(get_random_string(line_len) + "\n")

    try:
        with open(filepath, "a") as f:
            f.writelines(content_to_add)
        print(f"Modified dummy file: {filepath}")
    except IOError as e:
        print(f"Error modifying file {filepath}: {e}")


def delete_dummy_file(dir_path):
    """Deletes a random dummy file."""
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} does not exist. Cannot delete files.")
        return

    dummy_files = [f for f in os.listdir(dir_path) if f.startswith("dummy_file_") and f.endswith(".txt")]
    if not dummy_files:
        print("No dummy files found to delete.")
        return

    file_to_delete = random.choice(dummy_files)
    filepath = os.path.join(dir_path, file_to_delete)

    try:
        os.remove(filepath)
        print(f"Deleted dummy file: {filepath}")
    except OSError as e:
        print(f"Error deleting file {filepath}: {e}")

def main():
    """Main function to randomly perform an action."""
    # Ensure the directory exists before checking its contents
    if not os.path.exists(DUMMY_DATA_DIR):
        os.makedirs(DUMMY_DATA_DIR)
        print(f"Created directory: {DUMMY_DATA_DIR}")
        # If we just created it, definitely create a file
        print("Performing action: create_dummy_file")
        create_dummy_file(DUMMY_DATA_DIR)
        return

    actions = [create_dummy_file, modify_dummy_file, delete_dummy_file]
    # Bias towards creation/modification if few/no files exist
    current_files = len([f for f in os.listdir(DUMMY_DATA_DIR) if os.path.isfile(os.path.join(DUMMY_DATA_DIR, f))])

    if current_files == 0:
        weights = [1.0, 0.0, 0.0] # Must create
    elif current_files < 3:
         weights = [0.6, 0.4, 0.0] # Higher chance to create/modify, no delete yet
    elif current_files >= MAX_FILES:
         weights = [0.0, 0.5, 0.5] # Cannot create, only modify/delete
    else:
         weights = [0.4, 0.4, 0.2] # Balanced

    chosen_action = random.choices(actions, weights=weights, k=1)[0]

    print(f"Performing action: {chosen_action.__name__}")
    chosen_action(DUMMY_DATA_DIR)

if __name__ == "__main__":
    main()
