import requests
from typing import Optional


def print_streaming_events(
    events: list[dict],
) -> None:
    """Print all `CompletionChunkEvent` tokens.

    Args:
        events: The events to print.
        printed_event_ids: The set of ids of already printed events. Used to prevent duplicate printing.
    Returns:
        The updated set of printed events.
    """
    completion_events = [
        event for event in events if event["type"] == "CompletionChunkEvent"
    ]

    for completion_event in completion_events:
        print(completion_event["payload"]["token"], flush=True, end="")


def generate_headers(api_key: str) -> dict:
    """Generates headers for Griptape Cloud API calls

    Args:
        api_key: a Griptape Cloud API Key. This is ignored when running the Skatepark emulator, but required for a Griptape Cloud hosted Structure.

    Returns:
        Dictionary for the header field in a requests call.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    return headers


def create_structure_run(
    host: str, api_key: str, structure_id: str, env: dict, args: list
) -> dict:
    """Create a Structure Run.

    Args:
        host: the host URL for the Structure.
        api_key: a Griptape Cloud API Key. This is ignored when running the Skatepark emulator, but required for a Griptape Cloud hosted Structure.
        structure_id: The Structure ID.
        env: The environment variables to pass to the Structure program.
        args: The arguments to pass to the Structure program.

    Returns:
        The created Structure Run.
    """
    response = requests.post(
        f"{host}/api/structures/{structure_id}/runs",
        json={"env": env, "args": args},
        headers=generate_headers(api_key),
    )
    response.raise_for_status()

    return response.json()


def get_structure_run(host: str, api_key: str, run_id: str) -> dict:
    """Get a Structure Run status.

    Args:
        host: the host URL for the Structure.
        api_key: a Griptape Cloud API Key. This is ignored when running the Skatepark emulator, but required for a Griptape Cloud hosted Structure.
        run_id: The Structure Run ID.

    Returns:
        The Structure Run.
    """
    response = requests.get(
        f"{host}/api/structure-runs/{run_id}", headers=generate_headers(api_key)
    )
    response.raise_for_status()

    return response.json()


def get_structure_run_events(host: str, api_key: str, run_id: str, offset: int) -> dict:
    """Get all events for a run.

    Args:
        host: the host URL for the Structure.
        api_key: a Griptape Cloud API Key. This is ignored when running the Skatepark emulator, but required for a Griptape Cloud hosted Structure.
        run_id: The Structure Run ID.

    Returns:
        The events for the Structure Run.
    """
    response = requests.get(
        f"{host}/api/structure-runs/{run_id}/events",
        params={"offset": offset},
        headers=generate_headers(api_key),
    )
    response.raise_for_status()

    return response.json()


def get_output_from_events(events: list[dict]) -> Optional[str]:
    """Get the output from the Structure Run events.

    Args:
        events: The events to search.

    Returns:
        The output from the Structure Run events.
    """
    output_events = [
        event for event in events if event["type"] == "FinishStructureRunEvent"
    ]

    return (
        output_events[-1]["payload"]["output_task_output"]["value"]
        if output_events
        else None
    )


def get_status_from_events(events: list[dict]) -> str:
    """Get the status from the Structure Run events.

    Args:
        events: The events to search.

    Returns:
        The status from the Structure Run events.
    """
    system_events = [
        event
        for event in events
        if event["origin"] == "SYSTEM" and event["payload"].get("status") is not None
    ]

    return system_events[-1]["payload"]["status"] if system_events else "QUEUED"


def get_structure_run_logs(host: str, api_key: str, run_id: str) -> list[str]:
    """Get all logs for a run.

    Args:
        host: the host URL for the Structure.
        api_key: a Griptape Cloud API Key. This is ignored when running the Skatepark emulator, but required for a Griptape Cloud hosted Structure.
        run_id: The Structure Run ID.

    Returns:
        The logs for the Structure Run.
    """
    response = requests.get(
        f"{host}/api/structure-runs/{run_id}/logs", headers=generate_headers(api_key)
    )
    response.raise_for_status()

    return response.json()["logs"]


def is_status_complete(status: str) -> bool:
    """Check if a status indicated completed.

    Args:
        status: The status to check.

    Returns:
        True if the status is complete.
    """
    return status in ["SUCCEEDED", "FAILED", "CANCELLED", "ERROR"]
