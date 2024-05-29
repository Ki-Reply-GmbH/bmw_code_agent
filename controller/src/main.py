import os
import logging
from controller.src.git_handler import GitHandler
from controller.src.helper import not_deleted_files, get_changed_files, get_pr_branches
from merge_agent.src.merge_git_handler import MergeGitHandler
from pull_request_agent.src.pr_git_handler import PRGitHandler
from merge_agent.src.merge_agent import MergeAgent
from code_quality_agent.src.lint_agent import LintAgent
from pull_request_agent.src.pr_agent import PRAgent

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def main(
        json_deployment: str,
        text_deployment: str,
        git_repo: str,
        pr_number: str
        ):
    """ Set up the local git repository """

    # Arguments
    git_user = os.environ["GIT_USERNAME"]
    token = os.environ["GIT_ACCESS_TOKEN"]
    owner = "GCDM"
    repo = git_repo
    source_branch, target_branch = get_pr_branches(
        git_user,
        token,
        owner,
        git_repo,
        pr_number
        )
    file_list = get_changed_files(
        token=token,
        git_owner=owner,
        git_repo=repo,
        pr_number=pr_number
        )

    # Initializing PRGitHandler
    pr_gi = PRGitHandler(pr_number)
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
    pr_gi.create_progress_bar(
        percentage=0,
        status="Processing webhook information."
        )
    
    updated_file_list = not_deleted_files(gi.get_tmp_path(), file_list)

    """ Initialize with the Pull Request Agent """
    pr_agent = PRAgent(json_model=json_deployment, text_model=text_deployment)

    """ Interaction with the Merge Agent"""
    try:
        pr_gi.create_progress_bar(
            percentage=10,
            status="Checking for merge conflicts."
            )
    except:
        pr_agent.report_error("Pull Request Agent failed creating progress bar.")
    
    try:
        mgh = MergeGitHandler()
        mag = MergeAgent(gi._repo, json_model=json_deployment, text_model=text_deployment)

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
    except:
        pr_agent.report_error("Merge Agent failed to solve merge conflicts.")
        merge_commit_and_push = False

    try:
        """ Update the Pull Request Agent's memory """
        if merge_commit_and_push:
            pr_agent.set_memory(
                "merge_agent",
                mag.get_file_paths(),
                mag.get_responses(),
                mag.get_commit_msg()
            )
    except:
        pr_agent.report_error("Pull Request Agent failed to update memory.")

    try:
        """ Interaction with the Code Quality Agent """
        other_file_list = [file for file in updated_file_list if ".java" not in file]
        # Kennzahlen, um den Progress zu berechnen; LintAgent Progress in {x | 0.2 <= x <= 0.9}
        progress_increment_per_file = 70.0 / len(updated_file_list)
        quant_java_files =  len(updated_file_list) - len(other_file_list)

        LOGGER.debug("Interaction with the Code Quality Agent...")
        ja_lag = LintAgent(
            file_list= updated_file_list,
            directory=gi.get_tmp_path(),
            language="java",
            json_model=json_deployment,
            text_model=text_deployment
            )

        LOGGER.debug("Improving Java code...")
        ja_lag.improve_code(pr_gi, 20, progress_increment_per_file)
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
            language="other",
            json_model=json_deployment,
            text_model=text_deployment
            ) 

        LOGGER.debug("Improving other code...")
        other_lag.improve_code(
            pr_gi,
            quant_java_files * progress_increment_per_file + 20,
            progress_increment_per_file
            )
        
        LOGGER.debug("Writing changes...")
        other_lag.write_changes()
        print(other_lag)

        LOGGER.debug("Committing changes...")
        other_lag.make_commit_msg()
        LOGGER.debug("File paths:\n" + str(other_lag.get_file_paths()))
        LOGGER.debug("Commit message:\n" + other_lag.get_commit_msg())
        lint_commit_and_push = lint_commit_and_push or gi.commit_and_push(other_lag.get_file_paths(), other_lag.get_commit_msg())
    except:
        pr_agent.report_error("Code Quality Agent failed to improve code.")
        lint_commit_and_push = False

    pr_gi.create_progress_bar(
        percentage=90,
        status="Updating the pull request comment."
        )

    try:
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
    except:
        pr_agent.report_error("Pull Request Agent failed to update memory.")

    try:
        pr_agent.make_summary()
        pr_agent.make_title()

        pr_agent.write_response()

        LOGGER.debug("Updating pull request...")
        pr_gi.comment_pull_request(pr_agent.get_summary())
    except:
        pr_agent.report_error("Pull Request Agent failed to update pull request.")

if __name__ == "__main__":
    main()