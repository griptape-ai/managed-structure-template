import os
import sys
import time
from typing import Optional

from utils import (
    create_structure_run,
    get_structure_run,
    get_structure_run_events,
    print_streaming_events,
    get_structure_run_logs,
)
from requests.exceptions import HTTPError

GT_STRUCTURE_ID = os.environ["GT_STRUCTURE_ID"]


def run_structure(input: str) -> Optional[str]:
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
    structure_run_id = structure_run["structure_run_id"]
    status = structure_run["status"]
    printed_event_ids = set()  # Keep track of which events we've printed.
    while status not in ("SUCCEEDED", "FAILED"):
        structure_run = get_structure_run(structure_run_id)
        status = structure_run["status"]

        # You can comment out this block if you don't want to streaming events.
        event_list = get_structure_run_events(structure_run_id)
        events = event_list["events"]
        printed_event_ids = print_streaming_events(events, printed_event_ids)

        time.sleep(1)  # Poll every second.

    logs = get_structure_run_logs(structure_run_id)

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
        print(run_structure("What is 123 * 34, 23 / 12.3, and 9 ^ 4"))
    except HTTPError as e:
        print(e)
        print(f"HTTP Error: {e.response.text}", file=sys.stderr)
