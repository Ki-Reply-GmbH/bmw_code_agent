import csv
import os
import requests
import hashlib
import hmac
import json

class WebhookHandler:
    #TODO Check that pull request was opened, not closed.
    def __init__(self, webhook_url, csv_file_path):
        self._webhook_url = webhook_url
        self._csv_file_path = csv_file_path
        self._data = self._read_webhook()
        self._pull_request_event = self._extract_pull_request_event()
        self._previous_events = self._read_previous_events()
        self.owner = ""
        self.repo = ""
        self.source_branche = ""
        self.target_branche = ""
        self.pr_number = ""

        self._read_previous_events()
        self._init_event()

    def _read_previous_events(self):
        if not os.path.isfile(self._csv_file_path):
            return set()
        with open(self._csv_file_path, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            return set(tuple(row) for row in reader)

    def _init_event(self, event):
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
            self.owner = owner
            self.repo = repo
            self.source_branche = source_branch
            self.target_branche = target_branch
            self.pr_number = pr_number

    def _read_webhook(self):
        req = requests.get(self._webhook_url)
        if req.status_code == 200:
            return req.json()
        else:
            print("Failed to read webhook: %s", req.status_code)
            return []

    def _extract_pull_request_event(self, event):
        body_dict = json.loads(event["body"])
        if "pull_request" in body_dict and body_dict["action"] != "closed":
            #TODO add validation that the pull request was opened, not closed
            # And validate with the webhook secret
            try:
                print("Trying to verify signature ...")
                self.verify_signature(
                    event["body"].encode("utf-8"),
                    os.environ["GIT_WEBHOOK_SECRET"],
                    event["header"]["X-Hub-Signature-256"]
                )
                return body_dict
            except Exception as e:
                print("Exception occurred while verifying signature:")
                print(e)
                return None
        return None

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
        with open(self._csv_file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    self._webhook_url,
                    self.owner,
                    self.repo,
                    self.source_branch,
                    self.target_branch, 
                    self.pr_number
                ]
            )

    def verify_signature(self, payload_body, secret_token, signature_header):
        """Verify that the payload was sent from GitHub by validating SHA256.

        Raise and return 403 if not authorized.

        Args:
            payload_body: original request body to verify (request.body())
            secret_token: GitHub app webhook token (WEBHOOK_SECRET)
            signature_header: header received from GitHub (X-Hub-Signature-256)
        """
        if not signature_header:
            raise Exception(status_code=403, detail="X-Hub-Signature-256 header is missing!")
        hash_object = hmac.new(secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()
        print()
        print("Expected signature: " + expected_signature)
        print("Received signature: " + signature_header)
        print()
        if not hmac.compare_digest(expected_signature, signature_header):
            raise Exception(status_code=403, detail="Request signatures didn't match!")