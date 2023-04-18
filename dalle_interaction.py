import openai
import requests
from utils import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_image(prompt, n=1, size="1024x1024", response_format="url", user=None):
    try:
        api_url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {openai.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format
        }

        if user:
            data["user"] = user

        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        image_url = response_data['data'][0]['url']
        return image_url
    except Exception as e:
        raise e

def generate_image_command(update, context):
    """Generate an image using DALL-E."""
    user_id = update.message.from_user.id

    if is_allowed_user(user_id):
        prompt = update.message.text
        try:
            image_url = generate_image(prompt)
            update.message.reply_photo(photo=image_url)
        except Exception as e:
            update.message.reply_text(f"Error generating image: {e}")
    else:
        update.message.reply_text("Sorry, you are not allowed to use this bot.")
