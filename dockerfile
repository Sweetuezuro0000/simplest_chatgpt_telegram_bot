FROM python:3.7-slim-buster

# Install build tools
RUN apt-get update && apt-get install -y build-essential

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt and install the required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container at /app
COPY . .

# Expose port 8443 for Telegram API
EXPOSE 8443

# Start the bot
CMD ["python", "bot.py"]
