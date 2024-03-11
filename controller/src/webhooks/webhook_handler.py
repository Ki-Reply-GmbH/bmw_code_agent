import csv
import os
import requests
import hashlib
import hmac

class WebhookHandler:
    #TODO Check that pull request was opened, not closed.
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

        self._read_previous_events()
        self._init_events()

    def _read_previous_events(self):
        if not os.path.isfile(self._csv_file_path):
            return set()
        with open(self._csv_file_path, "r") as file:
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
                self._webhook_url,
                owner,
                repo,
                source_branch,
                target_branch,
                str(pr_number)
            )

            if event_tuple not in self._previous_events:
                # Add the event to the list of events; skip if it was already processed
                self.owners.append(owner)
                self.repos.append(repo)
                self.source_branches.append(source_branch)
                self.target_branches.append(target_branch)
                self.pr_numbers.append(pr_number)

    def _read_webhook(self):
        req = requests.get(self._webhook_url)
        if req.status_code == 200:
            return req.json()
        else:
            return []

    def _extract_pull_request_events(self):
        pull_request_events = []
        for event in self._data:
            if "pull_request" in event["body"]:
                #TODO add validation that the pull request was opened, not closed
                # And validate with the webhook secret
                pull_request_events.append(event["body"])
        return pull_request_events

    def save_to_csv(self):
        if not os.path.isfile(self._csv_file_path):
            with open(self._csv_file_path, "w", newline="") as file:
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
            with open(self._csv_file_path, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        self._webhook_url,
                        self.owners[i],
                        self.repos[i],
                        self.source_branches[i],
                        self.target_branches[i], 
                        self.pr_numbers[i]
                    ]
                )

    def verify_signature(payload_body, secret_token, signature_header):
        """Verify that the payload was sent from GitHub by validating SHA256.

        Raise and return 403 if not authorized.

        Args:
            payload_body: original request body to verify (request.body())
            secret_token: GitHub app webhook token (WEBHOOK_SECRET)
            signature_header: header received from GitHub (x-hub-signature-256)
        """
        if not signature_header:
            raise Exception(status_code=403, detail="x-hub-signature-256 header is missing!")
        hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()
        if not hmac.compare_digest(expected_signature, signature_header):
            raise Exception(status_code=403, detail="Request signatures didn't match!")