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
from typing import Optional


def is_running_in_managed_environment() -> bool:
    """Determine if the program is running in a managed environment (e.g., Griptape Cloud or Skatepark emulator).

    Returns:
        bool: True if the program is running in a managed environment, False otherwise.
    """
    return "GT_CLOUD_STRUCTURE_RUN_ID" in os.environ


def get_listener_api_key() -> str:
    """The event driver expects a Griptape Cloud API Key as a parameter.
    When your program is running in Griptape Cloud, you will need to provide a
    valid Griptape Cloud API Key in the GT_CLOUD_API_KEY environment variable, otherwise
    the service will not authorize the necessary calls.
    You can create an API Key by visiting https://cloud.griptape.ai/keys
    When running in Skatepark, the API key is not needed since it isn't validating calls.

    Returns:
        The Griptape Cloud API Key to authorize calls.
    """
    api_key = os.environ.get("GT_CLOUD_API_KEY", "")
    if is_running_in_managed_environment() and not api_key:
        print(
            """
              ****WARNING****: No value was found for the 'GT_CLOUD_API_KEY' environment variable.
              This environment variable is required when running in Griptape Cloud for authorization.
              You can generate a Griptape Cloud API Key by visiting https://cloud.griptape.ai/keys .
              Specify it as an environment variable when creating a Managed Structure in Griptape Cloud.
              """
        )
    return api_key


def run_example_with_griptape_agent(
    input: str, event_driver: Optional[GriptapeCloudEventListenerDriver]
):
    """This example demonstrates how to use a Griptape Agent as a Structure.
    The Agent is equipped with a Calculator tool, which it can use to solve math problems.
    The Agent will generate events as it thinks through the problem, and then emits events
    to indicate if the run has succeeded or failed.

    Args:
        input: a string with a question for the agent (e.g., "What is 2 ^ 31?")
        event_driver (optional): the object that will publish events as the agent thinks.
    """
    structure = Agent(
        tools=[Calculator(off_prompt=False)],
        event_listeners=[EventListener(driver=event_driver)],
    )

    structure.run(input)


def run_example_with_no_agent(
    input: str, event_driver: Optional[GriptapeCloudEventListenerDriver]
):
    """This example demonstrates how to run a program that does NOT rely on Griptape Agents,
    Pipelines, or Workflows, but still gets the benefits of running in the managed environment.
    There are situations where you may need to emit events outside of the automatic event generation
    that Agents, et. al. perform.

    This example creates a TextArtifact as output and then emits the FinishStructureRunEvent,
    making the output visible from within the Skatepark emulator or in the Griptape Cloud console.

    Args:
        input: the input passed to the program when invoked
        event_driver (optional): the object that will publish the event.
    """
    print("Dropping in on this gnarly half-pipe.")
    output_artifact = TextArtifact("Nosebone flip into a 360 Varial McTwist!")

    task_input = TextArtifact(value=input)
    done_event = FinishStructureRunEvent(
        output_task_input=task_input, output_task_output=output_artifact
    )

    if event_driver:
        event_driver.publish_event(done_event, flush=True)


input = sys.argv[1]

# Are we running this program in a managed environment (i.e., the Skatepark
# emulator or Griptape Cloud), or completely local (such as within an IDE)?
if is_running_in_managed_environment():
    # In the managed environment, our environment variables are provided for us.
    # We need an event driver to communicate events from this program back
    # to our host.
    # The event driver requires a URL to the host.
    # When running in Skatepark or Griptape Cloud, this value is automatically
    # provided to you in the environment variable GT_CLOUD_BASE_URL. You can
    # override this value by specifying your own for
    # GriptapeCloudEventListenerDriver.base_url .
    event_driver = GriptapeCloudEventListenerDriver(api_key=get_listener_api_key())
else:
    # If running completely local, such as within an IDE, load environment vars.
    # This is done automatically for you when the Structure is run within the
    # Skatepark emulator or as a Structure on Griptape Cloud.
    load_dotenv()

    # We don't need an event driver if we're testing the program in an IDE.
    event_driver = None


# This function will run with a Griptape Agent, who will automatically emit events.
run_example_with_griptape_agent(input, event_driver)

# Un-comment this example to run a program that manually generates events, without
# relying on a Griptape Agent.
# run_example_with_no_agent(input, event_driver)
