import os
import sys

from dotenv import load_dotenv

from griptape.artifacts import TextArtifact
from griptape.drivers import (
    GriptapeCloudEventListenerDriver,
)
from griptape.events import (
    EventListener,
    FinishStructureRunEvent,
)
from griptape.structures import Agent
from griptape.tools import Calculator


def is_running_in_managed_environment() -> bool:
    """Determine if the program is running in a managed environment (e.g., Griptape Cloud or Skatepark emulator).

    Returns:
        bool: True if the program is running in a managed environment, False otherwise.
    """
    return "GT_CLOUD_RUN_ID" in os.environ


def get_listener_api_key() -> str:
    """The event driver expects a Griptape API Key as a parameter.
    When your program is running in Griptape Cloud, you will need to provide a 
    valid Griptape API Key in the GT_CLOUD_API_KEY environment variable, otherwise
    the service will not authorize the necessary calls. 
    You can create an API Key by visiting https://cloud.griptape.ai/keys 
    When running in Skatepark, the API key is not needed since it isn't validating calls.

    Returns:
        The Griptape API Key to authorize calls.
    """
    api_key = os.environ.get("GT_CLOUD_API_KEY")
    if is_running_in_managed_environment() and not api_key:
        print("""
              ****WARNING****: No value was found for the 'GT_CLOUD_API_KEY' environment variable.
              This environment variable is required when running in Griptape Cloud for authorization.
              You can generate a Griptape API Key by visiting https://cloud.griptape.ai/keys.
              Specify it as an environment variable when creating a Managed Structure in Griptape Cloud.
              """
              )
    return api_key

  
# If running completely local, such as within an IDE, load environment vars.
if not is_running_in_managed_environment():
    load_dotenv()

input = sys.argv[1]

# We need an event driver to communicate events from our program back to our
# host, which could be the locally-run Skatepark or Griptape Cloud.
# The event driver requires a URL to the host.
# When running in Skatepark or Griptape Cloud, this value is automatically provided to 
# you in the environment variable GT_CLOUD_BASE_URL. You can override 
# this value by specifying your own for GriptapeCloudEventListenerDriver.base_url.
event_driver = GriptapeCloudEventListenerDriver(
    api_key=get_listener_api_key()
)

#### BEGIN EXAMPLE: USING A GRIPTAPE AGENT
# This example uses a Griptape Agent. The Agent will generate the correct events to indicate 
# if the run has succeeded or failed.
structure = Agent(
    tools=[Calculator(off_prompt=False)],
    event_listeners=[EventListener(driver=event_driver)],
)

structure.run(input)
#### END EXAMPLE

#### BEGIN EXAMPLE: NOT USING A GRIPTAPE STRUCTURE
# If you wish to run a program that is NOT a Griptape Structure (e.g., Agent, Pipeline, Workflow, etc.), 
# we will have to manually publish the FinishStructureRunEvent.
# To use this example:
# 1. Comment out the previous example
# 2. Un-comment the example below

# print("Dropping in on this gnarly half-pipe.")
# output_artifact = TextArtifact("Nosebone fip into a 360 Varial McTwist!")

# task_input = TextArtifact(value=sys.argv[1])
# done_event = FinishStructureRunEvent(
#     output_task_input=task_input, output_task_output=output_artifact
# )

# event_driver.publish_event(done_event)
#### END EXAMPLE