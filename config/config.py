import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

VECTORSTORE_PATH = "vectorstore"
DATA_PATH = "data"

MODEL_NAME = "gemini-2.5-flash"