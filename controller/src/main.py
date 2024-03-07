import os
from controller.src.git_handler import GitHandler
from merge_agent.src.merge_git_handler import MergeGitHandler
from pull_request_agent.src.pr_git_handler import PRGitHandler
from merge_agent.src.merge_agent import MergeAgent
from code_quality_agent.src.lint_agent import LintAgent
from pull_request_agent.src.pr_agent import PRAgent

""" Set up the local git repository """

# Arguments
git_user = os.environ["GIT_USERNAME"]
token = os.environ["GIT_ACCESS_TOKEN"]

# Information extracted from webhook
owner = "TimoKubera"
repo = "pull_request_merge_conflict"
source_branch = "main"
target_branch = "feature"

gi = GitHandler()
gi.initialize(
    source_branch,
    target_branch,
    git_user,
    owner,
    token,
    repo
    )
gi.clean_up()
gi.clone()

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
print("Interaction with the Code Quality Agent...")
#py_lag = LintAgent(directory=gi.get_tmp_path(), language="python")
ja_lag = LintAgent(directory=gi.get_tmp_path(), language="java-local")

print("Improving code...")
ja_lag.improve_code()

print("Writing changes...")
ja_lag.write_changes()

print(ja_lag)
print()

print("Committing changes...")
ja_lag.make_commit_msg()
print("File paths:\n" + str(ja_lag.get_file_paths()))
print("Commit message:\n" + ja_lag.get_commit_msg())
gi.commit_and_push(ja_lag.get_file_paths(), ja_lag.get_commit_msg())

"""" Update the Pull Request Agent's memory """
print("Updating the Pull Request Agent's memory...")
pr_agent.set_memory(
    "cq_agent",
    ja_lag.get_file_paths(),
    ja_lag.get_responses(),
    ja_lag.get_commit_msg()
)

print(pr_agent)

pr_agent.make_summary()
pr_agent.make_title()
pr_agent.write_response()

print("Updating pull request...")
#TODO dynamisch ermitteln
pr_number = 2
pr_gi = PRGitHandler(pr_number)
resp = pr_gi.comment_pull_request(pr_agent.get_summary())
print(resp)