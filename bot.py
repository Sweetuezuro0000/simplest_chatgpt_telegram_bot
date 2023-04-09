import os
import openai
import telegram

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv

# Load environment variables from tokens.env file
load_dotenv('tokens.env')

# Set up Telegram bot
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Set up OpenAI API client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL_ID = os.environ.get("OPENAI_MODEL_ID")
openai.api_key = OPENAI_API_KEY
chat_history = {}


def start(update, context):
    """Send a greeting message and the available commands to the user."""
    update.message.reply_text("Hello! I'm a Simplest ChatGPT bot. Send me a message and I'll try to respond. \n\nAvailable commands:\n/new - Start a new conversation\n/stop - Stop the current conversation and delete context\n/help - Show this help message")


def generate_response(update, context):
    """Generate a response message using OpenAI API."""
    message = update.message.text
    if chat_history.get(update.message.chat_id) is None:
        chat_history[update.message.chat_id] = []
    chat_history[update.message.chat_id].append(message)
    response = generate_text(chat_history[update.message.chat_id])
    update.message.reply_text(response)
    chat_history[update.message.chat_id].append(response)


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


def generate_text(chat_history):
    """Generate a response message using OpenAI API."""
    prompt = "\n".join(chat_history[-5:])
    response = openai.Completion.create(
        engine=OPENAI_MODEL_ID,
        prompt=prompt,
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = response.choices[0].text.strip()
    return message


def help_command(update, context):
    """Send the available commands to the user."""
    help_message = "Available commands:\n/new - Start a new conversation\n/stop - Stop the current conversation and delete context\n/help - Show this help message"
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

    # Add handlers to updater
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(new_handler)
    updater.dispatcher.add_handler(stop_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()