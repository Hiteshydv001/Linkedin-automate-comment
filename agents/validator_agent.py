from .agent_base import AgentBase

class ValidatorAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="ValidatorAgent", max_retries=max_retries, verbose=verbose)

    def execute(self, topic, article):
        """Validates the quality and relevance of a LinkedIn post."""
        prompt = (
            "You are an AI assistant that evaluates LinkedIn posts for clarity, engagement, and relevance.\n\n"
            "Given the topic and the LinkedIn post below, assess whether the post effectively covers the topic, maintains engagement, and aligns with professional standards.\n"
            "Provide a brief analysis and rate the post on a scale of 1 to 5, where 5 indicates excellent quality.\n\n"
            f"Topic: {topic}\n\n"
            f"Post:\n{article}\n\n"
            "Evaluation:"
        )

        # Call Gemini to validate the post
        validation = self.call_gemini(prompt, model="1.5-flash")
        return validation