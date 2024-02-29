import os
from controller.src.git_handler import GitHandler
from merge_agent.src.merge_git_handler import MergeGitHandler
from merge_agent.src.agent import Agent
from code_quality_agent.src.lint_agent import LintAgent

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

""" Interaction with the Merge Agent"""
mgh = MergeGitHandler()
mag = Agent(gi._repo)


for i, file_path in enumerate(mgh.get_unmerged_filepaths()):
    file_content = mgh.get_f_content(i)
    mag.make_prompt(file_path, file_content)
    print("Ai is solving the merge conflict in " + mgh._unmerged_filepaths[i] + "...")
    resp = mag.solve_merge_conflict()

print("Committing changes...")
mgh.write_responses(mag.get_file_paths(), mag.get_responses())
mag.make_commit_msg()
mgh.git_actions(mag.get_file_paths(), mag.get_commit_msg())

# Temporäer Code-Abschnitt. Soll commited werden
def save_to_file(attribute1, attribute2, attribute3):
    with open("tmp_explanations.txt", "w") as f:
        f.write("\n".join(attribute1))

    with open("tmp_responses.txt", "w") as f:
        f.write("\n".join(attribute2))

    with open("tmp_commit_msg.txt", "w") as f:
        f.write(attribute3)

save_to_file(mag.explanations, mag.responses, mag.commit_msg)

""" Interaction with the Code Quality Agent """
py_lag = LintAgent(directory=gi.get_tmp_path(), language="python")
ja_lag = LintAgent(directory=gi.get_tmp_path(), language="java")

print("Improving code...")
py_lag.improve_code()
ja_lag.improve_code()

print("Writing changes...")
py_lag.write_changes()
ja_lag.write_changes()

print(py_lag)
print()
print(ja_lag)
#TODO print("Committing changes...")