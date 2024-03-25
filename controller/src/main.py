import os
import logging
import json
from controller.src.git_handler import GitHandler
from merge_agent.src.merge_git_handler import MergeGitHandler
from pull_request_agent.src.pr_git_handler import PRGitHandler
from merge_agent.src.merge_agent import MergeAgent
from code_quality_agent.src.lint_agent import LintAgent
from pull_request_agent.src.pr_agent import PRAgent
from controller.src.webhooks.webhook_handler import WebhookHandler

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
        base_url="https://atc-github.azure.cloud.bmw/api/v3",
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
    
    LOGGER.debug("Retrieved information from webhook:\n%s\n%s\n%s\n%s\n%s\n",
                 owner,
                 repo,
                 source_branch,
                 target_branch,
                 pr_number
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
    gi.commit_and_push(mag.get_file_paths(), mag.get_commit_msg())

    """ Update the Pull Request Agent's memory """
    pr_agent.set_memory(
        "merge_agent",
        mag.get_file_paths(),
        mag.get_responses(),
        mag.get_commit_msg()
    )

    """ Interaction with the Code Quality Agent """
    #TODO Changed files (im PR) übergeben und nur die changed files anpassen.
    LOGGER.debug("Interaction with the Code Quality Agent...")
    demo_directory = os.path.join(gi.get_tmp_path(), "demo")
    ja_lag = LintAgent(directory=demo_directory, language="java")

    LOGGER.debug("Improving code...")
    ja_lag.improve_code()

    LOGGER.debug("Writing changes...")
    ja_lag.write_changes()

    print(ja_lag)

    LOGGER.debug("Committing changes...")
    ja_lag.make_commit_msg()
    LOGGER.debug("File paths:\n" + str(ja_lag.get_file_paths()))
    LOGGER.debug("Commit message:\n" + ja_lag.get_commit_msg())
    gi.commit_and_push(ja_lag.get_file_paths(), ja_lag.get_commit_msg())

    """" Update the Pull Request Agent's memory """
    LOGGER.debug("Updating the Pull Request Agent's memory...")
    pr_agent.set_memory(
        "cq_agent",
        ja_lag.get_file_paths(),
        ja_lag.get_responses(),
        ja_lag.get_commit_msg()
    )

    LOGGER.debug(pr_agent)

    pr_agent.make_summary()
    pr_agent.make_title()
    pr_agent.write_response()

    LOGGER.debug("Updating pull request...")
    pr_gi = PRGitHandler(pr_number)
    resp = pr_gi.comment_pull_request(pr_agent.get_summary())
    LOGGER.debug(resp)

if __name__ == "__main__":
    main()