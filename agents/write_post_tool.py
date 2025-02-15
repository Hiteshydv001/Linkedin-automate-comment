from .agent_base import AgentBase

class WritePostTool(AgentBase):
    def __init__(self, max_retries=3, verbose=True):
        super().__init__(name="WriteArticleTool", max_retries=max_retries, verbose=verbose)

    def execute(self, topic, outline=None):
        """Generates an engaging LinkedIn post based on the given topic and outline."""
        prompt = f"You are an expert LinkedIn content writer.\n\nWrite a compelling and engaging LinkedIn post on the following topic:\nTopic: {topic}\n\n"
        
        if outline:
            prompt += f"Outline:\n{outline}\n\n"
        
        prompt += "Post:\n"

        # Call Gemini to generate the LinkedIn post
        post = self.call_gemini(prompt, model="gemini-pro")
        return post
