# Managed Structure Template

This template is a starting point for creating programs that can run as Griptape Cloud Managed Structures.
It provides a basic project layout for creating a Managed Structure, but you can customize it to fit your needs.

See the [Griptape CLI](https://github.com/griptape-ai/griptape-cli?tab=readme-ov-file#skatepark-emulator) instructions for how to get started with this template.

## Project Structure

The template provides the following project layout:

- `structure.py` Contains the Managed Structure code.
- `requirements.txt` Contains the dependencies for the Managed Structure. These will be automatically installed when the Structure is registered with Skatepark.
- `structure_config.yaml` Contains the Managed Structure configuration. This informs Griptape Cloud and the Skatepark of your Managed Structure's dependencies and how it needs to build and run.
- `example-client/client.py` Contains an example client that _uses_ the Managed Structure's API. This is useful for testing your Managed Structure locally but ultimately you will want to integrate your Managed Structure with your own application.
- `example-client/pyproject.toml` Contains the dependencies for the example client. Poetry is only used for the example client and is not used by the Managed Structure itself.

### Structure Config Contents

Griptape Cloud and Skatepark make use of the `structure_config.yaml` for understanding the build-time and run-time configuration of the Structure.

The contents of the configuration file are as follows:

```yaml
version: 1.0 # Defines the version of the structure_config to use
runtime: python3 # Defines the runtime environment for the Structure
runtime_version: 3.11 # Defines the specific version of the runtime environment for the Structure
build: # Defines the build-time configuration for the Structure
  requirements_file: requirements.txt # Defines the path to the requirements.txt file for the Structure, relative to the structure_config.yaml. Or absolute from the repository root if a forward slash is used: `/requirements.txt`.
  cache_build_dependencies: # Defines the configuration for caching build dependencies in order to speed up Deployments
    enabled: false # Defines whether the build dependency caching is on or off
    watched_files: # Defines the particular files that will trigger cache invalidation, resulting in a full rebuild of the Structure and dependencies
      - requirements.txt
run: # Defines the run-time configuration for the Structure
  main_file: structure.py # Specifies the path to the entry point file of the Managed Structure. This path is relative to the structure_config.yaml. Or absolute from the repository root if a forward slash is used: `/structure.py`.
```

#### Cache Build Dependencies Field

By default, Griptape Cloud will rebuild and reinstall all dependencies for a Structure on Deployment.

When `cache_build_dependencies` is disabled, Griptape Cloud will always build the Structure code and install dependencies on every Deployment.

When `cache_build_dependencies` is enabled, Griptape Cloud will cache the base runtime dependencies for the Structure for reuse on subsequent Deployments. This speeds up the Deployment process, especially for Structures with many dependencies. That cache will be invalidated when any of the configured `watched_files` change. For instance, if the `requirements.txt` file is configured as the only `watched_file`, then Griptape Cloud will only rebuild the Structure and install dependencies when that file has changes from a previous Deployment. If there are no changes to `requirements.txt`, then Griptape Cloud will reuse the previously built base Structure runtime, and copy over the new Deployment's Structure code files.

When `cache_build_dependencies` is enabled, but there are no `watched_files` specified, Griptape Cloud will build the Structure code and install dependencies on every Deployment, similar to the behavior when `cache_build_dependencies` is disabled.

## Running Managed Code Outside of a Griptape Agent, Pipeline, or Workflow

Code running inside of a [Griptape Structure](https://docs.griptape.ai/stable/griptape-framework/structures/agents/) (such as an Agent, Pipeline, or Workflow), will publish events automatically.

However, when running code _outside_ of a Structure, you will need to publish events manually in order to communicate status back to the client. For example, if you want to gracefully exit before running an Agent, you will need to manually publish an event:

```python
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

1. Fetch the latest changes from the template repository:

```bash
git fetch upstream
```

1. Merge the changes into your project:

```bash
git merge upstream/main --allow-unrelated-histories
```
