from yamlmaker import env

concourse_target = "my-team"
fly_options = [
  "non-interactive",
  "pause-pipeline"
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
