from teams.dev_team import build_dev_team
import json


async def run_dev_team(task: str) -> dict:
    """
    Runs one full dev-team loop for the given task and returns a plain
    dict describing the outcome. Does NOT write to disk -- that's
    attempt_logger.py's job, called separately.
    """
    

    team , selector_instance  = build_dev_team()
    result = await team.run(task=task)

    final_code = None
    critic_reasoning = None
    failure_category = None
    final_verdict = "UNKNOWN"
    final_test_result = None

    for message in reversed(result.messages):
        source = getattr(message, "source", None)
        content = getattr(message, "content", None)

        if not isinstance(content, str):
            continue

        if source == "critic_agent" and critic_reasoning is None:
            try:
                verdict_data = json.loads(content)
                final_verdict = verdict_data.get("verdict", "UNKNOWN")
                critic_reasoning = verdict_data.get("reasoning")
                failure_category = verdict_data.get("failure_category")
            except json.JSONDecodeError:
                critic_reasoning = "Critic produced malformed output on final message."

        if source == "coder_agent" and final_code is None:
            try:
                coder_data = json.loads(content)
                final_code = coder_data.get("code")
            except json.JSONDecodeError:
                pass

        if source == "test_agent" and final_test_result is None:
            try:
                final_test_result = json.loads(content)
            except json.JSONDecodeError:
                pass


        if final_code is not None and critic_reasoning is not None and final_test_result is not None:
            break


    messages_summary = [
    {"source": getattr(m, "source", None), "content": getattr(m, "content", None)}
    for m in result.messages
    if isinstance(getattr(m, "content", None), str)
]

    return {
        "task": task,
        "stop_reason": result.stop_reason,
        "final_verdict": final_verdict,
        "final_code": final_code,
        "critic_reasoning": critic_reasoning,
        "failure_category": failure_category,
        "final_test_result": final_test_result,
        "code_retry_count": selector_instance.code_retry_count,
        "test_retry_count": selector_instance.test_retry_count,
        "messages": messages_summary,
    }