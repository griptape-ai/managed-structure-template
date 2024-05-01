import requests


def print_streaming_events(
    events: list[dict],
    printed_event_ids: set,
) -> set:
    """Print all `CompletionChunkEvent` tokens.

    Args:
        events: The events to print.
        printed_event_ids: The set of ids of already printed events. Used to prevent duplicate printing.
    Returns:
        The updated set of printed events.
    """
    new_completion_events = [
        event
        for event in events
        if event["value"]["type"] == "CompletionChunkEvent"
        and event["event_id"] not in printed_event_ids
    ]

    for completion_event in new_completion_events:
        print(completion_event["value"]["token"], flush=True, end="")
        printed_event_ids.add(completion_event["event_id"])

    return printed_event_ids


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


def get_structure_run_events(host: str, api_key: str, run_id: str) -> dict:
    """Get all events for a run.

    Args:
        host: the host URL for the Structure.
        api_key: a Griptape Cloud API Key. This is ignored when running the Skatepark emulator, but required for a Griptape Cloud hosted Structure.
        run_id: The Structure Run ID.

    Returns:
        The events for the Structure Run.
    """
    response = requests.get(
        f"{host}/api/structure-runs/{run_id}/events", headers=generate_headers(api_key)
    )
    response.raise_for_status()

    return response.json()


def get_structure_run_logs(host: str, api_key: str, run_id: str) -> dict:
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

    return response.json()
