from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from typing import Sequence
import json

class SelectorFunc():

    def __init__(self, code_retry_count, test_retry_count, max_code_retries, max_test_retries,
                 coder_agent, critic_agent, planner_agent, test_agent):
        self.code_retry_count = code_retry_count
        self.test_retry_count = test_retry_count
        self.max_code_retries = max_code_retries
        self.max_test_retries = max_test_retries
        self.coder_agent = coder_agent
        self.critic_agent = critic_agent
        self.planner_agent = planner_agent
        self.test_agent = test_agent

    
    def select(self, messages):
        last_message = messages[-1]

        # Case 1: conversation just started, nobody has spoken yet
        if len(messages) == 1:
            return self.planner_agent.name  

        # Case 2: Planner just finished planning
        if last_message.source == self.planner_agent.name:
            return self.coder_agent.name

        # Case 3: Coder just finished writing/fixing code
        if last_message.source == self.coder_agent.name:
            return self.test_agent.name 

        # Case 4: Test-writer just finished — need to parse its structured output
        if last_message.source == self.test_agent.name:
            result = json.loads(last_message.content)

            if result["execution_status"] == "INFRA_ERROR":
                self.test_retry_count = self.test_retry_count + 1
                return self.test_agent.name

            elif result["execution_status"] == "COMPLETED":
                return self.critic_agent.name
            
            else :
                raise RuntimeError(f"select() reached unexpected execution_status: {result['execution_status']}")

        # Case 5: Critic just finished — this is the branchiest one, parse its JSON too
        if last_message.source == self.critic_agent.name:
            verdict = json.loads(last_message.content)

            if verdict["verdict"] == "PASS":
                raise RuntimeError("select() reached PASS branch — termination_condition should have stopped this")

            elif verdict["failure_category"] == "CODE_BUG":
                self.code_retry_count = self.code_retry_count + 1
                return self.coder_agent.name
            
            elif verdict["failure_category"] == "TEST_BUG":
                self.test_retry_count = self.test_retry_count + 1
                return self.test_agent.name
            
            elif verdict["failure_category"] == "AMBIGUOUS_REQUIREMENT":
                raise RuntimeError("select() reached AMBIGUOUS_REQUIREMENT branch — termination_condition should have stopped this")
            
            else:
                raise RuntimeError(f"select() reached unexpected failure_category: {verdict['failure_category']}")

            

        raise RuntimeError(f"select() reached unexpected last_message.source: {last_message.source}")
            





    def my_selector_fun(self,messages: Sequence[BaseAgentEvent | BaseChatMessage]):
        pass 



 #whos_next =  messages[-1].source     ###   data for whos_next   need to be capture 
getcount = SelectorFunc(0,0,0,0)   ##  passing xount zero initially 

#getcount.lastcalled(whos_next)


    
        