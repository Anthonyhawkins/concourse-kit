from unittest import mock
from unittest.mock import Mock
from unittest.mock import patch
import pytest
import sys
import os
from concoursekit.concoursekit import set_pipeline
from concoursekit.concoursekit import load_config


#
# Foo Pipeline
#
@patch("concoursekit.concoursekit.fly_run")
def test_set_foo_pipeline_with_one_env(mock_fly_run):
  cck_config = load_config()

  set_pipeline(
    name="foo_mgmt", 
    environments=["dev"], 
    all_flag=False, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'dev-foo-mgmt-install', '--config', 'dev-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'dev-foo-mgmt-install'])
  ])

@patch("concoursekit.concoursekit.fly_run")
def test_set_foo_pipeline_with_multiple_env(mock_fly_run):
  cck_config = load_config()

  set_pipeline(
    name="foo_mgmt", 
    environments=["dev", "stage"], 
    all_flag=False, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'dev-foo-mgmt-install', '--config', 'dev-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'dev-foo-mgmt-install'])
  ])
  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'stage-foo-mgmt-install', '--config', 'stage-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'stage-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'stage-foo-mgmt-install'])
  ])

@patch("concoursekit.concoursekit.fly_run")
def test_set_foo_pipeline_with_all(mock_fly_run):
  cck_config = load_config()

  set_pipeline(
    name="foo_mgmt", 
    environments=[], 
    all_flag=True, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'dev-foo-mgmt-install', '--config', 'dev-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'dev-foo-mgmt-install'])
  ])
  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'stage-foo-mgmt-install', '--config', 'stage-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'stage-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'stage-foo-mgmt-install'])
  ])
  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'prod-foo-mgmt-install', '--config', 'prod-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'prod-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'prod-foo-mgmt-install'])
  ])

@patch("concoursekit.concoursekit.fly_run")
def test_set_foo_pipeline_with_no_env(mock_fly_run):
  mock_fly_run.reset_mock()
  cck_config = load_config()
  set_pipeline(
    name="foo_mgmt", 
    environments=[], 
    all_flag=False, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'dev-foo-mgmt-install', '--config', 'dev-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'dev-foo-mgmt-install'])
  ])

#
# Bar Pipeline
#
@patch("concoursekit.concoursekit.fly_run")
def test_set_bar_pipeline_with_one_env(mock_fly_run):
  cck_config = load_config()

  set_pipeline(
    name="bar_mgmt", 
    environments=["dev"], 
    all_flag=False, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'dev-bar-mgmt', '--config', 'dev-bar-mgmt.yml']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'dev-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'unpause-pipeline', '--pipeline', 'dev-bar-mgmt'])
  ])

#
# Baz Pipeline
#
@patch("concoursekit.concoursekit.fly_run")
def test_set_baz_pipeline_with_one_env(mock_fly_run):
  cck_config = load_config()

  set_pipeline(
    name="baz_mgmt", 
    environments=["dev"], 
    all_flag=False, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'dev-baz-mgmt', '--config', 'dev-baz-mgmt.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'dev-baz-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'pause-pipeline', '--pipeline', 'dev-baz-mgmt'])
  ])