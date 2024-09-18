import os
import sys
import time

from dotenv import load_dotenv
from requests.exceptions import HTTPError
from typing import Optional

from utils import (
    create_structure_run,
    get_output_from_events,
    get_status_from_events,
    get_structure_run_events,
    print_streaming_events,
    get_structure_run_logs,
    is_status_complete,
)

# Pull in configuration variables.
load_dotenv()

# If running against the Skatepark emulator, you will need to set
# this environment variable (or put it in a .env file) to tell the
# client which URL Skatepark is listening on. The default value is
# http://127.0.0.1:5000 .
# For a Structure in Griptape Cloud, this environment variable
# should be set to https://cloud.griptape.ai/
HOST = os.getenv("GT_CLOUD_BASE_URL", "http://cloud.griptape.ai")

# If running against the Skatepark emulator, this will be the ID
# of the Structure that you registered with Skatepark. For a Structure
# hosted in Griptape Cloud, it will be the ID of the Structure you
# are running, which can be found at https://cloud.griptape.ai/structures
GT_STRUCTURE_ID = os.environ["GT_STRUCTURE_ID"]

# The Skatepark emulator does NOT require a Griptape Cloud API key.
# However, Griptape Cloud requires a valid API Key in order
# to authorize calling the API. You can generate a key by
# visiting https://cloud.griptape.ai/configuration/api-keys
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
    offset = 0
    output = None
    while not is_status_complete(status) or output is None:
        event_response = get_structure_run_events(
            host=HOST, api_key=GT_API_KEY, run_id=structure_run_id, offset=offset
        )
        events = event_response["events"]
        for event in events:
            if event["origin"] == "SYSTEM":
                status = event["payload"]["status"]
                if event["type"] == "StructureRunError":
                    output = "Error running Structure: {}".format(event["payload"]["status_detail"])
                    print(output)
            elif event["origin"] == "USER":
                match event["type"]:
                    case "FinishStructureRunEvent":
                        # The Griptape structure has output the result in this event,
                        # so we can stop polling.
                        output = event["payload"]["output_task_output"]["value"]
                    case "CompletionChunkEvent":
                        # This is a streaming event, so we can print it out.
                        print(event["payload"]["token"], flush=True, end="")
                    case _:
                        print("Event:", event["type"])
    
        # Dont poll for the same events again.
        offset = event_response["next_offset"]
        time.sleep(1)  # Poll every second.

    logs = get_structure_run_logs(
        host=HOST, api_key=GT_API_KEY, run_id=structure_run_id
    )

    print("\n".join(logs))

    return output


if __name__ == "__main__":
    try:
        print(run_structure("What is 123 * 34, 23 / 12.3, and 9 ^ 4?"))
    except HTTPError as e:
        print(e)
        print(f"HTTP Error: {e.response.text}", file=sys.stderr)
