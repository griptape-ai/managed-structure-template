import os
import sys
import time

from requests.exceptions import HTTPError
from typing import Optional

from utils import (
    create_structure_run,
    get_structure_run,
    get_structure_run_events,
    print_streaming_events,
    get_structure_run_logs,
)

# If running the client against the Skatepark emulator, 
# use these values to specify the Host and Structure ID.
# Comment them out if you are running against Griptape Cloud.
HOST = "http://127.0.0.1:5000"
GT_STRUCTURE_ID = os.environ["GT_STRUCTURE_ID"]
GT_API_KEY = "API KEY NOT NEEDED FOR SKATEPARK EMULATOR"

# If running the client against a Structure in Griptape Cloud,
# use these values to specify the Host and Structure ID.
# Note that Griptape Cloud requires a valid API Key in order
# to authorize calling the API. You can generate a key by
# visiting https://cloud.griptape.ai/keys
# HOST = "https://cloud.griptape.ai"
# GT_STRUCTURE_ID = "GO TO https://cloud.griptape.ai/structures TO GET STRUCTURE ID AND FILL IN HERE"
# GT_API_KEY = os.environ.get("GT_CLOUD_API_KEY")

# When running a Structure in Griptape Cloud, the requests
# are first QUEUED before transitioning to RUNNING. Skatepark
# emulates this behavior by applying a default time to remain 
# in the QUEUED state in order to allow your client to 
# handle this state appropriately.
# You can override the time that the Structure remains in
# the QUEUED state within Skatepark by setting the environment
# variable GT_SKATEPARK_QUEUE_DELAY to the desired time in seconds.


def run_structure(input: str) -> Optional[str]:
    """Run a Structure program.

    Args:
        input: The input to the Structure program.

    Returns:
        The output of the Structure program.
    """
    # Start a run with the input args.
    # These args will be passed into our Structure program as standard input.
    structure_run = create_structure_run(
        host=HOST,
        api_key=GT_API_KEY,
        structure=GT_STRUCTURE_ID, 
        env={}, 
        args=[input]
        )

    # Runs are asynchronous, so we need to poll the status until it's no longer running.
    structure_run_id = structure_run["structure_run_id"]
    status = structure_run["status"]
    printed_event_ids = set()  # Keep track of which events we've printed.
    while status not in ("SUCCEEDED", "FAILED"):
        structure_run = get_structure_run(
            host=HOST,
            api_key=GT_API_KEY,
            structure_run_id=structure_run_id
            )
        status = structure_run["status"]

        # You can comment out this block if you don't want to streaming events.
        event_list = get_structure_run_events(
            host=HOST,
            api_key=GT_API_KEY,
            structure_run_id=structure_run_id
            )
        events = event_list["events"]
        printed_event_ids = print_streaming_events(events, printed_event_ids)

        time.sleep(1)  # Poll every second.

    logs = get_structure_run_logs(
        host=HOST,
        api_key=GT_API_KEY,
        structure_run_id=structure_run_id
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
