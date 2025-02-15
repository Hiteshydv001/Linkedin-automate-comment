from .agent_base import AgentBase

class SanitizeDataTool(AgentBase):
    def __init__(self, max_retries=3, verbose=True):
        super().__init__(name="SanitizeDataTool", max_retries=max_retries, verbose=verbose)

    def execute(self, data):
        """Sanitizes data by removing sensitive information."""
        prompt = (
            "You are an AI assistant that sanitizes data by removing sensitive information.\n\n"
            "Remove all sensitive information from the following data:\n\n"
            f"{data}\n\nSanitized Data:"
        )

        sanitized_data = self.call_gemini(prompt, model="gemini-pro")
        return sanitized_data
