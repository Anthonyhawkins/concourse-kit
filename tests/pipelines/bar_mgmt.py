from yamlmaker import env
import os

concouse_target = "concourse"
pipeline_suffix = "operations"
pipeline_environments = [
  "dev",
  "stage",
]

fly_options = [
  "non-interactive",
  "pause-pipeline",
  "expose-pipeline"
]

def pipeline_config():
  return {
      "jobs": [
          {
            "name": "bar-job-" + env("ENVIRONMENT"),
            "plan": [
              {
                "task": "foo-task",
                "config": {
                  "platform": "linux",
                  "image_resource": {
                    "type": "registry-image",
                    "source": {
                      "repository": "busybox"
                    }
                  },
                  "run": {
                    "path": "echo",
                    "args": ["hello world!"]
                  }
                }
              }
            ]
          }
      ]  # end jobs
  }
