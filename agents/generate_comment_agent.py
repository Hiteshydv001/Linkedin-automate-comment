from .agent_base import AgentBase

class GenerateCommentAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="GenerateCommentAgent", max_retries=max_retries, verbose=verbose)

    def execute(self, post_content):
        """Generates a relevant LinkedIn comment for the given post."""
        prompt = (
            "You are an expert at generating engaging LinkedIn comments. Based on the given post content, "
            "write a professional, insightful, and engaging comment:\n\n"
            f"Post: {post_content}\n\nGenerated Comment:"
        )
        comment = self.call_gemini(prompt, model="gemini-pro")
        return comment
