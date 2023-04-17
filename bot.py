import os
import openai
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables from tokens.env file
load_dotenv('private/tokens.env')

# Load basic configuration from config.env file
load_dotenv('private/config.env')

# Load basic configuration values from the environment variables
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", 2048))
N = int(os.environ.get("N", 1))
STOP = os.environ.get("STOP", None)
if STOP == "null":
    STOP = None
TEMPERATURE = float(os.environ.get("TEMPERATURE", 0.5))

# Create a dictionary to store user preferences
user_preferences = defaultdict(lambda: {"max_tokens": MAX_TOKENS, "temperature": TEMPERATURE, "language": "en"})



# Set up Telegram bot
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Set up OpenAI API client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL_ID = os.environ.get("OPENAI_MODEL_ID")
openai.api_key = OPENAI_API_KEY
chat_history = {}

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

def start(update, context):
    """Send a greeting message and the available commands as buttons to the user."""
    buttons = [
        [telegram.KeyboardButton("/new"), telegram.KeyboardButton("/stop")],
        [telegram.KeyboardButton("/settings"), telegram.KeyboardButton("/help")]
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        "Hello! I'm a Simplest ChatGPT bot. Send me a message and I'll try to respond. \n\nAvailable commands:\n"
        "/new - Start a new conversation\n"
        "/stop - Stop the current conversation and delete context\n"
        "/settings - Show or update user preferences by typing /settings, or /settings <key> <value> to update a setting\n"
        "/help - Show this help message",
        reply_markup=reply_markup
    )


def generate_response(update, context):
    """Generate a response message using OpenAI API."""
    message = update.message.text
    user_id = update.message.from_user.id

    if is_allowed_user(user_id):
        # Get user preferences
        preferences = user_preferences[user_id]

        if chat_history.get(update.message.chat_id) is None:
            chat_history[update.message.chat_id] = []
        chat_history[update.message.chat_id].append(message)

        prompt = "\n".join(chat_history[update.message.chat_id][-5:])
        response = openai.Completion.create(
            engine=OPENAI_MODEL_ID,
            prompt=prompt,
            max_tokens=preferences["max_tokens"],
            n=N,
            stop=STOP,
            temperature=preferences["temperature"],
        )
        message = response.choices[0].text.strip()

        update.message.reply_text(message)

        chat_history[update.message.chat_id].append(message)
    else:
        update.message.reply_text("Sorry, you are not allowed to use this bot.")

def new_conversation(update, context):
    """Start a new conversation by clearing the chat history."""
    chat_history[update.message.chat_id] = []
    update.message.reply_text("Starting a new conversation. Send me a message and I'll try to respond.")


def stop_conversation(update, context):
    """Stop the current conversation by deleting the chat history."""
    if chat_history.get(update.message.chat_id) is not None:
        chat_history[update.message.chat_id] = []
        update.message.reply_text("Conversation context has been deleted.")
    else:
        update.message.reply_text("There is no conversation context to delete.")

def settings_command(update, context):
    """Show or update user preferences."""
    user_id = update.message.from_user.id
    args = context.args

    if args:
        try:
            key, value = args[0], args[1]
            if key == "max_tokens":
                user_preferences[user_id]["max_tokens"] = int(value)
            elif key == "temperature":
                user_preferences[user_id]["temperature"] = float(value)
            else:
                update.message.reply_text("Invalid setting key. Available settings: max_tokens, temperature.")
                return
            update.message.reply_text(f"Updated {key} to {value}.")
        except (ValueError, IndexError):
            update.message.reply_text("Invalid setting value or format. Use /settings <key> <value> to update a setting.")
    else:
        preferences = user_preferences[user_id]
        update.message.reply_text(
            f"Current settings:\n"
            f"max_tokens: {preferences['max_tokens']} \n"
            f"temperature: {preferences['temperature']} \n\n"
            f"To update a setting, use the following format:\n"
            f"/settings <key> <value>\n\n"
            f"Available settings keys:\n"
            f"max_tokens - Maximum length of the generated response (range: 1-2048)\n"
            f"temperature - Controls response creativity (range: 0.0-1.0)"
        )


def help_command(update, context):
    """Send the available commands to the user."""
    if context.args:
        command = context.args[0]
        if command == '/new':
            help_message = 'Start a new conversation by typing /new'
        elif command == '/stop':
            help_message = 'Stop the current conversation and delete context by typing /stop'
        elif command == '/settings':
            help_message = 'Show or update user preferences by typing /settings, or /settings <key> <value> to update a setting.'
        elif command == '/help':
            help_message = 'Show the available commands by typing /help'
        else:
            help_message = 'Sorry, that command is not recognized. Please type /help for a list of available commands.'
    else:
        help_message = (
            'Available commands:\n'
            '/new - Start a new conversation\n'
            '/stop - Stop the current conversation and delete context\n'
            '/settings - Show or update user preferences\n'
            '/help - Show this help message'
        )

    update.message.reply_text(help_message)


def main():
    """Set up and start the Telegram bot."""
    # Set up Telegram bot updater
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Set up command handlers
    start_handler = CommandHandler("start", start)
    message_handler = MessageHandler(Filters.text & ~Filters.command, generate_response)
    help_handler = CommandHandler("help", help_command)
    new_handler = CommandHandler("new", new_conversation)
    stop_handler = CommandHandler("stop", stop_conversation)
    # Add a new command handler for the settings command
    settings_handler = CommandHandler("settings", settings_command)


    # Add handlers to updater
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(new_handler)
    dispatcher.add_handler(stop_handler)
    # Add a new command handler for the settings command
    dispatcher.add_handler(settings_handler)
    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")