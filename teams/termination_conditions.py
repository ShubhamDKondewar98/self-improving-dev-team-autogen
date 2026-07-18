from autogen_agentchat.base import TerminatedException
#from autogen_agentchat.conditions import TokenUsageTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, StopMessage
from typing import Sequence
import json
from autogen_agentchat.base import TerminationCondition
 

class CriticVerdictTermination(TerminationCondition):
    """
    Stops the conversation when the Critic emits either:
      - verdict == "PASS" (task succeeded), or
      - failure_category == "AMBIGUOUS_REQUIREMENT" (unsolvable as specified,
        should not be retried — routes to human as a "possible planning gap").
    Both are terminal signals that selector_func deliberately never routes
    from (see RuntimeError guards in select()) — this class is what's
    actually responsible for stopping the run in both cases.
    """

    def __init__(self, critic_agent) -> None:
        self._terminated = False
        self.critic_agent = critic_agent
        

    @property
    def terminated(self) -> bool:
        return self._terminated

    async def __call__(self, messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> StopMessage | None:
        if self._terminated:
            raise TerminatedException("Termination condition has already been reached")

        for msg in messages:
            if msg.source == self.critic_agent.name:
                try:
                    verdict = json.loads(msg.content)
                except json.JSONDecodeError:
                    self._terminated = True
                    return StopMessage(
                        content="Run stopped early: Critic produced malformed JSON "
                                "(treated as a possible planning gap / unresolvable case).",
                        source="CriticVerdictTermination",
                    )

                if verdict["verdict"] == "PASS":
                    self._terminated = True
                    return StopMessage(
                        content="Run succeeded: Critic returned PASS verdict.",
                        source="CriticVerdictTermination",
                    )

                if verdict.get("failure_category") == "AMBIGUOUS_REQUIREMENT":
                    self._terminated = True
                    return StopMessage(
                        content="Run stopped early: Critic flagged AMBIGUOUS_REQUIREMENT "
                                "(possible planning gap, not retried).",
                        source="CriticVerdictTermination",
                    )

        return None
            
            
    async def reset(self) -> None:
        self._terminated = False


    

class RetryCapTermination(TerminationCondition):
    """
    Stops the conversation when either:
        - code_retry_count reaches max_code_retries, or
        - test_retry_count reaches max_test_retries.
    Reads live counters directly from the shared Selector instance (Option B)
    rather than re-deriving them from messages — Selector remains the single
    source of truth, since it's the only component that increments them.

    """

    def __init__(self, selector_instance) -> None:
        self._terminated = False
        self.selector_instance = selector_instance

    @property
    def terminated(self) -> bool:
        return self._terminated

    async def __call__(self, messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> StopMessage | None:
        if self._terminated:
            raise TerminatedException("Termination condition has already been reached")

        if self.selector_instance.code_retry_count >= self.selector_instance.max_code_retries:
            self._terminated = True
            return StopMessage(
                content=f"Run stopped early: code_retry_count ({self.selector_instance.code_retry_count}) "
                        f"reached max_code_retries ({self.selector_instance.max_code_retries}).",
                source="RetryCapTermination",
            )

        if self.selector_instance.test_retry_count >= self.selector_instance.max_test_retries:
            self._terminated = True
            return StopMessage(
                content=f"Run stopped early: test_retry_count ({self.selector_instance.test_retry_count}) "
                        f"reached max_test_retries ({self.selector_instance.max_test_retries}).",
                source="RetryCapTermination",
            )

        return None

    async def reset(self) -> None:
        self._terminated = False

                

#token_termination = TokenUsageTermination(max_total_token=60000)