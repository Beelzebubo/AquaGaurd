import os
# os module import gareko yesle .env file bata variables load garna help garaxa which is imp for api calling and other config
from dotenv import load_dotenv
# load_dotnev () le .env file bata environment and variables load garna help garxa
load_dotenv()
# Ya tala GEMINI and ELEVENLABS ko APi keys load hunxa
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")