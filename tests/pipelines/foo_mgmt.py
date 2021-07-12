from yamlmaker import env
from yamlmaker import Include

concourse_target = "concourse"
pipeline_suffix = "install"
pipeline_environments = [
  "dev",
  "stage",
  "prod"
]
fly_options = [
  "non-interactive",
  "unpause-pipeline",
  "hide-pipeline"
]

def pipeline_config():
  return {
      "jobs": [
          {
            "name": "foo-job-" + env("ENVIRONMENT"),
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
                    "args": ["for all envs"]
                  }
                }
              }
            ]
          }
      ] + Include.when(env("ENVIRONMENT") == "dev", [
        {
          "name": "bar-job-" + env("ENVIRONMENT"),
          "plan": [
            {
              "task": "bar-task",
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
                  "args": ["only in dev!"]
                }
              }
            }
          ]
        }
    ]) # end jobs
  }
