FROM python:3.7-slim-buster

# Install build tools
RUN apt-get update && apt-get install -y build-essential

# Set the working directory to /app
WORKDIR /app

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose port 8443 for Telegram API
EXPOSE 8443

# Start the bot
CMD ["python", "bot.py"]
