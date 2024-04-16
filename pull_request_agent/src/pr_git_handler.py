import requests
import json
import re
import os
from controller.src.git_handler import GitHandler

class PRGitHandler(GitHandler):
    def __init__(self, pr_number) -> None:
        self._pr_number = pr_number

    def get_pr_number(self):
        return self._pr_number
    
    def comment_pull_request(self, comment: str):
        comment += "\n\nPlease review the changes on the branch {}.".format(
            self._unique_feature_branch_name
            )
        comment = self.shorten_file_paths(comment)
        data = {
            "body": comment
        }
        url = "https://atc-github.azure.cloud.bmw/api/v3/repos/{owner}/{repo}/issues/{issue_number}/comments".format(
            owner=self._owner,
            repo=self._repo_name,
            issue_number=self._pr_number  # Pull requests are considered as issues in terms of comments
        )
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "token {token}".format(token=self._token)
        }
        resp = requests.post(url, data=json.dumps(data), headers=headers)
        
        if resp.status_code == 201:
            return resp.json()
        else:
            print(f"Request failed with status code {resp.status_code}")
            return resp.text

    def update_pull_request(self, title: str, body: str):
        data = {
            "title": title,
            "body": body
        }
        #url = "https://atc-github.azure.cloud.bmw/api/v3/repos/{owner}/{repo}/pulls/{pr_number}".format(
        url = "https://" + os.environ["GIT_BASE_URL"] + "/api/v3/repos/{owner}/{repo}/pulls/{pr_number}".format(
            owner=self._owner,
            repo=self._repo_name,
            pr_number=self._pr_number
        )
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "token {token}".format(token=self._token)
            }
        resp = requests.patch(url, data=json.dumps(data), headers=headers)

        print("owner: " + self._owner)
        print("repo_name: " + self._repo_name)
        print("pr_number: " + str(self._pr_number))
        print("token: " + self._token)
        print("url: " + url)

        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Request failed with status code {resp.status_code}")
            return resp.text

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