import os
import sys
import time

from dotenv import load_dotenv
from requests.exceptions import HTTPError
from typing import Optional

from utils import (
    create_structure_run,
    get_structure_run,
    get_structure_run_events,
    print_streaming_events,
    get_structure_run_logs,
)

# Pull in configuration variables.
load_dotenv()

# If running against the Skatepark emulator, you will need to set
# this environment variable (or put it in a .env file) to tell the
# client which URL Skatepark is listening on. The default value is
# http://127.0.0.1:5000 .
# For a Structure in Griptape Cloud, this environment variable
# should be set to https://cloud.griptape.ai/
HOST = os.environ["GT_CLOUD_BASE_URL"]

# If running against the Skatepark emulator, this will be the ID
# of the Structure that you registered with Skatepark. For a Structure
# hosted in Griptape Cloud, it will be the ID of the Structure you
# are running, which can be found at https://cloud.griptape.ai/structures
GT_STRUCTURE_ID = os.environ["GT_STRUCTURE_ID"]

# The Skatepark emulator does NOT require a Griptape Cloud API key.
# However, Griptape Cloud requires a valid API Key in order
# to authorize calling the API. You can generate a key by
# visiting https://cloud.griptape.ai/keys
GT_API_KEY = os.environ.get(
    "GT_CLOUD_API_KEY",
    "GRIPTAPE CLOUD API KEY ONLY NEEDED FOR STRUCTURES IN GRIPTAPE CLOUD",
)


def run_structure(input: str) -> Optional[str]:
    """Run a Structure program.

    Args:
        input: The input to the Structure program.

    Returns:
        The output of the Structure program.
    """
    # Start a run with the input args, such as the asker's question
    # (e.g., "What is 123 * 34, 23 / 12.3, and 9 ^ 4?").
    # In this example, it is only a single string, but Structures support
    # an array of inputs. Advanced uses include serializing a JSON dictionary
    # for example.
    # These args will be passed into our Structure program as standard input.
    structure_run = create_structure_run(
        host=HOST,
        api_key=GT_API_KEY,
        structure_id=GT_STRUCTURE_ID,
        env={},
        args=[input],
    )

    # Runs are asynchronous, so we need to poll the status until it's no longer running.
    structure_run_id = structure_run["structure_run_id"]
    status = structure_run["status"]
    printed_event_ids = set()  # Keep track of which events we've printed.
    while status not in ("SUCCEEDED", "FAILED"):
        structure_run = get_structure_run(
            host=HOST, api_key=GT_API_KEY, run_id=structure_run_id
        )
        status = structure_run["status"]

        # You can comment out this block if you don't want to stream events as they occur.
        event_list = get_structure_run_events(
            host=HOST, api_key=GT_API_KEY, run_id=structure_run_id
        )
        events = event_list["events"]
        printed_event_ids = print_streaming_events(events, printed_event_ids)

        time.sleep(1)  # Poll every second.

    logs = get_structure_run_logs(
        host=HOST, api_key=GT_API_KEY, run_id=structure_run_id
    )

    if structure_run["status"] == "SUCCEEDED":
        stdout = next(
            (log["message"] for log in logs["logs"] if log["stream"] == "stdout"),
            None,
        )
        print(stdout)

        return structure_run["output"]["value"] if "output" in structure_run else None
    else:
        stderr = next(
            (log["message"] for log in logs["logs"] if log["stream"] == "stderr"),
            None,
        )
        raise ValueError(stderr)


if __name__ == "__main__":
    try:
        print(run_structure("What is 123 * 34, 23 / 12.3, and 9 ^ 4?"))
    except HTTPError as e:
        print(e)
        print(f"HTTP Error: {e.response.text}", file=sys.stderr)
