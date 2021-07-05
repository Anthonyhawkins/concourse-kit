from yamlmaker import env
import os
pipeline_suffix = "operations"

pipeline_environments = [
  "dev",
  "stage",
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
