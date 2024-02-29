import os
from git_handler import GitHandler

git_username = os.environ["GIT_USERNAME"]
git_access_token = os.environ["GIT_ACCESS_TOKEN"]

# Arguments
owner = "TimoKubera"
repo = "pull_request_merge_conflict"
source_branch = "main"
target_branch = "feature"

gi = GitHandler(f"https://{git_username}:{git_access_token}@github.com/{owner}/{repo}.git",
                source_branch,
                target_branch
                )