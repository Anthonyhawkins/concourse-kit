from unittest import mock
from unittest.mock import Mock
from unittest.mock import patch
import pytest
import sys
import os
from concoursekit.concoursekit import set_pipeline
from concoursekit.concoursekit import load_config


class ReturnCode(object):
  def __init__(self, returncode):
    self.returncode = returncode


@patch("concoursekit.concoursekit.fly_run")
def test_valid_pipeline(mock_fly_run, capsys):
  cck_config = load_config()

  mock_fly_run.return_value = ReturnCode(0)

  set_pipeline(
    name="foo_mgmt", 
    environments=["dev"], 
    all_flag=False, 
    cck_config=cck_config, 
    plan_flag=True
  )

  out, err = capsys.readouterr()
  assert "Pipeline Plan for: foo-mgmt-install - origin | pipeline-name | concourse-target | fly options | validity" in out

  for field in ["dev-foo-mgmt-install", "concourse", "non-interactive", "hide-pipeline", "unpause-pipeline", "valid"]:
    assert field in out

  mock_fly_run.assert_has_calls([
    mock.call(['fly', 'validate-pipeline', '--config', 'dev-foo-mgmt-install.yml'], stdout=-3),
  ])

@patch("concoursekit.concoursekit.fly_run")
def test_valid_pipeline(mock_fly_run, capsys):
  cck_config = load_config()

  mock_fly_run.return_value = ReturnCode(1)

  set_pipeline(
    name="foo_mgmt", 
    environments=["dev"], 
    all_flag=False, 
    cck_config=cck_config, 
    plan_flag=True
  )

  out, err = capsys.readouterr()
  assert "Pipeline Plan for: foo-mgmt-install - origin | pipeline-name | concourse-target | fly options | validity" in out

  for field in ["dev-foo-mgmt-install", "concourse", "non-interactive", "hide-pipeline", "unpause-pipeline", "invalid"]:
    assert field in out

  mock_fly_run.assert_has_calls([
    mock.call(['fly', 'validate-pipeline', '--config', 'dev-foo-mgmt-install.yml'], stdout=-3),
  ])