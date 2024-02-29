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
    _tmp_path = None
    _repo = None
    _source_branch = None
    _target_branch = None
    _feature_branch = None
    _unique_feature_branch_name = ""

    @classmethod
    def initialize(cls, source_branch: str, target_branch: str):
        project_root_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )
        )
        cls._tmp_path = os.path.join(project_root_dir, ".tmp")
        print("Temporary directory: " + cls._tmp_path)
        cls._source_branch = source_branch
        cls._target_branch = target_branch

    @classmethod
    def clone(cls, repo_url: str):
        cls._repo = Repo.clone_from(repo_url, cls._tmp_path)
        # Feature Branch soll aus der target branch erstellt werden,
        # weil hier der Pull Request erstellt wurde.
        cls._repo.git.checkout(cls._target_branch)
        cls._unique_feature_branch_name = datetime.now().strftime("%Y%m-%d%H-%M%S-") + str(uuid4())
        cls._feature_branch = cls._repo.create_head(cls._unique_feature_branch_name)
        cls._repo.git.checkout(cls._feature_branch)
        print("Creatured feature branch.")
        print("active branch: " + cls._repo.active_branch.name)

    @classmethod
    def clean_up(cls):
        """
        Cleans up the temporary directory.

        This method iterates over the directories and files in the temporary directory, changes their 
        permissions to make them readable, writable, and executable by the user, and then removes the 
        temporary directory.
        """
        if os.path.exists(cls._tmp_path):
            print("Cleaning up the .tmp directory ...")
            for root, dirs, files in os.walk(cls._tmp_path):
                for dir in dirs:
                    os.chmod(os.path.join(root, dir), stat.S_IRWXU)
                for file in files:
                    os.chmod(os.path.join(root, file), stat.S_IRWXU)
            shutil.rmtree(cls._tmp_path)