"""
This module provides the GitHandler class for handling git operations.

The GitHandler class initializes and clones repositories and creates a 
feature branch.
"""
import os
from git import Repo
import shutil
import stat
from datetime import datetime
from uuid import uuid4

class GitHandler:
    """
    A class for handling git operations.

    This class initializes and clones repositories, creates a feature branch, tries to merge the 
    main branch into the feature branch, and gets the file paths and contents of any unmerged files.

    Attributes:
    """
    def __init__(self, repo_url: str, source_branch: str, target_branch: str):
        """
        Initializes a GitHandler instance.

        This method initializes and clones the repositories, creates a feature branch, and initializes 
        the attributes for the merge conflicts. It then runs the workflow, which tries to merge the 
        main branch into the feature branch and gets the file paths and contents of any unmerged files.

        Args:
            downstream_url (str): The URL of the downstream repository.
            upstream_url (str): The URL of the upstream repository.
        """
        # Initializing and cloning the repositories
        self._tmp_path =  os.path.join(os.path.dirname(__file__), ".tmp")
        self._repo = None
        self._source_branch = source_branch
        self._target_branch = target_branch
        self._feature_branch = None
        self._unique_feature_branch_name = ""

        self._initialize_repo(repo_url)

    def _initialize_repo(self, repo_url: str):
        """
        Initializes and clones the repositories and creates a feature branch.

        This method checks if the upstream repository or the downstream repository already exists in 
        the temporary directory. If they do, it cleans up the temporary directory. It then clones the 
        upstream repository and the downstream repository, creates a remote for the upstream repository 
        in the downstream repository, and fetches from the remote.

        It also creates a unique name for the feature branch, creates the feature branch in the 
        downstream repository, and checks out the feature branch.

        Args:
            repo_url (str): The URL of the downstream repository.
            upstream_url (str): The URL of the upstream repository.
        """
        if os.path.exists(self._tmp_path):
            print("Cleaning up the .tmp directory ...")
            self._clean_up()

        self._repo = Repo.clone_from(repo_url, self._tmp_path)
        # Feature Branch soll aus der target branch erstellt werden,
        # weil hier der Pull Request erstellt wurde.
        self._repo.git.checkout(self._target_branch)
        self._unique_feature_branch_name = datetime.now().strftime("%Y%m-%d%H-%M%S-") + str(uuid4())
        self._feature_branch = self._repo.create_head(self._unique_feature_branch_name)
        self._repo.git.checkout(self._feature_branch)
        print("Creatured feature branch.")
        print("active branch: " + self._repo.active_branch.name)

    def _clean_up(self):
        """
        Cleans up the temporary directory.

        This method iterates over the directories and files in the temporary directory, changes their 
        permissions to make them readable, writable, and executable by the user, and then removes the 
        temporary directory.
        """
        for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), ".tmp")):
            for dir in dirs:
                os.chmod(os.path.join(root, dir), stat.S_IRWXU)
            for file in files:
                os.chmod(os.path.join(root, file), stat.S_IRWXU)
        shutil.rmtree(os.path.join(os.path.dirname(__file__), ".tmp"))
