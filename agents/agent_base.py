import google.generativeai as genai
from abc import ABC, abstractmethod
import os
import time
from dotenv import load_dotenv  # ✅ Import dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Fetch API key from environment vars
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Ensure you have a .env file with the API key.")

# ✅ Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

class AgentBase(ABC):
    def __init__(self, name, max_retries=3, verbose=True):
        self.name = name
        self.max_retries = max_retries
        self.verbose = verbose
        self.cache = {}  # In-memory cache

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def call_gemini(self, prompt, model="gemini-pro"):
        """Calls Gemini AI with retries, backoff, and caching to avoid rate limits."""
        if not GEMINI_API_KEY:
            raise ValueError(f"[{self.name}] GEMINI_API_KEY is missing. Check environment variables.")

        # Check cache (avoid redundant API calls)
        cache_key = hash(prompt)
        if cache_key in self.cache:
            if self.verbose:
                print(f"[{self.name}] Returning cached response.")
            return self.cache[cache_key]

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
                self.cache[cache_key] = reply

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
