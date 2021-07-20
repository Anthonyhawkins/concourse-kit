import argparse
import importlib
import time
import sys
import os
import subprocess
import traceback

import pytest
import yaml

from yamlmaker import Text
from yamlmaker import generate
from yamlmaker import panic

CCK_DEFAULTS = """
# The default concourse target to use
concourse_target: concourse


# When Setting a Pipeline Fly will use these options
fly_default_options:
- interactive
- hide-pipeline
- unpause-pipeline
# These options are allowed.
# - non-interactive | interactive
# - hide-pipeline | expose-pipeline
# - unpause-pipeline | pause-pipeline

# The directory to import <pipeline_name>.py files from. 
pipelines_dir: pipelines

# The directory to look for <pipeline_name>_test.py files from.
pipelines_test_dir: pipeline_tests

# The directory to use for target-environments
target_environments_dir: target_environments

# Environments to ignore when setting pipelines
ignore_environments:
- common
"""


def setup():
  """
  Parse Arguments from the CLI
  """
  parser = argparse.ArgumentParser(
    description="Concourse Kit - For Extream Concourse Pipelining."
  )
  commands = parser.add_mutually_exclusive_group()
  commands.add_argument("--init", action="store_true", dest="init", default=False, help="Initialize a new concourse-kit directory.")
  commands.add_argument("--generate-pipeline", action="store_true", dest="gen_pipeline", help="generate a pipeline.yml config")
  commands.add_argument("--test-pipeline", action="store_true", dest="test_pipeline", help="run the test for one or more pipelines")
  commands.add_argument("--set-pipeline", action="store_true", dest="set_pipeline", help="set pipeline(s)")

  parser.add_argument("--plan", action="store_true", dest="plan_flag", default=False, help="View the plan only, don't set anything.")
  parser.add_argument("--all", action="store_true", dest="all_flag", help="Specify all pipelines or all environments, depending on context.")
  parser.add_argument("--env", action="append", dest="environments", default=[], help="the name of a target environment; specify multiple times for multiple environments.")
  parser.add_argument("--name", action="store", dest="name", help="the name of the pipeline.py file")

  parsed_args = parser.parse_args()

  one_of_commands = [
    parsed_args.init,
    parsed_args.gen_pipeline,
    parsed_args.test_pipeline,
    parsed_args.set_pipeline
  ]

  if not True in one_of_commands:
    parser.print_usage()
    panic('You Must Specify a Top-Level command: --init | --generate-pipeline | --test-pipeline | --set-pipeline')
    
  return  parser.parse_args()


def main():
  """
  Dispatch to the respective functions.
  """
  sys.path.append(os.getcwd())
  parsed_args = setup()

  if os.path.exists(".cck.yml"):
    cck_config = load_config()
    if parsed_args.gen_pipeline: generate_pipeline(parsed_args.name, parsed_args.environments, cck_config, parsed_args.plan_flag)
    if parsed_args.test_pipeline: test_pipeline(parsed_args.name, parsed_args.all_flag, cck_config)
    if parsed_args.set_pipeline and parsed_args.name: set_pipeline(parsed_args.name, parsed_args.environments, parsed_args.all_flag, cck_config, parsed_args.plan_flag)
    if parsed_args.set_pipeline and not parsed_args.name: set_pipelines(parsed_args.environments, parsed_args.all_flag, cck_config, parsed_args.plan_flag)
  else:
    if parsed_args.init: 
      initialize_cck()
    else:
      panic("You are not in a concourse-kit managed directory.  You can run cck --init to create one.")


