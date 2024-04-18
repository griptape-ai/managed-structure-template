import os
import sys

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


input = sys.argv[1]

# We need an event driver to communicate events from our program back to Skatepark
event_driver = GriptapeCloudEventListenerDriver(
    base_url="http://127.0.0.1:5000", api_key="..."
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