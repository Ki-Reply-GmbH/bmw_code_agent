#TODO Datei löschen, wenn nicht mehr benötigt
import requests
import json
import csv
import os
from datetime import datetime

webhook_url = "http://localhost:8080/optima/api/coding/webhooks"
req = requests.get(webhook_url)

push_events = []
pull_request_events = []

most_recent_push_time = None
pull_request_number = None

# Read the most recent push time and pull request number from the CSV file
if os.path.exists("data.csv"):
    with open("data.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            if row[0] == "most_recent_push_time":
                most_recent_push_time = row[1]
            elif row[0] == "pull_request_number":
                pull_request_number = row[1]

# Ensure the request was successful and we have data to write
if req.status_code == 200:
    data = req.json()

    for event in data:
        # Extracting pull requests events respectively push events
        if "pull_request" in event:
            pull_request_events.append(event)
        elif "pusher" in event:
            push_events.append(event)
        
    for push in push_events:
        # Extract the most recent push event
        push_time_str = push["head_commit"]["timestamp"]
        push_time = datetime.strptime(push_time_str, "%Y-%m-%dT%H:%M:%S%z")

        if most_recent_push_time is None:
            most_recent_push_time = push_time
        elif push_time > most_recent_push_time:
            most_recent_push_time = push_time
    
    for pull_request in pull_request_events:
        # Extract the most recent pull request number
        pull_request_number = pull_request["number"]

        if pull_request_number is None:
            pull_request_number = pull_request["number"]
        elif pull_request_number > pull_request["number"]:
            pull_request_number = pull_request["number"]

    # Write the most recent push time and pull request number to a CSV file
    with open("data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Value"])
        writer.writerow(["most_recent_push_time", most_recent_push_time])
        writer.writerow(["pull_request_number", pull_request_number])

    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    pull_req_output_file_path = os.path.join(current_dir_path, "out_pull_req.json")
    push_output_file_path = os.path.join(current_dir_path, "out_push.json")

    # Write the data to the file
    with open(pull_req_output_file_path, "w") as f:
        json.dump(pull_request_events, f, indent=4)
    with open(push_output_file_path, "w") as f:
        json.dump(push_events, f, indent=4)