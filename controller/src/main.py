import os
import logging
import json
from controller.src.git_handler import GitHandler
from controller.src.helper import not_deleted_files
from merge_agent.src.merge_git_handler import MergeGitHandler
from pull_request_agent.src.pr_git_handler import PRGitHandler
from merge_agent.src.merge_agent import MergeAgent
from code_quality_agent.src.lint_agent import LintAgent
from pull_request_agent.src.pr_agent import PRAgent
from controller.src.webhook_handler import WebhookHandler

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def main(event: dict):
    """ Set up the local git repository """

    # Arguments
    git_user = os.environ["GIT_USERNAME"]
    token = os.environ["GIT_ACCESS_TOKEN"]

    # Initialize WebhookHandler
    wh = WebhookHandler(event, "./.webhooks.csv")
    wh.get_changed_files(
        token=token
        )

    if len(wh.owner) == 0:
        LOGGER.debug("No new webhooks.")
        return

    # Information extracted from webhook
    owner = wh.owner
    repo = wh.repo
    source_branch = wh.source_branche
    target_branch = wh.target_branche
    pr_number = wh.pr_number
    file_list = wh.changed_files
    
    # Initializing PRGitHandler
    pr_gi = PRGitHandler(pr_number)
    pr_gi.create_progress_bar(0)
    
    LOGGER.debug("Retrieved information from webhook:\n%s\n%s\n%s\n%s\n%s\n%s\n",
                 owner,
                 repo,
                 source_branch,
                 target_branch,
                 pr_number,
                 str(file_list)
                )
    

    LOGGER.debug("Non-critical environment variables:\n%s\n%s\n%s\n%s\n%s\n",
                 os.environ["OPTIMA-FE-USERNAME"],
                 os.environ["OPTIMA-FE-PASSWORD"],
                 os.environ["JSON-DEPLOYMENT"],
                 os.environ["TEXT-DEPLOYMENT"],
                 os.environ["GIT_BASE_URL"]
                 )
    

    gi = GitHandler()
    gi.initialize(
        source_branch,
        target_branch,
        git_user,
        owner,
        token,
        repo,
        pr_number
        )

    gi.set_credentials(
        email="optima-coding-mentor@bmw.de",
        name="Optima Coding Mentor"
    )
    gi.clean_up()
    gi.clone()

    pr_gi.create_progress_bar(10)

    updated_file_list = not_deleted_files(gi.get_tmp_path(), file_list)
    LOGGER.debug("Updated file list:\n%s\n",
                 str(updated_file_list)
                )

    """ Initialize with the Pull Request Agent """
    pr_agent = PRAgent()

    """ Interaction with the Merge Agent"""
    mgh = MergeGitHandler()
    mag = MergeAgent(gi._repo)

    LOGGER.debug("Initialized GitHandler and Agents")
    for i, file_path in enumerate(mgh.get_unmerged_filepaths()):
        file_content = mgh.get_f_content(i)
        mag.make_prompt(file_path, file_content)
        LOGGER.debug("Ai is solving the merge conflict in %s...", mgh.get_unmerged_filepaths()[i])
        resp = mag.solve_merge_conflict()

    LOGGER.debug("Committing changes...")
    gi.write_responses(mag.get_file_paths(), mag.get_responses())
    mag.make_commit_msg()
    merge_commit_and_push = gi.commit_and_push(mag.get_file_paths(), mag.get_commit_msg())


    """ Update the Pull Request Agent's memory """
    if merge_commit_and_push:
        pr_agent.set_memory(
            "merge_agent",
            mag.get_file_paths(),
            mag.get_responses(),
            mag.get_commit_msg()
        )

    """ Interaction with the Code Quality Agent """
    other_file_list = [file for file in updated_file_list if ".java" not in file]
    # Kennzahlen, um den Progress zu berechnen; LintAgent Progress in {x | 0.2 <= x <= 0.9}
    java_proportion =  0,7 * (len(updated_file_list) / len(other_file_list))
    other_proportion = 0,7 * (1 - java_proportion)
    java_increment_per_file = java_proportion / len(updated_file_list)
    other_increment_per_file = other_proportion / len(other_file_list)

    LOGGER.debug("Interaction with the Code Quality Agent...")
    ja_lag = LintAgent(
        file_list= updated_file_list,
        directory=gi.get_tmp_path(),
        language="java"
        )

    LOGGER.debug("Improving Java code...")
    ja_lag.improve_code(pr_gi, 20, java_increment_per_file)
    LOGGER.debug("Writing changes...")
    ja_lag.write_changes()
    print(ja_lag)

    LOGGER.debug("Committing changes...")
    ja_lag.make_commit_msg()
    LOGGER.debug("File paths:\n" + str(ja_lag.get_file_paths()))
    LOGGER.debug("Commit message:\n" + ja_lag.get_commit_msg())
    lint_commit_and_push = gi.commit_and_push(ja_lag.get_file_paths(), ja_lag.get_commit_msg())

    """
    py_lag = LintAgent(
        file_list= updated_file_list,
        directory=gi.get_tmp_path(),
        language="python"
        )
    LOGGER.debug("Improving Python code...")
    py_lag.improve_code()
    LOGGER.debug("Writing changes...")
    py_lag.write_changes()
    print(py_lag)
    """

    other_lag = LintAgent(
        file_list= other_file_list,
        directory=gi.get_tmp_path(),
        language="other"
        ) 

    LOGGER.debug("Improving other code...")
    other_lag.improve_code(pr_gi, java_proportion*100 + 20, other_increment_per_file)
    LOGGER.debug("Writing changes...")
    other_lag.write_changes()
    print(other_lag)

    LOGGER.debug("Committing changes...")
    other_lag.make_commit_msg()
    LOGGER.debug("File paths:\n" + str(other_lag.get_file_paths()))
    LOGGER.debug("Commit message:\n" + other_lag.get_commit_msg())
    lint_commit_and_push = lint_commit_and_push or gi.commit_and_push(other_lag.get_file_paths(), other_lag.get_commit_msg())

    pr_gi.create_progress_bar(90)

    """" Update the Pull Request Agent's memory """
    LOGGER.debug("Updating the Pull Request Agent's memory...")
    if lint_commit_and_push:
        pr_agent.set_memory(
            "cq_agent",
            ja_lag.get_file_paths(),
            ja_lag.get_responses() +  other_lag.get_responses(),
            ja_lag.get_commit_msg() +  other_lag.get_commit_msg()
        )

    LOGGER.debug(pr_agent)

    pr_agent.make_summary()
    pr_agent.make_title()

    pr_agent.write_response()

    LOGGER.debug("Updating pull request...")
    pr_gi.comment_pull_request(pr_agent.get_summary())

if __name__ == "__main__":
    main()