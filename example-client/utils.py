from typing import Iterator
import requests
import json


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
        json={
            "env_vars": [{"name": k, "value": v} for k, v in env.items()],
            "args": args,
        },
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


def get_structure_run_event_stream(
    host: str, api_key: str, run_id: str
) -> Iterator[dict]:
    """Get all events for a run.

    Args:
        host: the host URL for the Structure.
        api_key: a Griptape Cloud API Key. This is ignored when running the Skatepark emulator, but required for a Griptape Cloud hosted Structure.
        run_id: The Structure Run ID.

    Returns:
        The events for the Structure Run.
    """
    with requests.get(
        f"{host}/api/structure-runs/{run_id}/events/stream",
        headers=generate_headers(api_key),
        stream=True,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data:"):
                    yield json.loads(decoded_line.removeprefix("data:").strip())


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
