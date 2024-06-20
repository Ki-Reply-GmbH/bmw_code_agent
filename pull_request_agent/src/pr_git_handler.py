import requests
import json
import re
import os
import logging
from controller.src.git_handler import GitHandler
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class PRGitHandler(GitHandler):
    """
    A class designed to handle various operations related to pull requests on a version control system. The PRGitHandler class provides functionalities to manage comments, update progress, and manipulate text related to pull requests. It is initialized with a specific pull request number and offers methods to retrieve this number, create or update comments, add comments with additional information, create visual progress indicators, and shorten file paths within text content.

    This class is particularly useful for automating interactions with pull requests, such as posting updates, managing review comments, and enhancing readability of content in version control scenarios.
    """

    def __init__(self, pr_number) ->None:
        """
        Initializes a PRGitHandler object with a specific pull request number.

        :param pr_number: The number of the pull request to handle.
        """
        self._pr_number = pr_number
        self.comment_id = None

    def get_pr_number(self):
        """
        Retrieves the pull request number associated with this handler instance.

        Returns:
            int: The pull request number.
        """
        return self._pr_number

    def create_or_update_comment(self, comment: str):
        """
        Creates or updates a comment on a pull request based on whether a comment ID already exists.

        If the comment ID does not exist, a new comment is created on the pull request. If the comment ID
        exists, the existing comment is updated with the new content.

        Parameters:
            comment (str): The content of the comment to be posted or updated.

        Returns:
            None: This method does not return anything but logs the response status and details.
        """
        headers = {'Content-type': 'application/json', 'Accept':
            'application/json', 'Authorization': 'token {token}'.format(
            token=self._token)}
        LOGGER.debug('Comment ID: ' + str(self.comment_id))
        LOGGER.debug('create_or_update_comment: ' + comment)
        if self.comment_id is None:
            url = ('https://' + os.environ['GIT_BASE_URL'] +
                '/api/v3/repos/{owner}/{repo}/issues/{issue_number}/comments'
                .format(owner=self._owner, repo=self._repo_name,
                issue_number=self._pr_number))
            data = {'body': comment}
            response = requests.post(url, headers=headers, data=json.dumps(
                data))
            if response.status_code == 201:
                LOGGER.debug('Response:')
                LOGGER.debug(response.json())
                self.comment_id = response.json().get('id')
            else:
                LOGGER.debug(
                    f'Failed to create comment: {response.status_code}, {response.text}'
                    )
        else:
            url = ('https://' + os.environ['GIT_BASE_URL'] +
                '/api/v3/repos/{owner}/{repo}/issues/comments/{comment_id}'
                .format(owner=self._owner, repo=self._repo_name, comment_id
                =self.comment_id))
            data = {'body': comment}
            response = requests.patch(url, headers=headers, data=json.dumps
                (data))
            if response.status_code == 200:
                LOGGER.debug('Response:')
                LOGGER.debug(response.json())
                LOGGER.debug('Comment updated successfully.')
            else:
                LOGGER.debug(
                    f'Failed to update comment: {response.status_code}, {response.text}'
                    )

    def comment_pull_request(self, comment: str):
        """
        Adds a comment to a pull request with additional information about the branch being reviewed.

        This method appends a message to the provided comment indicating the branch that needs review,
        shortens any file paths in the comment to make them more readable, and then either creates a new
        comment or updates an existing one on the pull request.

        Parameters:
            comment (str): The initial comment text to be posted or updated in the pull request.

        Returns:
            None
        """
        comment += '\n\nPlease review the changes on the branch {}.'.format(
            self._unique_feature_branch_name)
        comment = self.shorten_file_paths(comment)
        self.create_or_update_comment(comment)

    def create_progress_bar(self, percentage, status=''):
        """
        Creates a progress bar and posts it as a comment to a pull request.

        This method generates a visual representation of a progress bar based on the
        percentage of completion provided. It optionally includes a status message at the
        end of the progress bar. The progress bar is then posted as a comment to the
        associated pull request using the `create_or_update_comment` method.

        Parameters:
            percentage (float): The completion percentage of the task.
            status (str, optional): Additional status message to append to the progress bar.

        Example:
            create_progress_bar(75, "Processing")
            # This will create and post a progress bar like: [##############------] 75.0% - Processing
        """
        bar_length = 20
        progress_blocks = int(percentage / 100 * bar_length)
        progress_bar = '[' + '#' * progress_blocks + '-' * (bar_length -
            progress_blocks) + ']'
        progress_bar += ' {:.1f}%'.format(percentage)
        if status:
            progress_bar += ' - ' + str(status)
        self.create_or_update_comment(progress_bar)

    def shorten_file_paths(self, input_string):
        """
        Shortens file paths in the LLM response. The file path should start 
        with the repo name and should not contain a unique id.
        """
        unique_ids = set(re.findall(
            'bmw_code_agent\\/\\.tmp\\/[^_]+_([^\\/]+)', input_string))
        for unique_id in unique_ids:
            pattern = '(\\/?bmw_code_agent\\/\\.tmp\\/)([^_]+)_(' + re.escape(
                unique_id) + ')(\\/.*)'
            replacement = '\\2\\4'
            while True:
                input_string, num_substitutions = re.subn(pattern,
                    replacement, input_string)
                if num_substitutions == 0:
                    break
        return input_string
