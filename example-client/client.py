import os
import sys
import time

from requests.exceptions import HTTPError

from utils import (
    create_structure_run,
    get_structure_run,
    get_structure_run_events,
    print_streaming_events,
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

def run_structure(input: str) -> str:
    """Run a Structure program.

    Args:
        input: The input to the Structure program.

    Returns:
        The output of the Structure program.
    """
    # Start a run with the args "What is 5 ^ 2".
    # These args will be passed into our Structure program as standard input.
    structure_run = create_structure_run(
        host=HOST,
        api_key=GT_API_KEY,
        structure_id=GT_STRUCTURE_ID, 
        env={}, 
        args=[input]
    )

    # Runs are asynchronous, so we need to poll the status until it's no longer running.
    run_id = structure_run["structure_run_id"]
    status = structure_run["status"]
    printed_events = set()
    while status == "RUNNING" or status == "QUEUED":
        structure_run = get_structure_run(
            host=HOST,
            api_key=GT_API_KEY,
            run_id=run_id
        )
        status = structure_run["status"]

        # Print all new CompletionChunkEvents.
        event_list = get_structure_run_events(
            host=HOST,
            api_key=GT_API_KEY,
            run_id=run_id
        )
        events = event_list["events"]
        printed_events = print_streaming_events(events, printed_events)

        time.sleep(1)  # Poll every second.

    if structure_run["status"] == "SUCCEEDED":
        print(structure_run["stdout"])
        return structure_run["output"]["value"]
    else:
        print(structure_run["stdout"])
        raise Exception(structure_run["stderr"])


if __name__ == "__main__":
    try:
        print(run_structure("What is 123 * 34, 23 / 12.3, and 9 ^ 4"))
    except HTTPError as e:
        print(e)
        print(f"HTTP Error: {e.response.text}", file=sys.stderr)
