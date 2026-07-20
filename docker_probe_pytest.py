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

    test_code = '''
def add(a, b):
    return a + b

def test_add_correct():
    assert add(2, 3) == 5

def test_add_deliberately_wrong():
    assert add(2, 2) == 5

if __name__ == "__main__":
    import subprocess, sys
    with open("test_file.py", "w") as f:
        f.write(open(__file__).read())
    result = subprocess.run(["pytest", "test_file.py", "-v"], capture_output=True, text=True)
    print("PYTEST_EXIT_CODE:", result.returncode)
    print("PYTEST_STDOUT:", result.stdout)
    print("PYTEST_STDERR:", result.stderr)
'''

    result = await docker.execute_code_blocks(
        code_blocks=[
            CodeBlock(language="python", code=setup_code),
            CodeBlock(language="python", code=test_code),
        ],
        cancellation_token=CancellationToken(),
    )
    print("outer exit_code:", result.exit_code)
    print("outer output:", result.output)
    await docker.stop()

asyncio.run(test())
