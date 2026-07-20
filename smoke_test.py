import asyncio
from teams.dev_team import build_dev_team

async def main():
    team = build_dev_team()

    task = "Write a function that returns the sum of two numbers."

    result = await team.run(task=task)

    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    for message in result.messages:
        print(f"\n--- {message.source} ---")
        content = message.content if hasattr(message, "content") else str(message)
        print(content[:2000])

    print("\n" + "=" * 60)
    print("STOP REASON:", result.stop_reason)

asyncio.run(main())
