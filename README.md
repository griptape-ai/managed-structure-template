# Managed Structure Template
This template is a starting point for creating programs that can run as Griptape Cloud Managed Structures. 
It provides a basic project layout for creating a Managed Structure, but you can customize it to fit your needs.

See the [Griptape CLI](https://github.com/griptape-ai/griptape-cli?tab=readme-ov-file#skatepark-emulator) instructions for how to get started with this template.

## Project Structure
The template provides the following project layout:

- `structure.py` Contains the Managed Structure code.
- `requirements.txt` Contains the dependencies for the Managed Structure. These will be automatically installed when the Structure is registered with Skatepark.
- `example-client/client.py` Contains an example client that _uses_ the Managed Structure's API. This is useful for testing your Managed Structure locally but ultimately you will want to integrate your Managed Structure with your own application. 
- `example-client/pyproject.toml` Contains the dependencies for the example client. Poetry is only used for the example client and is not used by the Managed Structure itself.

## Running Managed Code Outside of a Griptape Agent, Pipeline, or Workflow
Code running inside of a [Griptape Structure](https://docs.griptape.ai/stable/griptape-framework/structures/agents/) (such as an Agent, Pipeline, or Workflow), will publish events automatically.

However, when running code _outside_ of a Structure, you will need to publish events manually in order to communicate status back to the client. For example, if you want to gracefully exit before running an Agent, you will need to manually publish an event:

```
task_input = TextArtifact(value="Input params: empty.")
task_output = TextArtifact(value="Already up to date!")
done_event = FinishStructureRunEvent(
    output_task_input=task_input, output_task_output=task_output
)

event_driver.publish_event(done_event)
```

An example of this is provided.

## Keeping in Sync with this Template
To sync your project with the latest changes from this template, you can run the following command:

1. Add the template repository as a remote:
```bash
git remote add upstream https://github.com/griptape-ai/managed-structure-template.git
```
2. Fetch the latest changes from the template repository:
```bash
git fetch upstream 
```
3. Merge the changes into your project:
```bash
git merge upstream/main --allow-unrelated-histories
```
