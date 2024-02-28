"""
This module provides the GitHandler class for handling git operations.

The GitHandler class initializes and clones repositories, creates a feature branch, tries to merge 
the main branch into the feature branch, and gets the file paths and contents of any unmerged files.
"""
import os
from git import Repo, GitCommandError
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

        """
        # Initializing the attributes for the merge conflicts
        self._unmerged_filepaths = []
        self._unmerged_filecontents = []

        self._run_workflow()
        """

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
        print("Cloned main repo locally.")

        self._unique_feature_branch_name = datetime.now().strftime("%Y%m-%d%H-%M%S-") + str(uuid4())
        self._feature_branch = self._repo.create_head(self._unique_feature_branch_name, self._repo.refs.main)
        self._repo.git.checkout(self._feature_branch)
        print("Creatured feature branch.")
        print("active branch: " + self._repo.active_branch.name)

    def _run_workflow(self):
        """
        Runs the workflow for merging the main branch into the feature branch and getting the file paths 
        and contents of any unmerged files.

        This method tries to merge the main branch into the feature branch, analyses the files in the 
        downstream repository, prints the file paths of any unmerged files, and gets the contents of 
        any unmerged files.
        """
        self._try_to_merge()
        self._analyse_files()
        self._print_unmerged_files()
        self._get_merge_conflicts()

    def _analyse_files(self):
        """
        Analyses the files in the downstream repository and gets the file paths of any unmerged files.

        This method iterates over the unmerged blobs in the index of the downstream repository and 
        adds the file paths of any unmerged blobs to the _unmerged_filepaths attribute.
        """
        for path in self._downstream.index.unmerged_blobs():
            self._unmerged_filepaths += [path]

    def _get_merge_conflicts(self):
        """
        Gets the contents of any unmerged files.

        This method iterates over the file paths in the _unmerged_filepaths attribute, opens each file, 
        reads its content, and adds the content to the _unmerged_filecontents attribute. It replaces 
        the unique feature branch name in the content with "feature_branch" to make the content 
        comparable using the cache.
        """
        for path in self._unmerged_filepaths:
            full_path = os.path.join(self._tmp_downstream_path, path).replace("\\","/")    # Backslashes aus dem path ersetzen, damit es einheitlich ist
            with open(full_path) as f:
                file_content = f.read()

            self._unmerged_filecontents += [
                file_content.replace(
                    self._unique_feature_branch_name,
                    "feature_branch"
                    )
                ] #to make the file content comparable using the cache

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
    
    def _try_to_merge(self):
        """
        Tries to merge the main branch into the feature branch.

        This method tries to merge the main branch into the feature branch in the downstream repository. 
        If the merge is successful, it returns False. If a GitCommandError is raised, it returns True.

        Returns:
            bool: False if the merge is successful, True if a GitCommandError is raised.
        """
        try:
            self._downstream.git.merge(self._downstream.refs.main)
            return False
        except GitCommandError as e:
            return True
        
    def get_unmerged_filepaths(self):
        """
        Gets the file paths of any unmerged files.

        This method returns the _unmerged_filepaths attribute, which is a list of the file paths of 
        any unmerged files in the downstream repository.

        Returns:
            list of str: The file paths of any unmerged files.
        """
        return self._unmerged_filepaths

    def get_f_content(self, index: int):
        """
        Gets the content of an unmerged file.

        This method returns the content of the unmerged file at the given index in the 
        _unmerged_filecontents attribute.

        Args:
            index (int): The index of the unmerged file.

        Returns:
            str: The content of the unmerged file.
        """
        return self._unmerged_filecontents[index]

    def _print_unmerged_files(self):
        """
        Prints the file paths of any unmerged files.

        This method iterates over the file paths in the _unmerged_filepaths attribute and prints each 
        file path. It prints a message before and after printing the file paths.
        """
        print("\nFound merge conflicts in:")
        for path in self.get_unmerged_filepaths():
            print(path)
        print()