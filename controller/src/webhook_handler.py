import csv
import os
import hashlib
import hmac
import json
import requests
from flask import abort

class WebhookHandler:
    #TODO Check that pull request was opened, not closed.
    def __init__(self, event, csv_file_path):
        self._event = event
        self._csv_file_path = csv_file_path
        self._pull_request_event = self._extract_pull_request_event()
        self._previous_events = self._read_previous_events()
        self.owner = ""
        self.repo = ""
        self.source_branche = ""
        self.target_branche = ""
        self.pr_number = ""
        self.changed_files = []

        self._read_previous_events()
        self._init_event()

    def _read_previous_events(self):
        if not os.path.isfile(self._csv_file_path):
            return set()
        with open(self._csv_file_path, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            return set(tuple(row) for row in reader)

    def _init_event(self):
        owner = self._pull_request_event["repository"]["owner"]["login"]
        repo = self._pull_request_event["repository"]["name"]
        full_repo_name = self._pull_request_event["repository"]["full_name"]
        source_branch = self._pull_request_event["pull_request"]["head"]["ref"]
        target_branch = self._pull_request_event["pull_request"]["base"]["ref"]
        pr_number = str(self._pull_request_event["number"])
        event_tuple = (
            owner,
            repo,
            full_repo_name,
            source_branch,
            target_branch,
            pr_number
        )

        monitored_repo = os.environ["MONITORED_REPO"].split(";")
        if repo not in monitored_repo:
            abort(400)

        if event_tuple not in self._previous_events:
            # Add the event to the list of events; skip if it was already processed
            self.owner = owner
            self.repo = repo
            self.full_repo_name = full_repo_name
            self.source_branche = source_branch
            self.target_branche = target_branch
            self.pr_number = pr_number
        else:
            abort(400)


    def _extract_pull_request_event(self):
        body_dict = json.loads(self._event["body"])
        if "pull_request" in body_dict and body_dict["action"] != "closed":
            #TODO add validation that the pull request was opened, not closed
            # And validate with the webhook secret
            try:
                print("Trying to verify signature ...")
                self.verify_signature(
                    self._event["body"].encode("utf-8"),
                    os.environ["GIT_WEBHOOK_SECRET"],
                    self._event["header"]["X-Hub-Signature-256"]
                )
                return body_dict
            except Exception:
                abort(401)
        else:
            abort(400)

    def save_to_csv(self):
        if not os.path.isfile(self._csv_file_path):
            with open(self._csv_file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
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
                    self.owner,
                    self.repo,
                    self.full_repo_name,
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

    def get_changed_files(self, token):
        """
        Get a list of files changed in a pull request.

        Args:
            base_url (str): The base url of your GitHub API.
            token (str): A GitHub Access Token to access the repo.
        """
        url = f"https://{os.environ["GIT_BASE_URL"]}/api/v3/repos/{self.full_repo_name}/pulls/{self.pr_number}/files"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch changed files: {response.content}")

        files = response.json()
        
        #TODO Don't add files that were deleted in the p.r.
        # => Full file path and check for os.path.exist
        print("Debug: Changed files:")
        self.changed_files = [file["filename"] for file in files]
        print(self.changed_files)
        """
        self.changed_files = ['demo/Calculator.java',
            'demo/gcdm-ms-file-generator-web/src/main/FileGeneratorResource.java',
            'demo/gcdm-ms-file-generator-web/src/main/UserProcessorResource.java',
            'demo/gcdm-ms-file-generator-web/src/main/VehicleProcessorResource.java'
            ]

            optima-coding-mentor-789f7fd6c8-2dggn
        """