import csv
import os
import requests

class WebhookHandler:
    def __init__(self, webhook_url, csv_file_path):
        self._webhook_url = webhook_url
        self._csv_file_path = csv_file_path
        self._data = self._read_webhook()
        self._pull_request_events = self._extract_pull_request_events()
        self._previous_events = self._read_previous_events()
        self.owners = []
        self.repos = []
        self.source_branches = []
        self.target_branches = []
        self.pr_numbers = []

    def _read_previous_events(self):
        if not os.path.isfile(self.csv_file_path):
            return set()
        with open(self.csv_file_path, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            return set(tuple(row) for row in reader)

    def _init_events(self):
        for event in self._pull_request_events:
            owner = event["repository"]["owner"]["login"]
            repo = event["repository"]["name"]
            source_branch = event["pull_request"]["head"]["ref"]
            target_branch = event["pull_request"]["base"]["ref"]
            pr_number = event["number"]
            event_tuple = (
                self.webhook_url,
                owner,
                repo,
                source_branch,
                target_branch,
                str(pr_number)
            )

            if event_tuple not in self._existing_events:
                # Add the event to the list of events; skip if it was already processed
                self._owners.append(owner)
                self._repos.append(repo)
                self._source_branches.append(source_branch)
                self._target_branches.append(target_branch)
                self._pr_numbers.append(pr_number)

    def _read_webhook(self):
        req = requests.get(self.webhook_url)
        if req.status_code == 200:
            return req.json()
        else:
            return []

    def _extract_pull_request_events(self):
        pull_request_events = []
        for event in self.data:
            if "pull_request" in event:
                pull_request_events.append(event)
        return pull_request_events

    def save_to_csv(self):
        if not os.path.isfile(self.csv_file_path):
            with open(self.csv_file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        "webhook_url",
                        "owner",
                        "repo",
                        "source_branch",
                        "target_branch",
                        "pr_number"
                    ]
                )
        for i in range(len(self._owners)):
            with open(self.csv_file_path, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        self.webhook_url,
                        self._owners[i],
                        self._repos[i],
                        self._source_branches[i],
                        self._target_branches[i], 
                        self._pr_numbers[i]
                    ]
                )