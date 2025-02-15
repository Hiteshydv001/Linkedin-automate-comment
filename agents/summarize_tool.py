from .agent_base import AgentBase

class SummarizeTool(AgentBase):
    def __init__(self, max_retries=3, verbose=True):
        super().__init__(name="SummarizeTool", max_retries=max_retries, verbose=verbose)

    def execute(self, text):
        """Summarizes any LinkedIn post concisely for better insights."""
        prompt = (
            "You are an AI assistant specializing in summarizing LinkedIn posts for quick insights.\n\n"
            "Please generate a concise and insightful summary of the following LinkedIn post:\n\n"
            f"{text}\n\nSummary:"
        )

        summary = self.call_gemini(prompt, model="gemini-pro")
        return summary