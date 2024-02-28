import os
from git_handler import GitHandler
from agent import Agent

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
"""
ag = Agent(gi._downstream, gi._upstream)


for i, file_path in enumerate(gi.get_unmerged_filepaths()):
    file_content = gi.get_f_content(i)
    ag.make_prompt(file_path, file_content)
    print("Ai is solving the merge conflict in " + gi._unmerged_filepaths[i] + "...")
    resp = ag.solve_merge_conflict()
    #ag.git_add_and_commit()

ag.write_responses()
ag.make_commit_msg()
ag.git_actions()
ag.create_pull_request()
"""
#gi.delete_feature_branch() If we delete this branch, the pull request will be closed.
"""
print()
print("Press any key to save the files without merge conflicts.")
input()
writing_agent = WriteAgent()
writing_agent.get_code("./responses.csv")
writing_agent.save_code_to_file()
"""