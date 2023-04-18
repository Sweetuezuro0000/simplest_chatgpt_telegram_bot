import os
import openai
import logging
import telegram
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables from tokens.env file
load_dotenv('private/tokens.env')

# Load basic configuration from config.env file
load_dotenv('private/config.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# Set up Telegram bot
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Set up OpenAI API client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL_ID = os.environ.get("OPENAI_MODEL_ID")
openai.api_key = OPENAI_API_KEY
chat_history = {}

# Load basic configuration values from the environment variables
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", 2048))
N = int(os.environ.get("N", 1))
STOP = os.environ.get("STOP", None)
if STOP == "null":
    STOP = None
TEMPERATURE = float(os.environ.get("TEMPERATURE", 0.5))
TOP_P = float(os.environ.get("TOP_P", 1.0))
PRESENCE_PENALTY = float(os.environ.get("PRESENCE_PENALTY", 0.0))
FREQUENCY_PENALTY = float(os.environ.get("FREQUENCY_PENALTY", 0.0))


# Create a dictionary to store user preferences
user_preferences = defaultdict(lambda: {"max_tokens": MAX_TOKENS, "temperature": TEMPERATURE, "top_p": TOP_P, "presence_penalty": PRESENCE_PENALTY, "frequency_penalty": FREQUENCY_PENALTY})


def is_allowed_user(user_id):
    logger.info(f"Checking user ID: {user_id}")
    """
    Checks if the given user ID is allowed to use the bot.
    Returns True if the user is allowed, False otherwise.
    """
    try:
        # Read the list of allowed user IDs from a file
        with open('private/allowed_users.txt', 'r') as f:
            allowed_users = [int(line.strip()) for line in f.readlines()]

        # If the list is empty, everyone is allowed
        if not allowed_users:
            return True

        # Check if the user's ID is in the list of allowed user IDs
        return user_id in allowed_users

    except FileNotFoundError:
        logger.error("Allowed users file not found.")
        return False

    except Exception as e:
        logger.error(f"Error occurred while checking allowed users: {e}")
        return False