from .summarize_tool import SummarizeTool
from .write_post_tool import WritePostTool
from .sanitize_data_tool import SanitizeDataTool
from .summarize_validator_agent import SummarizeValidatorAgent
from .write_post_validator_agent import WritePostValidatorAgent
from .sanitize_data_validator_agent import SanitizeDataValidatorAgent
from .refiner_agent import RefinerAgent
from .validator_agent import ValidatorAgent
from .generate_comment_agent import GenerateCommentAgent
from .sentiment_analysis_agent import SentimentAnalysisAgent

class AgentManager:
    def __init__(self, max_retries=2, verbose=True):
        self.agents = {
            "summarize": SummarizeTool(max_retries=max_retries, verbose=verbose),
            "write_post": WritePostTool(max_retries=max_retries, verbose=verbose),
            "sanitize_data": SanitizeDataTool(max_retries=max_retries, verbose=verbose),
            "summarize_validator": SummarizeValidatorAgent(max_retries=max_retries, verbose=verbose),
            "write_post_validator": WritePostValidatorAgent(max_retries=max_retries, verbose=verbose),
            "sanitize_data_validator": SanitizeDataValidatorAgent(max_retries=max_retries, verbose=verbose),
            "refiner": RefinerAgent(max_retries=max_retries, verbose=verbose),
            "validator": ValidatorAgent(max_retries=max_retries, verbose=verbose),
            "generate_comment": GenerateCommentAgent(max_retries=max_retries, verbose=verbose),
            "sentiment_analysis": SentimentAnalysisAgent(max_retries=max_retries, verbose=verbose),
        }

    def get_agent(self, agent_name):
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        return agent
