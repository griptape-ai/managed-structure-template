import os
import requests


GT_CLOUD_BASE_URL = os.environ.get("GT_CLOUD_BASE_URL", "http://127.0.0.1:5000")


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
        f"{GT_CLOUD_BASE_URL}/api/structures/{structure_id}/runs",
        json={"env": env, "args": args},
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
    response = requests.get(f"{GT_CLOUD_BASE_URL}/api/structure-runs/{run_id}")
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
        f"{GT_CLOUD_BASE_URL}/api/structure-runs/{run_id}/events",
    )
    response.raise_for_status()

    return response.json()


def get_structure_run_logs(run_id: str) -> dict:
    """Get all logs for a run.

    Args:
        run_id: The Structure Run ID.

    Returns:
        The logs for the Structure Run.
    """
    response = requests.get(
        f"{GT_CLOUD_BASE_URL}/api/structure-runs/{run_id}/logs",
    )
    response.raise_for_status()

    return response.json()
