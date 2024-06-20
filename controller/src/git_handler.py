"""
This module provides the GitHandler class for handling git operations.

The GitHandler class initializes and clones repositories and creates a 
feature branch.
"""
import os
from git import Repo, Git
import shutil
import stat
import time
from uuid import uuid4


class GitHandler:
    """
    A class designed to handle various Git operations such as cloning repositories, managing branches, and committing changes. 

    The GitHandler class provides methods to set up and configure Git settings, manage temporary directories for operations, clone repositories, handle files during merge conflicts, and clean up resources. It is intended to streamline the process of managing Git repositories, particularly in automated environments where operations like handling merge conflicts, committing, and pushing changes need to be executed programmatically.

    Attributes:
        source_branch (str): The name of the source branch in the repository.
        target_branch (str): The name of the target branch in the repository.
        git_user (str): The username for git operations.
        owner (str): The owner of the repository.
        token (str): The personal access token for authentication.
        repo_name (str): The name of the repository.
        pr_number (str): The pull request number associated with the operations.
    """
    _tmp_path = None
    _git = None
    _repo = None
    _owner = ''
    _token = ''
    _repo_name = ''
    _source_branch = None
    _target_branch = None
    _feature_branch = None
    _unique_feature_branch_name = ''
    _pr_number = None
    _unique_id = None

    def get_tmp_path(self):
        """
        Returns the temporary directory path used by the GitHandler.

        This method retrieves the path to the temporary directory where the repository is cloned and managed.
        """
        return self._tmp_path

    def set_credentials(self, email, name):
        """
        Sets the global Git configuration for user email and name.

        This method configures the global Git settings for the user's email and name using the provided email and name parameters.

        Args:
            email (str): The email address to set for the Git user configuration.
            name (str): The name to set for the Git user configuration.
        """
        self._git.config('--global', 'user.email', email)
        self._git.config('--global', 'user.name', name)

    @classmethod
    def initialize(cls, source_branch: str, target_branch: str, git_user:
        str, owner: str, token: str, repo_name: str, pr_number: str):
        """
        Initializes the GitHandler class with the necessary configuration for handling git operations.

        This method sets up the class variables with the provided parameters, creates a unique temporary directory
        for the operations, and prepares the class for subsequent git actions like cloning and creating feature branches.

        Parameters:
            source_branch (str): The name of the source branch in the repository.
            target_branch (str): The name of the target branch in the repository.
            git_user (str): The username for git operations.
            owner (str): The owner of the repository.
            token (str): The personal access token for authentication.
            repo_name (str): The name of the repository.
            pr_number (str): The pull request number associated with the operations.
        """
        project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        cls._unique_id = str(uuid4())
        cls._tmp_path = os.path.join(project_root_dir, '.tmp',
            f'{repo_name}_{cls._unique_id}')
        print('Temporary directory: ' + cls._tmp_path)
        os.makedirs(os.path.dirname(cls._tmp_path), exist_ok=True)
        cls._git = Git(project_root_dir)
        cls._source_branch = f'origin/{source_branch}'
        cls._target_branch = f'origin/{target_branch}'
        cls._git_user = git_user
        cls._owner = owner
        cls._token = token
        cls._repo_name = repo_name
        cls._pr_number = pr_number

    @classmethod
    def clone(cls):
        """
        Clones the repository specified by the class attributes and sets up a feature branch.

        This method performs the following operations:
        - Clones the repository from the specified URL into a temporary directory.
        - Checks out the source branch.
        - Creates and checks out a new feature branch named uniquely based on the pull request number and current timestamp.
        """
        cls._repo = Repo.clone_from(
            'https://{git_username}:{git_access_token}@{git_base_url}/{owner}/{repo}.git'
            .format(git_username=cls._git_user, git_access_token=cls._token,
            git_base_url=os.environ['GIT_BASE_URL'], owner=cls._owner, repo
            =cls._repo_name), cls._tmp_path)
        cls._repo.git.checkout(cls._source_branch)
        cls._unique_feature_branch_name = 'optima/' + str(cls._pr_number
            ) + '/' + str(time.time())
        cls._feature_branch = cls._repo.create_head(cls.
            _unique_feature_branch_name)
        cls._repo.git.checkout(cls._feature_branch)
        print('Creatured feature branch.')
        print('active branch: ' + cls._repo.active_branch.name)

    @classmethod
    def clean_up(cls):
        """
        Cleans up the temporary directory.

        This method iterates over the directories and files in the temporary directory, changes their 
        permissions to make them readable, writable, and executable by the user, and then removes the 
        temporary directory.
        """
        if os.path.exists(cls._tmp_path):
            print('Cleaning up the .tmp directory ...')
            for root, dirs, files in os.walk(cls._tmp_path):
                for dir in dirs:
                    os.chmod(os.path.join(root, dir), stat.S_IRWXU)
                for file in files:
                    os.chmod(os.path.join(root, file), stat.S_IRWXU)
            shutil.rmtree(cls._tmp_path)

    @classmethod
    def commit_and_push(cls, file_paths, commit_msg):
        """
        Performs Git actions such as add, commit, and push.

        This method performs the following Git actions in the downstream repository:
        - Adds the files with the resolved merge conflicts to the staging area.
        - Commits the changes with the commit message generated by the AI model.
        - Pushes the changes to the remote repository, setting the upstream branch to the active branch.
        """
        cls._repo.git.add(file_paths)
        changes = cls._repo.git.diff('--staged')
        if changes:
            cls._repo.git.commit('-m', commit_msg)
            cls._repo.git.push('--set-upstream', 'origin', GitHandler._repo
                .active_branch.name)
            return True
        else:
            return False

    @classmethod
    def write_responses(cls, file_paths, responses):
        """
        Writes the AI's responses (solutions to the merge conflicts) back to the files.

        This method iterates over the _file_paths list and for each file path, it opens the corresponding 
        file in the downstream repository in write mode and writes the corresponding response from the 
        responses list to the file.

        Note: The method assumes that the order of the file paths in _file_paths matches the order of 
        the responses in responses.
        """
        print('Writing responses to files...')
        print(file_paths)
        for i, file_path in enumerate(file_paths):
            with open(os.path.join(cls._tmp_path, file_path), 'w') as file:
                print('Writing to ' + os.path.join(cls._tmp_path, file_path))
                file.write(responses[i])