def load_config():
  """
  Load the .cck.yml file, validate a proper config, and ensure required directories exists.
  """
  with open(".cck.yml") as stream:
    try:
      cck_config = yaml.safe_load(stream)
    except yaml.YAMLError:
      panic("YAML Load Failure for .cck.yml")

  config_keys = {
    "concourse_target": str,
    "fly_default_options": list,
    "pipelines_dir": str,
    "pipelines_test_dir": str,
    "target_environments_dir": str,
    "ignore_environments": list
  }

  for key, required_type in config_keys.items():
    if key not in cck_config:
      panic(f"Invalid Config: Key: {key} - Not Found")
    else:
      if not type(cck_config[key]) == required_type:
        panic(f"Invalid Config: Key: {key} - Is not Type {required_type}")

    if "_dir" in key and not os.path.exists(cck_config[key]):
      panic("Required Directory: {dir_name} - Does not Exist".format(dir_name=cck_config[key]))


  return cck_config

def initialize_cck():
  """
  Establish a new concourse-kit directory with a .cck.yml file.
  """
  with open(".cck.yml","w+") as file:
    file.writelines(CCK_DEFAULTS)

  print("cck initialized with the following")
  print("\tConcourse Target:              concourse")
  print("\tFly Default Options:")
  print("\t\tinteractive")
  print("\t\thide-pipeline")
  print("\t\tunpause-pipeline")
  print("\tPipelines Directory:           pipelines")
  print("\tTarget Environments Directory: target-environments")
  print("\tPipelines Test Directory:      pipelines_test")
  print("To change the defaults, edit the .cck.yml file within this directory.")


def import_pipeline(name, pipelines_dir):
  """
  Attempt to import a pipeline based on file_name or panic
  """
  try:
    return importlib.import_module(f"{pipelines_dir}.{name}")
  except ModuleNotFoundError as e:
    panic(f"Pipeline {name}.py does not exist within the {pipelines_dir} directory or a module used by that pipeline does not exist.", e)
  except SyntaxError as e:
    panic(f"Pipeline: {pipelines_dir}/{name}.py - contains a Syntax Error.", e)


def generate_pipeline(name, environments, cck_config, plan_flag, pipeline=None):
  """
  Generate a pipeline config and write it to a yaml file.
  """
  if not (name and environments):
    panic("Must Provide a name and an environment.")

  pipelines_dir = cck_config["pipelines_dir"]

  environment = environments[0] #  only generate 1 environment, ignore the rest
  os.environ["ENVIRONMENT"] = environment

  if not plan_flag: print(Text.blue(f"Generating Pipeline to {name}.yml"))
  if not pipeline: pipeline = import_pipeline(name, pipelines_dir)

  try:
    try:
      pass
      config = pipeline.pipeline_config()
    except Exception as e:
      exc_type, exc_value, exc_tb = sys.exc_info()
      error = traceback.format_exception(exc_type, exc_value, exc_tb)[-2]
      print(Text.red(f"ENVIRONMENT: {environment}"))
      print(Text.red(error))
      panic(f"Pipeline: {pipelines_dir}/{name}.py Encountered an Python Exception", e)
    if type(config) is not dict: 
      panic(f"Pipeline: {pipelines_dir}/{name}.py pipeline_config() MUST return a dictionary.")
    generate(pipeline.pipeline_config(), name)
  except AttributeError:
    panic(f"Pipeline: {pipelines_dir}/{name}.py MUST have a top-level function defined as pipeline_config()")


def test_pipeline(name, all_flag, cck_config):
  """
  Test one or more pipelies using pytest.
  """
  if all_flag:
    print(Text.cyan("Testing All Pipelines"))
    pytest.main(["-s", "-k", cck_config["pipelines_test_dir"], "-rA"])
  else:
    print(Text.cyan(f"Testing Pipeline: {name}"))
    pytest.main(["-s", "-k", name, "-rA"])

  
def set_pipelines(environments, all_flag, cck_config, plan_flag):
  """
  Set multiple pipelines
  """

  pipelines_dir = cck_config["pipelines_dir"]

  if not plan_flag: 
    print("Setting all pipelines in 10 seconds... ctl+c to cancel.")
    try:
      time.sleep(10)
    except KeyboardInterrupt:
      print(Text.yellow("Aborting!"))
      sys.exit(0)

  # raw [('pipelines', [], ['foo.py', 'bar.py', ...])]
  pipelines = [pipeline[2] for pipeline in os.walk(pipelines_dir)][0]

  for pipeline in pipelines:
    set_pipeline(pipeline.replace(".py", ""), environments, all_flag, cck_config, plan_flag)


