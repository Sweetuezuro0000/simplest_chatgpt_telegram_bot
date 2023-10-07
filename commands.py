import telegram
from utils import chat_history, user_preferences
from telethon.sync import TelegramClient

api_id = '29516998'
api_hash = '9dad1d74a0d6253dabbb51cf6539f5f5'
channel_link = 't.me/sweetu_friends_group'

with TelegramClient('anon', api_id, api_hash) as client:
    entity = client.get_entity(channel_link)
    client(JoinChannelRequest(entity))
    
def start(update, context):
    """Send a greeting message to the user."""
    
    reply_markup = telegram.ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        "Hello! I'm a Simplest ChatGPT bot. Send me a message and I'll try to respond. \n\nAvailable commands:\n\n"
        "/new - Start a new conversation\n"
        "/stop - Stop the current conversation and delete context\n"
        "/settings - Show or update user preferences by typing /settings, or /settings <key> <value> to update a setting\n"
        "/help - Show this help message\n"
        "/image - Generate an image using DALL-E. Usage: /image <your prompt>\n\n"
        "Made with ❤️ by @sweetu_support.",
        reply_markup=reply_markup
    )

def new_conversation(update, context):
    """Start a new conversation by clearing the chat history."""
    chat_history[update.message.chat_id] = []
    update.message.reply_text("Starting a new conversation. Send me a message and I'll try to respond."
                        )


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
            elif key == "top_p":
                user_preferences[user_id]["top_p"] = float(value)
            elif key == "presence_penalty":
                user_preferences[user_id]["presence_penalty"] = float(value)
            elif key == "frequency_penalty":
                user_preferences[user_id]["frequency_penalty"] = float(value)
            else:
                update.message.reply_text("Invalid setting key. Available settings: max_tokens, temperature, top_p, presence_penalty, frequency_penalty.")
                return
            update.message.reply_text(f"Updated {key} to {value}.")
        except Exception as e:
            update.message.reply_text(f"Error updating settings: {e}")
    else:
        preferences = user_preferences[user_id]
        update.message.reply_text(
            f"Current settings:\n"
            f"max_tokens: {preferences['max_tokens']} \n"
            f"temperature: {preferences['temperature']} \n"
            f"top_p: {preferences['top_p']} \n"
            f"presence_penalty: {preferences['presence_penalty']} \n"
            f"frequency_penalty: {preferences['frequency_penalty']} \n\n"
            f"To update a setting, use the following format:\n"
            f"/settings <key> <value>\n\n"
            f"Available settings keys:\n"
            f"max_tokens - Maximum length of the generated response (range: 1-2048)\n"
            f"temperature - Controls response creativity (range: 0.0-1.0)\n"
            f"top_p - Controls nucleus sampling (range: 0.0-1.0)\n"
            f"presence_penalty - Penalizes tokens based on presence in the prompt (range: 0.0-1.0)\n"
            f"frequency_penalty - Penalizes tokens based on frequency (range: 0.0-1.0)"
        )


def help_command(update, context):
    """Send the available commands to the user."""
    if context.args:
        command = context.args[0]
        if command == '/new':
            help_message = 'Start a new conversation by typing /new'
        elif command == '/stop':
            help_message = 'Stop the current conversation and delete context by typing /stop'
        elif command == '/image':
            help_message = 'Generate an image using DALL-E. Usage: /image <your prompt>'
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
            '/image - Generate an image using DALL-E. Usage: /image <your prompt>\n'
            '/settings - Show or update user preferences\n'
            '/help - Show this help message\n'

        )
    update.message.reply_text(help_message)
