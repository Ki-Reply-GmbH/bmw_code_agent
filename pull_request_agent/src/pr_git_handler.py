import requests
import json
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
        data = {
            "body": comment
        }
        url = "https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments".format(
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
        url = "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}".format(
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
