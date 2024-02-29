import os
from controller.src.git_handler import GitHandler
from merge_agent.src.merge_git_handler import MergeGitHandler

git_username = os.environ["GIT_USERNAME"]
git_access_token = os.environ["GIT_ACCESS_TOKEN"]

# Arguments
owner = "TimoKubera"
repo = "pull_request_merge_conflict"
source_branch = "main"
target_branch = "feature"

gi = GitHandler()
gi.initialize(
    source_branch,
    target_branch
    )
gi.clean_up()
gi.clone(f"https://{git_username}:{git_access_token}@github.com/{owner}/{repo}.git")

mgh = MergeGitHandler()