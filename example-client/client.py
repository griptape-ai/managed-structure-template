import sys
import os
import time

import requests
from requests.exceptions import HTTPError

HOST = "http://127.0.0.1:5000"
GT_STRUCTURE_ID = os.environ["GT_STRUCTURE_ID"]


def print_streaming_events(
    events: list[dict],
    printed_events: set,
) -> set:
    """Print all `CompletionChunkEvent` tokens.

    Args:
        events: The events to print.
        printed_events: The set of ids of already printed events. Used to prevent duplicate printing.
    Returns:
        The updated set of printed events.
    """
    new_completion_events = [
        event
        for event in events
        if event["value"]["type"] == "CompletionChunkEvent"
        and event["event_id"] not in printed_events
    ]

    for completion_event in new_completion_events:
        print(completion_event["value"]["token"], flush=True, end="")
        printed_events.add(completion_event["event_id"])

    return printed_events


def create_structure_run(structure_id: str, env: dict, args: list) -> dict:
    """Create a Structure Run.

    Args:
        structure_id: The Structure ID.
        env: The environment variables to pass to the Structure program.
        args: The arguments to pass to the Structure program.

    Returns:
        The created Structure Run.
    """
    response = requests.post(
        f"{HOST}/api/structures/{structure_id}/runs", json={"env": env, "args": args}
    )
    response.raise_for_status()

    return response.json()


def get_structure_run(run_id: str) -> dict:
    """Get a Structure Run status.

    Args:
        run_id: The Structure Run ID.

    Returns:
        The Structure Run.
    """
    response = requests.get(f"{HOST}/api/structure-runs/{run_id}")
    response.raise_for_status()

    return response.json()


def get_structure_run_events(run_id: str) -> dict:
    """Get all events for a run.

    Args:
        run_id: The Structure Run ID.

    Returns:
        The events for the Structure Run.
    """
    response = requests.get(
        f"{HOST}/api/structure-runs/{run_id}/events",
    )
    response.raise_for_status()

    return response.json()


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
