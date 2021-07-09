import os
from pipelines.bar_mgmt import pipeline_config

def test_dev_has_two_jobs():
  os.environ["ENVIRONMENT"] = "dev"
  config = pipeline_config()
  assert len(config["jobs"]) == 1
  