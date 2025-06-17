import os
from autogen import LLMConfig

# Set all required environment variables here, or load via dotenv (recommended in prod)
os.environ['GEMINI_API_KEY'] = os.getenv("GEMINI_API_KEY", 'AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA')
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0449161426")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json")

llm_config = LLMConfig(
    api_type="google",
    model="gemini-2.5-flash-preview-05-20"
)
