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

    code = '''
def add(a, b):
    return a + b

assert add(2, 3) == 5, "should be 5"
assert add(2, 2) == 5, "deliberately wrong to see a FAILURE case"
print("done")
'''
    result = await docker.execute_code_blocks(
        code_blocks=[CodeBlock(language="python", code=code)],
        cancellation_token=CancellationToken(),
    )
    print("exit_code:", result.exit_code)
    print("output:", repr(result.output))
    await docker.stop()

asyncio.run(test())
