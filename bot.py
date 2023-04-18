from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from chatgpt_interaction import generate_response
from dalle_interaction import generate_image_command
from commands import start, new_conversation, stop_conversation, settings_command, help_command
from utils import logger, TELEGRAM_BOT_TOKEN

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
    settings_handler = CommandHandler("settings", settings_command)
    image_handler = CommandHandler("image", generate_image_command)

    # Add handlers to updater
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(new_handler)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(image_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")