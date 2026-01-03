import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
    ZHIPU_API_URL = os.getenv("ZHIPU_API_URL")
    HOST = "0.0.0.0"
    PORT = 5000
    CORS_ORIGINS = "*"

config = Config()