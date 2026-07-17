from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from config.constants import DOCKER_TIMEOUT_SECONDS, DOCKER_WORK_DIR,DOCKER_IMAGE



def getDockerCommandLineExecutor():
    docker=DockerCommandLineCodeExecutor(
        image=DOCKER_IMAGE,
        work_dir=DOCKER_WORK_DIR,
        timeout=DOCKER_TIMEOUT_SECONDS
    )
    return docker

async def start_docker_container(docker):
    print("Starting Docker Container")
    await docker.start()
    print("Docker Container Started") 

async def stop_docker_container(docker):
    print("Stopping Docker Container")
    await docker.stop()
    print("Docker Container Stopped")


