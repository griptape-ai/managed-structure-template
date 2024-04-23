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

HOST = "http://127.0.0.1:5000"
GT_STRUCTURE_ID = os.environ["GT_STRUCTURE_ID"]


def run_structure(input: str) -> str:
    """Run a Structure program.

    Args:
        input: The input to the Structure program.

    Returns:
        The output of the Structure program.
    """
    # Start a run with the args "What is 5 ^ 2".
    # These args will be passed into our Structure program as standard input.
    structure_run = create_structure_run(GT_STRUCTURE_ID, {}, [input])

    # Runs are asynchronous, so we need to poll the status until it's no longer running.
    run_id = structure_run["run_id"]
    status = structure_run["status"]
    printed_events = set()
    while status == "RUNNING":
        structure_run = get_structure_run(run_id)
        status = structure_run["status"]

        # Print all new CompletionChunkEvents.
        event_list = get_structure_run_events(run_id)
        events = event_list["events"]
        printed_events = print_streaming_events(events, printed_events)

        time.sleep(1)  # Poll every second.

    if structure_run["status"] == "COMPLETED":
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
