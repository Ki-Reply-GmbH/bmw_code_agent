import os

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