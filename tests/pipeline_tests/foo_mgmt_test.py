import os
from pipelines.foo_mgmt import pipeline_config



def test_dev_has_two_jobs():
  os.environ["ENVIRONMENT"] = "dev"
  config = pipeline_config()
  assert len(config["jobs"]) == 2
  
def test_prod_has_one_job():
  os.environ["ENVIRONMENT"] = "prod"
  config = pipeline_config()
  assert len(config["jobs"]) == 1
