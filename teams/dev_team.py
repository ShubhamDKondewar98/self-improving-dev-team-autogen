from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TokenUsageTermination

from agents.planner_agent import planner_agent
from agents.coder_agent import coder_agent
from agents.test_agent import test_agent
from agents.critic_agent import critic_agent

from teams.selector_func import SelectorFunc
from teams.termination_conditions import CriticVerdictTermination, RetryCapTermination

from config.constants import MAX_CODE_RETRIES, MAX_TEST_RETRIES, MAX_TOTAL_TOKENS
from models.openai_model_client import model_client


def build_dev_team() -> SelectorGroupChat:
    """
    Assembles the fully-wired SelectorGroupChat for one run of the
    self-improving dev team loop.

    NOTE: call this fresh for EACH new run/task. Creating a new
    SelectorFunc instance here (not reusing one across runs) gives each
    run isolated, fresh retry counters.
    """

    selector_instance = SelectorFunc(
        code_retry_count=0,
        test_retry_count=0,
        max_code_retries=MAX_CODE_RETRIES,
        max_test_retries=MAX_TEST_RETRIES,
        coder_agent=coder_agent,
        critic_agent=critic_agent,
        planner_agent=planner_agent,
        test_agent=test_agent,
    )

    critic_verdict_termination = CriticVerdictTermination(critic_agent)
    retry_cap_termination = RetryCapTermination(selector_instance)
    token_termination = TokenUsageTermination(max_total_token=MAX_TOTAL_TOKENS)

    combined_termination = critic_verdict_termination | retry_cap_termination | token_termination

    team = SelectorGroupChat(
        participants=[planner_agent, coder_agent, test_agent, critic_agent],
        model_client=model_client,
        selector_func=selector_instance.select,
        termination_condition=combined_termination,
        allow_repeated_speaker=True,
    )

    return team