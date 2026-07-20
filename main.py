import asyncio
import sys
from orchestration.run_manager import run_dev_team
from orchestration.attempt_logger import log_attempt


async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python main.py \"<task description>\"")
        sys.exit(1)

    task = sys.argv[1]

    print(f"Running task: {task}\n")
    result = await run_dev_team(task)

    print("=" * 60)
    print("RUN COMPLETE")
    print("=" * 60)
    print(f"Stop reason:      {result['stop_reason']}")
    print(f"Final verdict:    {result['final_verdict']}")
    print(f"Failure category: {result['failure_category']}")
    print(f"Code retries:     {result['code_retry_count']}")
    print(f"Test retries:     {result['test_retry_count']}")
    print()
    print("Final code:")
    print(result['final_code'])
    print()
    print("Critic reasoning:")
    print(result['critic_reasoning'])

    filepath = log_attempt(result)
    print(f"\nLogged to: {filepath}")


if __name__ == "__main__":
    asyncio.run(main())