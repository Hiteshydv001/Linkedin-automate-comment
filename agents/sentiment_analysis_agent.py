from .agent_base import AgentBase

class SentimentAnalysisAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="SentimentAnalysisAgent", max_retries=max_retries, verbose=verbose)

    def execute(self, text):
        """Analyzes sentiment of the given text."""
        prompt = (
            "You are an expert in sentiment analysis. Determine the sentiment of the following text "
            "and provide a concise summary:\n\n"
            f"Text: {text}\n\nSentiment:"
        )
        sentiment = self.call_gemini(prompt, model="1.5-flash")
        return sentiment
