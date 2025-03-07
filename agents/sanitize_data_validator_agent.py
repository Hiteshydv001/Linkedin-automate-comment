from .agent_base import AgentBase

class SanitizeDataValidatorAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="SanitizeDataValidatorAgent", max_retries=max_retries, verbose=verbose)

    def execute(self, original_data, sanitized_data):
        """Validates that sensitive information has been removed from data."""
        prompt = (
            "You are an AI assistant that validates the sanitization of data by checking for the removal of sensitive information.\n\n"
            "Given the original data and the sanitized data, verify that all sensitive information has been removed.\n"
            "List any remaining sensitive information in the sanitized data and rate the sanitization process on a scale of 1 to 5, where 5 indicates complete sanitization.\n\n"
            f"Original Data:\n{original_data}\n\n"
            f"Sanitized Data:\n{sanitized_data}\n\n"
            "Validation:"
        )

        validation = self.call_gemini(prompt, model="1.5-flash")
        return validation