def set_pipeline(name, environments, all_flag, cck_config, plan_flag):
  """ 
  Set a single pipeline in one or more environments
  """

  target_environments_dir = cck_config["target_environments_dir"]
  pipelines_dir = cck_config["pipelines_dir"]
  ignore_environments = cck_config["ignore_environments"]

  # must always set the ENVIRONMENT variable before import
  # import once, now to pull in pipeline_suffix, pipeline_environments etc.
  pipeline = import_pipeline(name, cck_config["pipelines_dir"])
  allowed_environments = determine_pipeline_environments(pipeline, name, environments, pipelines_dir, target_environments_dir, ignore_environments)
  origin_name = name
  name = name.replace("_", "-").lower()

  if plan_flag: 
    print(Text.bold(f"Pipeline Plan for: {name} - origin | pipeline-name | concourse-target | fly options | validity"))

  for environment in allowed_environments:
    os.environ["ENVIRONMENT"] = environment
    importlib.reload(pipeline)
    pipeline_suffix = get_pipeline_suffix(pipeline)
    concourse_target = determine_concourse_target(pipeline, cck_config["concourse_target"])
      
    if pipeline_suffix:
      pipeline_name = f"{environment}-{name}-{pipeline_suffix}"
    else:
      pipeline_name = f"{environment}-{name}"

    if not plan_flag: print(Text.green(f"Setting pipeline: {pipeline_name}"))

    generate_pipeline(pipeline_name, [environment], cck_config, plan_flag, pipeline)
    fly_options = determine_fly_options(pipeline, cck_config["fly_default_options"])

    if plan_flag: 

      for index, option in enumerate(fly_options):
        if option  == "expose-pipeline":
          fly_options[index] = Text.yellow(option)
        elif option == "pause-pipeline":
          fly_options[index] = Text.blue(option)
        elif option == "unpause-pipeline":
          fly_options[index] = Text.green(option)

      fly_options_string = " ".join(fly_options)

      output = fly_run(['fly', 'validate-pipeline', '--config', f"{pipeline_name}.yml"], stdout=subprocess.DEVNULL)
      if output.returncode == 0:
        valid = Text.green("valid")
        arrow = ""
      else:
        valid = Text.red("invalid")
        arrow = Text.red("└───> ")

      print(f"{arrow}{pipelines_dir}/{origin_name}.py | {pipeline_name} | {concourse_target} | {fly_options_string} | {valid}")

    else:
      
      set_command = ['fly', '-t', concourse_target, 'set-pipeline', '--pipeline', pipeline_name , '--config', f"{pipeline_name}.yml"]
      if "non-interactive" in fly_options: set_command.append("--non-interactive")    
      fly_run(set_command)
      
      # Visibility and Pause State
      if "expose-pipeline" in fly_options:
        expose_command = ['fly', '-t', concourse_target, 'expose-pipeline', '--pipeline', pipeline_name]
        fly_run(expose_command)
      if "hide-pipeline" in fly_options:
        hide_command = ['fly', '-t', concourse_target, 'hide-pipeline', '--pipeline', pipeline_name]
        fly_run(hide_command)
      if "unpause-pipeline" in fly_options:
        unpause_command = ['fly', '-t', concourse_target, 'unpause-pipeline', '--pipeline', pipeline_name]
        fly_run(unpause_command)
      if "pause-pipeline" in fly_options:
        pause_command = ['fly', '-t', concourse_target, 'pause-pipeline', '--pipeline', pipeline_name]
        fly_run(pause_command)

    os.remove(f"{pipeline_name}.yml")


