from .agent_base import AgentBase

class WritePostValidatorAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="WritePostValidatorAgent", max_retries=max_retries, verbose=verbose)

    def execute(self, topic, article):
        """Validates a generated research article for its quality, structure, and relevance to the topic."""
        prompt = (
            "You are an AI assistant that validates research articles.\n\n"
            "Given the topic and the article, assess whether the article comprehensively covers the topic, follows a logical structure, and maintains academic standards.\n"
            "Provide a brief analysis and rate the article on a scale of 1 to 5, where 5 indicates excellent quality.\n\n"
            f"Topic: {topic}\n\n"
            f"Article:\n{article}\n\n"
            "Validation:"
        )

        # Call Gemini to validate the article
        validation = self.call_gemini(prompt, model="1.5-flash")
        return validation
