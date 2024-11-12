import os

from toil.common import Toil
from toil.job import Job
from toil.lib.io import mkdtemp


def helloWorld():
    return "Hello, world!"


if __name__ == "__main__":
    jobstore: str = mkdtemp("tutorial_quickstart")
    os.rmdir(jobstore)
    options = Job.Runner.getDefaultOptions(jobstore)
    options.clean = "always"

    hello_job = Job.wrapFn(helloWorld)

    with Toil(options) as toil:
      print(toil.start(hello_job))