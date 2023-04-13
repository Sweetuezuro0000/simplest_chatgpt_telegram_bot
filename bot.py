import os
import openai
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from dotenv import load_dotenv
from typing import List
import logging

load_dotenv('private/tokens.env')

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL_ID = os.environ.get("OPENAI_MODEL_ID")
openai.api_key = OPENAI_API_KEY
chat_history = {}


def load_allowed_users() -> List[int]:
    """
    Description: Loads and returns a list of allowed user IDs from a file.
    Returns: List of integers representing allowed user IDs.
    """
    try:
        with open('private/allowed_users.txt', 'r') as f:
            return [int(line.strip()) for line in f.readlines()]
    except FileNotFoundError:
        logging.warning("Allowed users file not found.")
        return []
    except Exception as e:
        logging.error("Error occurred while loading allowed users:", e)
        return []


ALLOWED_USERS = load_allowed_users()


def is_allowed_user(user_id: int) -> bool:
    """
    Description: Checks if the given user ID is in the list of allowed user IDs.
    Parameters: user_id (integer) - the user ID to check.
    Returns: True if the user is allowed, False otherwise.
    """
    if not ALLOWED_USERS:
        return True
    return user_id in ALLOWED_USERS


def load_config() -> dict:
    """
    Description: Loads and returns configuration settings from an environment file.
    Returns: Dictionary containing configuration settings.
    """
    try:
        load_dotenv("private/config.env")
        config = os.environ
        return config
    except FileNotFoundError:
        logging.error("Config file not found.")
        return {}
    except Exception as e:
        logging.error("Error occurred while loading config: %s", e)
        return {}



def start(update: Update, context: CallbackContext) -> None:
    """
    Description: Handles the /start command by sending a welcome message and displaying a set of available commands.
    Parameters: update (telegram.Update) - the incoming message update, context (telegram.ext.CallbackContext) - context object to pass extra data.
    Returns: None.
    """
    buttons = [
        [KeyboardButton("/new"), KeyboardButton("/stop")],
        [KeyboardButton("/help")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        "Hello! I'm a Simplest ChatGPT bot. Send me a message and I'll try to respond. \n\nAvailable commands:\n/new - Start a new conversation\n/stop - Stop the current conversation and delete context\n/help - Show this help message",
        reply_markup=reply_markup
    )


def generate_response(update: Update, context: CallbackContext) -> None:
    """
    Description: Generates a response message using OpenAI's GPT-3 language model and sends it to the user.
    Parameters: update (telegram.Update) - the incoming message update, context (telegram.ext.CallbackContext) - context object to pass extra data.
    Returns: None.
    """
    user_id = update.message.from_user.id

    if is_allowed_user(user_id):
        if chat_history.get(update.message.chat_id) is None:
            chat_history[update.message.chat_id] = []
        chat_history[update.message.chat_id].append(update.message.text)

        prompt = "\n".join(chat_history[update.message.chat_id][-5:])
        config = load_config()
        try:
            response = openai.Completion.create(
                engine=config.get("OPENAI_MODEL_ID", ""),
                prompt=prompt,
                max_tokens=int(config.get("MAX_TOKENS", 2048)),
                n=int(config.get("N", 1)),
                stop=config.get("STOP", None),
                temperature=float(config.get("TEMPERATURE", 0.5)),
            )
            message = response.choices[0].text.strip()

            update.message.reply_text(message)

            chat_history[update.message.chat_id].append(message)
        except openai.Error as e:
            logging.error(f"OpenAI API request failed: {e}")
            update.message.reply_text("Sorry, an error occurred while processing your request.")
    else:
        update.message.reply_text("Sorry, you are not allowed to use this bot.")



def new_conversation(update: Update, context: CallbackContext) -> None:
    """
    Description: Handles the /new command by starting a new conversation and clearing the chat history.
    Parameters: update (telegram.Update) - the incoming message update, context (telegram.ext.CallbackContext) - context object to pass extra data.
    Returns: None.
    """
    chat_history[update.message.chat_id] = []
    update.message.reply_text("Starting a new conversation. Send me a message and I'll try to respond.")


def stop_conversation(update: Update, context: CallbackContext) -> None:
    """
    Description: Handles the /stop command by stopping the current conversation and deleting the chat history.
    Parameters: update (telegram.Update) - the incoming message update, context (telegram.ext.CallbackContext) - context object to pass extra data.
    Returns: None.
    """
    if chat_history.get(update.message.chat_id) is not None:
        chat_history[update.message.chat_id] = []
        update.message.reply_text("Conversation context has been deleted.")
    else:
        update.message.reply_text("There is no conversation context to delete.")


def help_command(update: Update, context: CallbackContext) -> None:
    """
    Description: Handles the /help command by sending a help message that lists the available commands.
    Parameters: update (telegram.Update) - the incoming message update, context (telegram.ext.CallbackContext) - context object to pass extra data.
    Returns: None.
    """
    help_message = 'Available commands:\n/new - Start a new conversation\n/stop - Stop the current conversation and delete context\n/help - Show this help message'
    update.message.reply_text(help_message)


def main() -> None:
    """
    Description: Starts the Telegram bot and sets up the necessary handlers.
    Returns: None.
    """
    logging.basicConfig(filename='chatbot.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    updater = Updater(TELEGRAM_BOT_TOKEN)

    start_handler = CommandHandler("start", start)
    message_handler = MessageHandler(Filters.text & ~Filters.command, generate_response)
    help_handler = CommandHandler("help", help_command)
    new_handler = CommandHandler("new", new_conversation)
    stop_handler = CommandHandler("stop", stop_conversation)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(new_handler)
    dispatcher.add_handler(stop_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()