import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "default_gemini_key")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "default_weather_key")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "default_github_token")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Bot Settings
DEFAULT_PREFIX = "!"
BOT_NAME = "Gemini AI Discord Bot"
BOT_VERSION = "1.0.0"
BOT_COLOR = 0x00ff00

# Database Settings
DATABASE_PATH = "bot_database.db"

# Music Settings
MUSIC_VOLUME = 0.5
MAX_QUEUE_SIZE = 50

# Economy Settings
DAILY_REWARD = 100
BEG_MIN = 10
BEG_MAX = 50
CRIME_MIN = 50
CRIME_MAX = 200
CRIME_FAIL_PENALTY = 25

# Image Settings
MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8MB
SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.gif', '.webp']

# API Endpoints
MEME_API = "https://meme-api.herokuapp.com/gimme"
CAT_API = "https://api.thecatapi.com/v1/images/search"
DOG_API = "https://api.thedogapi.com/v1/images/search"
FACT_API = "https://uselessfacts.jsph.pl/random.json?language=en"
JOKE_API = "https://official-joke-api.appspot.com/random_joke"

# Gemini Settings
DEFAULT_MODEL = "gemini-2.5-flash"
PRO_MODEL = "gemini-2.5-pro"
