import os
from merge_agent.src.merge_git_handler import MergeGitHandler
#from merge_agent.src.agent import Agent

git_username = os.environ["GIT_USERNAME"]
git_access_token = os.environ["GIT_ACCESS_TOKEN"]

# Arguments
owner = "TimoKubera"
repo = "pull_request_merge_conflict"
source_branch = "main"
target_branch = "feature"

gi = MergeGitHandler("C:\\Users\\t.kubera\\dev\\bmw\\bmw_code_agent\\.tmp",
                source_branch,
                target_branch
                )
"""
ag = Agent(gi._repo)


for i, file_path in enumerate(gi.get_unmerged_filepaths()):
    file_content = gi.get_f_content(i)
    ag.make_prompt(file_path, file_content)
    print("Ai is solving the merge conflict in " + gi._unmerged_filepaths[i] + "...")
    resp = ag.solve_merge_conflict()
    #ag.git_add_and_commit()

ag.write_responses()
ag.make_commit_msg()
ag.git_actions()
"""

# Temporäer Code-Abschnitt. Wird später in die Controller-Klasse verschoben
def save_to_file(attribute1, attribute2, attribute3):
    with open("../tmp_explanations.txt", "w") as f:
        f.write("\n".join(attribute1))

    with open("../tmp_responses.txt", "w") as f:
        f.write("\n".join(attribute2))

    with open("../tmp_commit_msg.txt", "w") as f:
        f.write(attribute3)

save_to_file(ag.explanations, ag.responses, ag.commit_msg)