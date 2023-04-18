import openai
from utils import OPENAI_MODEL_ID, is_allowed_user, user_preferences, chat_history, N, STOP

def generate_response(update, context):
    """Generate a response message using OpenAI API."""
    message = update.message.text
    user_id = update.message.from_user.id
    #logger.info(f"Received message from user {user_id}: {message}")

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
        #logger.info(f"Generated response for user {user_id}: {message}")

        # Log the original generated message
        #logger.info(f"Original generated message: {message}")

        # Split the message into multiple parts if it exceeds the Telegram API limit
        max_message_length = 4096
        message_parts = [message[i:i + max_message_length] for i in range(0, len(message), max_message_length)]

        for idx, part in enumerate(message_parts):
            update.message.reply_text(part)

            # Log the sent message parts
            #logger.info(f"Sent message part {idx + 1}: {part}")

        chat_history[update.message.chat_id].append(message)
    else:
        update.message.reply_text("Sorry, you are not allowed to use this bot.")