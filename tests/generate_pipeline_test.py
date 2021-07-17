import os
from concoursekit import generate_pipeline
from concoursekit import load_config

def test_generate_pipeline_with_env(capsys):
  cck_config = load_config()
  
  generate_pipeline(
    name="foo_mgmt", 
    environments=["dev"], 
    cck_config=cck_config, 
    plan_flag=False
  )

  out, err = capsys.readouterr()
  assert "Generating Pipeline to foo_mgmt.yml" in out
  assert os.path.exists("foo_mgmt.yml")
  os.remove("foo_mgmt.yml")


def test_generate_pipeline_with_all(capsys):
  cck_config = load_config()
  
  try:
    generate_pipeline(
      name="foo_mgmt", 
      environments=[], 
      cck_config=cck_config, 
      plan_flag=False
    )
  except SystemExit:
    out, err = capsys.readouterr()
    assert "Must Provide a name and an environment" in out


def test_generate_nonexisting_pipeline_with_env(capsys):
  cck_config = load_config()
  
  try:
    generate_pipeline(
      name="blah_mgmt", 
      environments=["dev"], 
      cck_config=cck_config, 
      plan_flag=False
    )
  except SystemExit:
    out, err = capsys.readouterr()
    assert "Pipeline blah_mgmt.py does not exist" in out

  
