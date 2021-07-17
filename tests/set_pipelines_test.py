from unittest import mock
from unittest.mock import Mock
from unittest.mock import patch
import pytest
import sys
import os
from concoursekit.concoursekit import set_pipelines
from concoursekit.concoursekit import load_config


@patch("concoursekit.concoursekit.fly_run")
def test_set_pipelines_with_one_env(mock_fly_run):
  cck_config = load_config()

  set_pipelines( 
    environments=["dev"], 
    all_flag=True, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'dev-bar-mgmt', '--config', 'dev-bar-mgmt.yml']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'dev-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'unpause-pipeline', '--pipeline', 'dev-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'dev-baz-mgmt', '--config', 'dev-baz-mgmt.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'dev-baz-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'pause-pipeline', '--pipeline', 'dev-baz-mgmt']),
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'dev-foo-mgmt-install', '--config', 'dev-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'dev-foo-mgmt-install'])
  ], any_order=True)

@patch("concoursekit.concoursekit.fly_run")
def test_set_pipelines_with_two_env(mock_fly_run):
  cck_config = load_config()

  set_pipelines( 
    environments=["dev", "stage"], 
    all_flag=True, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
  mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'dev-bar-mgmt', '--config', 'dev-bar-mgmt.yml']),
  mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'dev-bar-mgmt']),
  mock.call(['fly', '-t', 'my-team', 'unpause-pipeline', '--pipeline', 'dev-bar-mgmt']),
  mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'stage-bar-mgmt', '--config', 'stage-bar-mgmt.yml']),
  mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'stage-bar-mgmt']),
  mock.call(['fly', '-t', 'my-team', 'unpause-pipeline', '--pipeline', 'stage-bar-mgmt']),
  mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'dev-baz-mgmt', '--config', 'dev-baz-mgmt.yml', '--non-interactive']),
  mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'dev-baz-mgmt']),
  mock.call(['fly', '-t', 'my-team', 'pause-pipeline', '--pipeline', 'dev-baz-mgmt']),
  mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'stage-baz-mgmt', '--config', 'stage-baz-mgmt.yml', '--non-interactive']),
  mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'stage-baz-mgmt']),
  mock.call(['fly', '-t', 'my-team', 'pause-pipeline', '--pipeline', 'stage-baz-mgmt']),
  mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'dev-foo-mgmt-install', '--config', 'dev-foo-mgmt-install.yml', '--non-interactive']),
  mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
  mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
  mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'stage-foo-mgmt-install', '--config', 'stage-foo-mgmt-install.yml', '--non-interactive']),
  mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'stage-foo-mgmt-install']),
  mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'stage-foo-mgmt-install'])
  ], any_order=True)

@patch("concoursekit.concoursekit.fly_run")
def test_set_pipelines_without_envs(mock_fly_run):
  cck_config = load_config()

  set_pipelines( 
    environments=[], 
    all_flag=True, 
    cck_config=cck_config, 
    plan_flag=False
  )

  mock_fly_run.assert_has_calls([
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'dev-bar-mgmt', '--config', 'dev-bar-mgmt.yml']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'dev-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'unpause-pipeline', '--pipeline', 'dev-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'prod-bar-mgmt', '--config', 'prod-bar-mgmt.yml']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'prod-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'unpause-pipeline', '--pipeline', 'prod-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'stage-bar-mgmt', '--config', 'stage-bar-mgmt.yml']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'stage-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'unpause-pipeline', '--pipeline', 'stage-bar-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'dev-baz-mgmt', '--config', 'dev-baz-mgmt.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'dev-baz-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'pause-pipeline', '--pipeline', 'dev-baz-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'prod-baz-mgmt', '--config', 'prod-baz-mgmt.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'prod-baz-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'pause-pipeline', '--pipeline', 'prod-baz-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'set-pipeline', '--pipeline', 'stage-baz-mgmt', '--config', 'stage-baz-mgmt.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'my-team', 'hide-pipeline', '--pipeline', 'stage-baz-mgmt']),
    mock.call(['fly', '-t', 'my-team', 'pause-pipeline', '--pipeline', 'stage-baz-mgmt']),
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'dev-foo-mgmt-install', '--config', 'dev-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'dev-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'stage-foo-mgmt-install', '--config', 'stage-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'stage-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'stage-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'set-pipeline', '--pipeline', 'prod-foo-mgmt-install', '--config', 'prod-foo-mgmt-install.yml', '--non-interactive']),
    mock.call(['fly', '-t', 'concourse', 'hide-pipeline', '--pipeline', 'prod-foo-mgmt-install']),
    mock.call(['fly', '-t', 'concourse', 'unpause-pipeline', '--pipeline', 'prod-foo-mgmt-install'])
  ], any_order=True)