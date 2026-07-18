import json
import re
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_core.tools import FunctionTool
from models.openai_model_client import model_client
from config.docker_util import getDockerCommandLineExecutor, start_docker_container, stop_docker_container


def parse_pytest_summary(pytest_stdout: str) -> dict | None:
    """
    Parses pytest's final summary line to extract passed/failed counts.
    VERIFIED against real Docker/pytest output.
    Returns {"passed": int, "failed": int} or None if nothing legitimate ran.
    """
    passed_match = re.search(r"(\d+) passed", pytest_stdout)
    failed_match = re.search(r"(\d+) failed", pytest_stdout)

    if not passed_match and not failed_match:
        return None

    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0

    return {"passed": passed, "failed": failed}


async def run_tests_in_docker(solution_code: str, test_code: str) -> str:
    """
    Writes solution.py and test_solution.py, runs pytest in a fresh
    Docker sandbox, returns JSON matching the locked Test-writer schema.
    """
    docker = getDockerCommandLineExecutor()
    try:
        await start_docker_container(docker)

        harness_code = f'''
import subprocess

with open("solution.py", "w") as f:
    f.write({solution_code!r})

with open("test_solution.py", "w") as f:
    f.write({test_code!r})

subprocess.run(["pip", "install", "-q", "pytest"])
result = subprocess.run(
    ["pytest", "test_solution.py", "-v"],
    capture_output=True,
    text=True,
)
print("PYTEST_STDOUT_START")
print(result.stdout)
print("PYTEST_STDOUT_END")
print("PYTEST_STDERR_START")
print(result.stderr)
print("PYTEST_STDERR_END")
'''

        result = await docker.execute_code_blocks(
            code_blocks=[CodeBlock(language="python", code=harness_code)],
            cancellation_token=CancellationToken(),
        )

        if "PYTEST_STDOUT_START" not in result.output:
            return json.dumps({
                "execution_status": "INFRA_ERROR",
                "results": None,
                "error_detail": f"Harness script did not complete. Raw output: {result.output}",
            })

        pytest_stdout = result.output.split("PYTEST_STDOUT_START")[1].split("PYTEST_STDOUT_END")[0]
        pytest_stderr = result.output.split("PYTEST_STDERR_START")[1].split("PYTEST_STDERR_END")[0]

        parsed = parse_pytest_summary(pytest_stdout)

        if parsed is None:
            return json.dumps({
                "execution_status": "INFRA_ERROR",
                "results": None,
                "error_detail": (pytest_stdout + "\n" + pytest_stderr).strip(),
            })

        return json.dumps({
            "execution_status": "COMPLETED",
            "results": parsed,
            "error_detail": None,
        })

    except Exception as e:
        return json.dumps({
            "execution_status": "INFRA_ERROR",
            "results": None,
            "error_detail": str(e),
        })
    finally:
        await stop_docker_container(docker)


run_tests_tool = FunctionTool(
    run_tests_in_docker,
    description=(
        "Writes the given solution code and test code to files and executes "
        "the tests inside a Docker sandbox. Returns a JSON string with "
        "execution_status, results, and error_detail."
    ),
)

test_agent = AssistantAgent(
    name="test_agent",
    description="Writes tests for the Coder's code, independently of its implementation, and executes them in Docker.",
    model_client=model_client,
    tools=[run_tests_tool],
    system_message="""
    You are the test-writer agent for a small automated development team.

    You will receive the original task and the Coder's code. Write pytest
    tests based ONLY on what the task requires -- do not rely on the
    Coder's internal implementation details or logic, only its stated
    behavior. This keeps your tests an honest, independent check rather
    than validating the Coder's own assumptions.

    The Coder's solution always exposes its entry point as a function
    named exactly `solution`. Your test file must import it with:
        from solution import solution

    Write your tests as standard pytest test functions (functions whose
    names start with `test_`), each with its own assert statements.

    Call the run_tests_in_docker tool, passing the Coder's solution code
    and your test code, to execute your tests.

    After the tool returns, respond with ONLY the JSON string the tool
    gave you -- do not add commentary, do not wrap it in markdown, do not
    modify its structure. Pass it through exactly as returned.
    """,
)