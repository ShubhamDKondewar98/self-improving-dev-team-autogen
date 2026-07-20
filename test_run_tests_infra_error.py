import asyncio
import sys
sys.path.insert(0, ".")
from agents.test_agent import run_tests_in_docker

async def main():
    solution_code = '''
def solution(a, b):
    return a + b
'''

    # deliberate syntax error - missing colon
    test_code = '''
from solution import solution

def test_basic()
    assert solution(2, 3) == 5
'''

    result = await run_tests_in_docker(solution_code, test_code)
    print("RESULT:", result)

asyncio.run(main())
