import requests
from controller.src.git_handler import GitHandler

class PRGitHandler(GitHandler):
    def __init__(self, pr_number) -> None:
        self._pr_number = pr_number

    def get_pr_number(self):
        return self._pr_number
    
    def update_pull_request(self, title: str, body: str):
        pass
