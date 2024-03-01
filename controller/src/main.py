import os
from controller.src.git_handler import GitHandler
from merge_agent.src.merge_git_handler import MergeGitHandler
from merge_agent.src.merge_agent import MergeAgent
from code_quality_agent.src.lint_agent import LintAgent
from pull_request_agent.src.pr_agent import PRAgent

""" Set up the local git repository """

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

""" Initialize with the Pull Request Agent """
pr_agent = PRAgent()

""" Interaction with the Merge Agent"""
mgh = MergeGitHandler()
mag = MergeAgent(gi._repo)


for i, file_path in enumerate(mgh.get_unmerged_filepaths()):
    file_content = mgh.get_f_content(i)
    mag.make_prompt(file_path, file_content)
    print("Ai is solving the merge conflict in " + mgh._unmerged_filepaths[i] + "...")
    resp = mag.solve_merge_conflict()

print("Committing changes...")
gi.write_responses(mag.get_file_paths(), mag.get_responses())
mag.make_commit_msg()
gi.commit_and_push(mag.get_file_paths(), mag.get_commit_msg())

""" Update the Pull Request Agent's memory """
pr_agent.set_memory(
    "merge_agent",
    mag.get_file_paths(),
    mag.get_responses(),
    mag.get_commit_msg()
)

""" Interaction with the Code Quality Agent """
py_lag = LintAgent(directory=gi.get_tmp_path(), language="python")
ja_lag = LintAgent(directory=gi.get_tmp_path(), language="java")

print("Improving code...")
py_lag.improve_code()

print("Writing changes...")
py_lag.write_changes()

print(py_lag)
print()

print("Committing changes...")
py_lag.make_commit_msg()
print("File paths:\n" + str(py_lag.get_file_paths()))
print("Commit message:\n" + py_lag.get_commit_msg())
gi.commit_and_push(py_lag.get_file_paths(), py_lag.get_commit_msg())

"""" Update the Pull Request Agent's memory """
pr_agent.set_memory(
    "cq_agent",
    py_lag.get_file_paths(),
    py_lag.get_responses(),
    py_lag.get_commit_msg()
)

print(pr_agent)

pr_agent.make_summary()
pr_agent.make_title()
pr_agent.write_response()