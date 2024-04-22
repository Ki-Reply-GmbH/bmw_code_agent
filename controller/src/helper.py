import os
import csv
from datetime import datetime, timedelta

def not_deleted_files(tmp_path, changed_files):

    # Check the operating system and format the path accordingly
    if os.name == "nt":  # Windows
        tmp_path = tmp_path.replace("/", "\\")
    else:  # Unix/Linux
        tmp_path = tmp_path.replace("\\", "/")
    
    actually_changed_files = []

    for file in changed_files:
        normpath_tmp = os.path.normpath(tmp_path)
        normpath_file = os.path.normpath(file)
        os.chdir(normpath_tmp)
        if os.path.exists(normpath_file):
            actually_changed_files.append(file)
    
    return actually_changed_files

# Webhook DB interaction
def add_new_entries(db_path, repo_name, pr_number):
    # Normalize the path
    normpath_db = os.path.normpath(db_path)

    # Add the new entry
    with open(normpath_db, "a", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([repo_name, pr_number, datetime.now().isoformat()])

def remove_old_entries(db_path):
    # Get the current time
    now = datetime.now()

    # Read the existing entries
    with open(db_path, "r") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)  # Save the header
        entries = list(reader)

    # Filter out entries older than 24 hours
    entries = [
        entry for entry in entries
        if now - datetime.fromisoformat(entry[2]) < timedelta(hours=24)
    ]

    # Write the remaining entries back to the file
    with open(db_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(entries)