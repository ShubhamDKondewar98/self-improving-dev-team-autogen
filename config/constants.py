import os
from dotenv import load_dotenv

load_dotenv()


MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")


MAX_CODE_RETRIES = int(os.getenv("MAX_CODE_RETRIES", 3))
MAX_TEST_RETRIES = int(os.getenv("MAX_TEST_RETRIES", 3))
MAX_TOTAL_TOKENS = int(os.getenv("MAX_TOTAL_TOKENS", 60000))


DOCKER_IMAGE = "python:3.12-slim"
DOCKER_TIMEOUT_SECONDS = 60
DOCKER_WORK_DIR = "docker_workspace"


ATTEMPT_LOG_DIR = "logs"