import asyncio
from autogen_core import CancellationToken
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_core.code_executor import CodeBlock

async def test():
    docker = DockerCommandLineCodeExecutor(
        image="python:3.12-slim",
        work_dir="docker_probe_workspace",
        timeout=60,
    )
    await docker.start()

    setup_code = "import subprocess; subprocess.run(['pip', 'install', '-q', 'pytest'])"

    harness_code = '''
broken_test_file_content = """
def add(a, b)
    return a + b

def test_add():
    assert add(2, 3) == 5
"""

with open("broken_test.py", "w") as f:
    f.write(broken_test_file_content)

import subprocess
result = subprocess.run(["pytest", "broken_test.py", "-v"], capture_output=True, text=True)
print("PYTEST_EXIT_CODE:", result.returncode)
print("PYTEST_STDOUT:", result.stdout)
print("PYTEST_STDERR:", result.stderr)
'''

    result = await docker.execute_code_blocks(
        code_blocks=[
            CodeBlock(language="python", code=setup_code),
            CodeBlock(language="python", code=harness_code),
        ],
        cancellation_token=CancellationToken(),
    )
    print("=" * 60)
    print("OUTER exit_code:", result.exit_code)
    print("OUTER output:", result.output)

    await docker.stop()

asyncio.run(test())
