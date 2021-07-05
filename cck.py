import argparse
import importlib
import time
import sys
import os
import subprocess
import pytest

from yamlmaker import Text
from yamlmaker import generate
from yamlmaker import panic
# DONE - cc_kit.py --set-pipeline --name <pipeline_name> --env <env>
# DONE - cc_kit.py --set-pipeline --name <pipeline_name> --all
# DONE - cc_kit.py --set-pipeline --all
# DONE - cc_kit.py --gen-pipeline --name <pipeline_name> --env <env>
# DONE - cc_kit.py --test-pipeline --name <pipeline_name>
# DONE - cc_kit.py --test-pipeline --all

def setup():
  """
  Parse Arguments from the CLI
  """

  parser = argparse.ArgumentParser(
    description="Concourse Kit - For Extream Concourse Pipelining."
  )
  commands = parser.add_mutually_exclusive_group()
  commands.add_argument("--generate-pipeline", action="store_true", dest="gen_pipeline", help="generate a pipeline.yml config")
  commands.add_argument("--test-pipeline", action="store_true", dest="test_pipeline", help="run the test for one or more pipelines")
  commands.add_argument("--set-pipeline", action="store_true", dest="set_pipeline", help="set pipeline(s)")

  parser.add_argument("--all", action="store_true", dest="all_flag", help="Specify all pipelines or all environments, depending on context.")
  parser.add_argument("--env", action="append", dest="environments", default=[], help="the name of a target environment; specify multiple times for multiple environments.")
  parser.add_argument("--name", action="store", dest="name", help="the name of the pipeline.py file")

  return  parser.parse_args()


def main():
  """
  Dispatch to the respective functions.
  """
  parsed_args = setup()
  if parsed_args.gen_pipeline: generate_pipeline(parsed_args.name, parsed_args.environments)
  if parsed_args.test_pipeline: test_pipeline(parsed_args.name, parsed_args.all_flag)
  if parsed_args.set_pipeline and parsed_args.name: set_pipeline(parsed_args.name, parsed_args.environments, parsed_args.all_flag)
  if parsed_args.set_pipeline and not parsed_args.name: set_pipelines(parsed_args.environments, parsed_args.all_flag)


def import_pipeline(name):
  """
  Attempt to import a pipeline based on file_name or panic
  """
  try:
    return importlib.import_module(f"pipelines.{name}")
  except ModuleNotFoundError as e:
    panic(f"Pipeline {name}.py does not exist within the pipelines directory or a module used by that pipeline does not exist.", e)
  except SyntaxError as e:
    panic(f"Pipeline: pipelines/{name}.py - contains a Syntax Error.", e)


def generate_pipeline(name, environments, pipeline=None):
  """
  Generate a pipeline config and write it to a yaml file.
  """
  if not (name and environments):
    panic("Must Provide a name and an environment.")

  environment = environments[0] #  only generate 1 environment, ignore the rest
  os.environ["ENVIRONMENT"] = environment

  print(Text.blue("Generating Pipeline to {name}.yml".format(name=name)))

  if not pipeline:
    pipeline = import_pipeline(name)
  else:
    importlib.reload(pipeline)

  try:
    config = pipeline.pipeline_config()
    if type(config) is not dict: 
      panic(f"Pipeline: pipelines/{name}.py pipeline_config() MUST return a dictionary.")
    generate(pipeline.pipeline_config(), name)
  except AttributeError:
    panic(f"Pipeline: pipelines/{name}.py MUST have a top-level function defined as pipeline_config()")


def test_pipeline(name, all_flag):
  """
  Test one or more pipelies using pytest.
  """
  if all_flag:
    print(Text.cyan("Testing All Pipelines"))
    pytest.main(["-s", "-k", "pipeline_tests", "-rA"])
  else:
    print(Text.cyan(f"Testing Pipeline: {name}"))
    pytest.main(["-s", "-k", name, "-rA"])

  
def set_pipelines(environments, all_flag):
  """
  Set multiple pipelines
  """
  print("Setting all pipelines in 10 seconds... ctl+c to cancel.")
  try:
    time.sleep(10)
  except KeyboardInterrupt:
    print(Text.yellow("Aborting!"))
    sys.exit(0)

  # raw [('pipelines', [], ['foo.py', 'bar.py', ...])]
  pipelines = [pipeline[2] for pipeline in os.walk("pipelines")][0]

  for pipeline in pipelines:
    set_pipeline(pipeline.replace(".py", ""), environments, all_flag)


def set_pipeline(name, environments, all_flag):
  """ 
  Set a single pipeline in one or more environments
  """
  # must always set the ENVIRONMENT variable before import
  # import once, now to pull in pipeline_suffix, pipeline_environments etc.
  pipeline = import_pipeline(name)
  #
  # The suffix goes at the end of the pipeline name i.e.
  # -install -upgrade -operations -misc
  #
  try:
    pipeline_suffix = pipeline.pipeline_suffix
    if not type(pipeline_suffix) == str: pipeline_suffix = ""
  except AttributeError:
    pipeline_suffix = ""
  #
  # if the pipeline.py file contains pipeline_environments
  # only those environments are allowed to be set
  #
  try:
    allowed_environments = pipeline.pipeline_environments
    if not type(allowed_environments) == list:
      panic(f"Pipeline: pipelines/{name}.py - The pipeline_environments variable must be a list of strings.")
  #
  # if the pipeline_environments variable does not exist, all environments
  # under target-environments direcotry are allowed
  #
  except AttributeError:
    env_directories = [env[0] for env in os.walk("target-environments")]
    env_directories.pop(0) # remove target-environments dir name
    # TODO - Account for unix forward slash /
    allowed_environments = [env.split("\\")[-1] for env in env_directories]

  #
  # if --all was not specified reduce the list down to only the environments which were specified
  # using the --env flag(s) 
  # 
  if environments:
    for environment in environments:
      if environment not in allowed_environments:
        print(Text.yellow(f"Warning - environment {environment} does not exist within the target-environments directory and will be ignored."))
    allowed_environments = list(set(environments).intersection(allowed_environments))

  name = name.replace("_", "-").lower()
  if pipeline_suffix: name = f"{name}-{pipeline_suffix}"
  
  for environment in allowed_environments:
    if environment == "common": continue
    os.environ["ENVIRONMENT"] = environment
    pipeline_name = "{env}-{name}".format(env=environment, name=name)    
    generate_pipeline(pipeline_name, [environment], pipeline)
    print(Text.green(f"Setting pipeline: {pipeline_name}"))

    # TODO - account for fly not logged in
    subprocess.run(
      ['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', pipeline_name , '--config', f"{pipeline_name}.yml"]
    )

    os.remove(f"{pipeline_name}.yml")


if __name__ == "__main__":
  main()


