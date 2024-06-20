import os
import csv
import requests
from datetime import datetime, timedelta


def get_changed_files(token: str, git_owner: str, git_repo: str, pr_number: str
    ):
    """
    Get a list of files changed in a pull request.

    Args:
        base_url (str): The base url of your GitHub API.
        token (str): A GitHub Access Token to access the repo.
    """
    url = (
        f"https://{os.environ['GIT_BASE_URL']}/api/v3/repos/{git_owner}/{git_repo}/pulls/{pr_number}/files"
        )
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f'Failed to fetch changed files: {response.content}')
    files = response.json()
    print('Debug: Changed files:')
    changed_files = [file['filename'] for file in files]
    print(changed_files)
    return changed_files


def not_deleted_files(tmp_path, changed_files):
    """
    Identify and return a list of changed files that have not been deleted from the filesystem.

    This function checks each file in the list of changed files to see if it still exists in the given temporary path. It adjusts the path format based on the operating system.

    Args:
        tmp_path (str): The base temporary path where files are stored.
        changed_files (list): A list of paths to files that have been changed.

    Returns:
        list: A list of paths to files that have been changed and still exist in the temporary path.
    """
    if os.name == 'nt':
        tmp_path = tmp_path.replace('/', '\\')
    else:
        tmp_path = tmp_path.replace('\\', '/')
    actually_changed_files = []
    for file in changed_files:
        normpath_tmp = os.path.normpath(tmp_path)
        normpath_file = os.path.normpath(file)
        os.chdir(normpath_tmp)
        if os.path.exists(normpath_file):
            actually_changed_files.append(file)
    return actually_changed_files


def get_pr_branches(username, token, owner, repo, pr_number):
    """
    This function retrieves the source and target branches of a Pull Request.

    Args:
        username (str): The GitHub username.
        token (str): The GitHub token for authentication.
        repo (str): The name of the repository.
        pr_number (int): The number of the Pull Request.

    Returns:
        tuple: A tuple containing the names of the source branch (head) and the target branch (base) of the Pull Request. 
               If the Pull Request does not exist or an error occurs, it returns (None, None).
    """
    base_url = os.environ['GIT_BASE_URL']
    url = f'https://{base_url}/api/v3/repos/{owner}/{repo}/pulls/{pr_number}'
    response = requests.get(url, auth=(username, token))
    if response.status_code == 200:
        data = response.json()
        return data['head']['ref'], data['base']['ref']
    else:
        return None, None


def add_new_entries(db_path, repo_name, pr_number):
    """
    Add a new entry to the database for a pull request.

    This function appends a new entry to a CSV file representing a database. Each entry logs a repository name,
    a pull request number, and the current timestamp.

    Args:
        db_path (str): The file system path to the CSV database file.
        repo_name (str): The name of the repository associated with the pull request.
        pr_number (int): The number of the pull request.

    The function does not return any value.
    """
    normpath_db = os.path.normpath(db_path)
    with open(normpath_db, 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([repo_name, pr_number, datetime.now().isoformat()])


def remove_old_entries(db_path):
    """
    Remove entries from the database that are older than 24 hours.

    This function reads the existing entries from a CSV file, filters out entries that are older than 24 hours,
    and writes the remaining entries back to the CSV file.

    Args:
        db_path (str): The file path to the database CSV file.
    """
    now = datetime.now()
    with open(db_path, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        entries = list(reader)
    entries = [entry for entry in entries if now - datetime.fromisoformat(
        entry[2]) < timedelta(hours=24)]
    with open(db_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(entries)
