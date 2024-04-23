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


# Returns True if this program is being run from within Griptape Cloud or via the Skatepark emulator
def is_running_in_managed_environment():
    return "GT_CLOUD_RUN_ID" in os.environ


# If running completely local, such as within an IDE, load environment vars.
if not is_running_in_managed_environment():
    load_dotenv()

input = sys.argv[1]

# We need an event driver to communicate events from our program back to our
# host, which could be the locally-run Skatepark or Griptape Cloud.

# The event driver requires a URL, stored in the GRIPTAPE_CLOUD_BASE_URL 
# environment variable.
# In Griptape Cloud, this environment variable is provided for you.
# In Skatepark, you may optionally provide your own if you have overridden
# the default URL and port that the emulator is listening on. Otherwise,
# it will use the default URL and port.
listener_url = os.environ.get("GRIPTAPE_CLOUD_BASE_URL")

# The event driver expects a Griptape API Key as a parameter.
# When your program is running in Griptape Cloud, you will need to provide a 
# valid Griptape API Key in order to authorize calls. 
# You can create one by visiting https://cloud.griptape.ai/keys 
# When running in Skatepark, the API key is not needed since it isn't validating calls.
griptape_api_key = os.environ.get("GRIPTAPE_CLOUD_API_KEY")

event_driver = GriptapeCloudEventListenerDriver(
    base_url=listener_url, api_key=griptape_api_key
)

#### BEGIN EXAMPLE: USING A GRIPTAPE AGENT
# This example uses a Griptape Agent. The Agent will generate the correct events to indicate if the run has succeeded or failed.
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