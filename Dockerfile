# 1. Use an official lightweight Python image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file first to leverage Docker's caching
COPY requirements.txt .

# 4. Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your bot files into the container
COPY . .

# 6. Expose the port (Back4app overrides this dynamically via the PORT environment variable)
EXPOSE 8080

# 7. The command to run your Python bot script
CMD ["python", "aternos_server_bot.py"]
