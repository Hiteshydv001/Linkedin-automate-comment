from .agent_base import AgentBase

class RefinerAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="RefinerAgent", max_retries=max_retries, verbose=verbose)

    def execute(self, draft):
        """Refines a LinkedIn post for clarity, engagement, and professional impact."""
        prompt = (
            "You are an expert social media editor who enhances LinkedIn posts for clarity, engagement, "
            "and professional impact.\n\n"
            "Please refine the following LinkedIn post draft to make it more engaging, concise, and impactful:\n\n"
            f"{draft}\n\nRefined LinkedIn Post:"
        )
        
        refined_post = self.call_gemini(prompt, model="gemini-pro")
        return refined_post
