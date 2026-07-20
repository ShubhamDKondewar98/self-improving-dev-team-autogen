from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from config.constants import MODEL_NAME
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

model_client = OpenAIChatCompletionClient(model=MODEL_NAME, api_key=api_key)