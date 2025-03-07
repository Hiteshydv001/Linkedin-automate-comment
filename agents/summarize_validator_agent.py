from .agent_base import AgentBase

class SummarizeValidatorAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="SummarizeValidatorAgent", max_retries=max_retries, verbose=verbose)

    def execute(self, original_text, summary):
        """Validates the accuracy and quality of a LinkedIn post summary."""
        prompt = (
            "You are an AI assistant that evaluates the quality of LinkedIn post summaries.\n\n"
            "Given the original LinkedIn post and its summary, determine whether the summary accurately and concisely captures the key insights.\n"
            "Provide a brief analysis and rate the summary on a scale of 1 to 5, where 5 indicates excellent quality.\n\n"
            f"Original Post:\n{original_text}\n\n"
            f"Summary:\n{summary}\n\n"
            "Evaluation:"
        )

        validation = self.call_gemini(prompt, model="1.5-flash")
        return validation