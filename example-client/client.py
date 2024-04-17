import sys
import os
import requests
import time

from requests.exceptions import HTTPError

HOST = "http://127.0.0.1:5000"
GT_STRUCTURE_ID = os.environ["GT_STRUCTURE_ID"]


def run_structure(input: str) -> str:
    # Start a run with the args "What is 5 ^ 2".
    # These args will be passed into our Structure program as standard input.
    response = requests.post(
        f"{HOST}/api/structures/{GT_STRUCTURE_ID}/runs",
        json={
            "env": {},
            "args": [input],
        },
    )
    response.raise_for_status()

    # Runs are asynchronous, so we need to poll the status until it's no longer running.
    run_id = response.json()["run_id"]
    status = response.json()["status"]
    while status == "RUNNING":
        response = requests.get(f"{HOST}/api/runs/{run_id}")
        response.raise_for_status()
        status = response.json()["status"]

        time.sleep(1)  # Poll every second.

    content = response.json()
    if content["status"] == "COMPLETED":
        print(content["stdout"])
        return content["output"]["value"]
    else:
        print(content["stdout"])
        raise Exception(content["stderr"])


try:
    print(run_structure("What is 123 * 34, 23 / 12.3, and 9 ^ 4"))
except HTTPError as e:
    print(f"HTTP Error: {e.response.text}", file=sys.stderr)
