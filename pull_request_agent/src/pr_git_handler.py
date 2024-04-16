import requests
import json
import re
import os
import logging
from controller.src.git_handler import GitHandler

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class PRGitHandler(GitHandler):
    def __init__(self, pr_number) -> None:
        self._pr_number = pr_number
        self.comment_id = None

    def get_pr_number(self):
        return self._pr_number

    def create_or_update_comment(self, comment: str):
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "token {token}".format(token=self._token)
        }
        LOGGER.debug("Comment ID: " + str(self.comment_id))
        LOGGER.debug("create_or_update_comment: " + comment)

        if self.comment_id is None:
            # Create a new comment
            url = "https://" + os.environ["GIT_BASE_URL"] + "/api/v3/repos/{owner}/{repo}/issues/{issue_number}/comments".format(
                owner=self._owner,
                repo=self._repo_name,
                issue_number=self._pr_number  # Pull requests are considered as issues in terms of comments
            )
            data = {"body": comment}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 201:
                LOGGER.debug("Response:")
                LOGGER.debug(response.json())
                self.comment_id = response.json().get("id")
            else:
                LOGGER.debug(f"Failed to create comment: {response.status_code}, {response.text}")
        else:
            # Update the existing comment
            url = "https://" + os.environ["GIT_BASE_URL"] + "/api/v3/repos/{owner}/{repo}/issues/comments/{comment_id}".format(
                owner=self._owner,
                repo=self._repo_name,
                comment_id=self.comment_id 
            )
            data = {"body": comment}
            response = requests.patch(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                LOGGER.debug("Response:")
                LOGGER.debug(response.json())
                LOGGER.debug("Comment updated successfully.")
            else:
                LOGGER.debug(f"Failed to update comment: {response.status_code}, {response.text}")

    def comment_pull_request(self, comment: str):
        comment += "\n\nPlease review the changes on the branch {}.".format(
            self._unique_feature_branch_name
            )
        comment = self.shorten_file_paths(comment)
        self.create_or_update_comment(comment)

    def create_progress_bar(self, percentage):
        # Define the length of the progress bar
        bar_length = 20

        # Calculate the number of progress blocks
        progress_blocks = int(percentage / 100 * bar_length)

        # Create the progress bar
        progress_bar = "[" + "#" * progress_blocks + "-" * (bar_length - progress_blocks) + "]"

        # Add the percentage to the progress bar
        progress_bar += " {:.1f}%".format(percentage)

        self.create_or_update_comment(progress_bar)

    def shorten_file_paths(self, input_string):
        """
        Shortens file paths in the LLM response. The file path should start 
        with the repo name and should not contain a unique id.
        """
        # Extract unique IDs from the input string
        unique_ids = set(re.findall(r"bmw_code_agent\/\.tmp\/[^_]+_([^\/]+)", input_string))

        # Iterate over each unique ID
        for unique_id in unique_ids:
            # Define the pattern to search for and the replacement pattern
            pattern = r"(\/?bmw_code_agent\/\.tmp\/)([^_]+)_(" + re.escape(unique_id) + ")(\/.*)"
            replacement = r"\2\4"

            # Continuously apply the replacement until no more matches are found
            while True:
                input_string, num_substitutions = re.subn(pattern, replacement, input_string)
                if num_substitutions == 0:
                    break

        return input_string