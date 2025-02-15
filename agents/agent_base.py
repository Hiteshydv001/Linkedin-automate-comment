import google.generativeai as genai
from abc import ABC, abstractmethod
import streamlit as st
import time

# Configure Gemini API using Streamlit secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY is missing! Make sure to set it in Streamlit secrets.")

class AgentBase(ABC):
    def __init__(self, name, max_retries=3, verbose=True):
        self.name = name
        self.max_retries = max_retries
        self.verbose = verbose

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def call_gemini(self, prompt, model="gemini-pro"):
        """Calls Gemini AI with retries, backoff, and caching to avoid rate limits."""
        if not GEMINI_API_KEY:
            raise ValueError(f"[{self.name}] GEMINI_API_KEY is missing. Check Streamlit secrets.")

        # Check cache (avoid redundant API calls)
        cache_key = f"gemini_cache_{hash(prompt)}"
        if cache_key in st.session_state:
            if self.verbose:
                print(f"[{self.name}] Returning cached response.")
            return st.session_state[cache_key]

        retries = 0
        while retries < self.max_retries:
            try:
                if self.verbose:
                    print(f"[{self.name}] Sending prompt to Gemini ({model}): {prompt}")

                # Create a model instance
                gemini_model = genai.GenerativeModel(model)
                response = gemini_model.generate_content(prompt)

                if response and hasattr(response, "text"):
                    reply = response.text.strip()
                else:
                    reply = "No response generated."

                # Cache response
                st.session_state[cache_key] = reply

                if self.verbose:
                    print(f"[{self.name}] Received response: {reply}")
                return reply

            except Exception as e:
                if "429" in str(e) or "Resource has been exhausted" in str(e):
                    wait_time = 2 ** retries  # Exponential backoff: 2s, 4s, 8s...
                    print(f"[{self.name}] Rate limit reached. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)  # Wait before retrying
                else:
                    print(f"[{self.name}] Unexpected error: {e}")
                    break  # Stop retrying for non-rate-limit errors

            retries += 1

        # If `gemini-pro` fails, try `gemini-lite` as a fallback
        if model == "gemini-pro":
            print(f"[{self.name}] Switching to 'gemini-lite' due to failures.")
            return self.call_gemini(prompt, model="gemini-lite")

        raise Exception(f"[{self.name}] Failed to get response from Gemini after {self.max_retries} retries.")