def get_pipeline_suffix(pipeline):
  """
  # The suffix goes at the end of the pipeline name i.e.
  # -install -upgrade -operations -misc
  """
  try:
    pipeline_suffix = pipeline.pipeline_suffix
    if not type(pipeline_suffix) == str: pipeline_suffix = ""
  except AttributeError:
    pipeline_suffix = ""
  
  return pipeline_suffix


def determine_concourse_target(pipeline, default_target):
  """
  Determine which concourse target to set the pipeline to.
  """
  try:
    concourse_target = pipeline.concourse_target
    if not type(concourse_target) == str: return default_target
  except AttributeError:
    return default_target
  return concourse_target


def determine_pipeline_environments(pipeline, name, environments, pipelines_dir, target_environments_dir, ignore_environments):
  """
  Determine which environments a pipeline should be generated for.
  """
  #
  # if the pipeline.py file contains pipeline_environments
  # only those environments are allowed to be set
  #
  try:
    allowed_environments = pipeline.pipeline_environments
    if not type(allowed_environments) == list:
      panic(f"Pipeline: {pipelines_dir}/{name}.py - The pipeline_environments variable must be a list of strings.")
  #
  # if the pipeline_environments variable does not exist, all environments
  # under target-environments direcotry are allowed
  #
  except AttributeError:
    env_directories = [env[0] for env in os.walk(target_environments_dir)]
    env_directories.pop(0) # remove target-environments dir name

    if os.name == 'nt':
      allowed_environments = [env.split("\\")[-1] for env in env_directories]
    else:
      allowed_environments = [env.split("/")[-1] for env in env_directories]
  #
  # reduce the list down to only the environments which were specified
  # using the --env flag(s) (environments) 
  # 

  negated_environments = []   # environments to remove, start with !<env> or within ignore_environments
  explicit_environments = []  # environments to reduce down to, passed with --env arg. 
  for environment in list(environments):

    #
    # If an environment begins with a bang it will be negated.
    #
    if environment.startswith("!"):
      negated_environments.append(environment.replace("!", ""))
      continue

    #
    # If an environment is allowed, it will be reduced to it
    # 
    if environment not in allowed_environments:
      print(Text.yellow(f"Warning - environment {environment} does not exist within the {target_environments_dir} directory and will be ignored."))
    else:
      explicit_environments.append(environment)


  negated_environments += ignore_environments
  allowed_environments = list(set(allowed_environments))
  
  #
  # Remove environments which are to be negated
  #
  for negated_environment in negated_environments:
    if negated_environment in allowed_environments:
      allowed_environments.remove(negated_environment)
  
  #
  # Reduce down to only the environments that were passed via --env and what's allowed. 
  #
  if explicit_environments:
    allowed_environments = list(set(explicit_environments).intersection(allowed_environments))

  return allowed_environments


def determine_fly_options(pipeline, default_options):
  """
  Load default fly options and load any overrides from the pipeline if
  they exists.
  """
  try:
    pipeline_options = pipeline.fly_options
    if not type(pipeline_options) == list: pipeline_options = []
  except AttributeError:
    pipeline_options = []

  counter_options = {
    "interactive": "non-interactive",
    "non-interactive": "interactive",

    "expose-pipeline": "hide-pipeline",
    "hide-pipeline": "expose-pipeline",

    "pause-pipeline": "unpause-pipeline",
    "unpause-pipeline": "pause-pipeline"
  }

  for option in default_options:
    # does this option exist as an option?
    if option in counter_options.keys():
      # if the counter option isn't in pipeline_options then use it as an option.
      if counter_options[option] not in pipeline_options:
        pipeline_options.append(option)

  return list(set(pipeline_options))

def fly_run(command, **kwargs):
  """
  Run the fly command.
  """
  try:
    return subprocess.run(command, **kwargs)
  except FileNotFoundError:
    panic("Unable to Execute Fly Command. Is it Installed?")

if __name__ == "__main__":
  main()
