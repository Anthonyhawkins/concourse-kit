from yamlmaker import env

concourse_target = "my-team-" + env("ENVIRONMENT")
pipeline_suffix = "install-" + env("ENVIRONMENT")

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