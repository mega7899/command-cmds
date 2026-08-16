import discord
import os
import time
from python_aternos import Client
from mcstatus import JavaServer

# --- NEW IMPORTS FOR THE BACKGROUND SERVER ---
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. THE WEB SERVER (Answers Back4app's health checks)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"I am alive!")

def run_server():
    # Back4app assigns a port dynamically via the PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def keep_alive():
    # 2. THE THREAD (Runs the server in the background)
    t = Thread(target=run_server)
    t.daemon = True # Ensures the thread closes when the main bot script closes
    t.start()
# ---------------------------------------------

# Fetch credentials from environment variables safely
TOKEN = os.environ.get('DISCORD_TOKEN')
ATERNOS_USER = os.environ.get('ATERNOS_USER', 'your_username_here')
ATERNOS_PASS = os.environ.get('ATERNOS_PASS', 'your_password_here')

# Initialize Discord Client
client = discord.Client()

# 1. Initialize the Aternos client and log in
atclient = Client()
atclient.login(ATERNOS_USER, ATERNOS_PASS)

# 2. Get the account object
aternos_account = atclient.account

# 3. Fetch the servers list
servers = aternos_account.list_servers()

# 4. Get your specific server (assuming you only have 1)
myserv = servers[0]

@client.event
async def on_ready():
    print('we have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')

    if message.author == client.user:
        return

    if message.channel.name == 'bot-cmnds':
        if user_message.lower() == '?hello':
            await message.channel.send(f'Hello {username}!')
            return

        if user_message.lower() == '?server_start':
            myserv.start()
            
            # Lookup the server address and specific port
            server = JavaServer.lookup("kinezo.aternos.me:11723")
            
            while True:
                try:
                    # Attempt to fetch the server status
                    status = server.status()
                    # If the above line succeeds without an error, the server is responding!
                    break 
                except Exception:
                    # If it fails (server is still offline), wait 1 second and loop again
                    time.sleep(1)
                    
            await message.channel.send("server is now alive!!! you can join in 2-3 minutes by pasting ||kinezo.aternos.me:11723|| in the server address.")
            return

        if user_message.lower() == '?server_stop':
            myserv.stop()
            await message.channel.send('server stopped')
            return

# 3. START THE BACKGROUND SERVER BEFORE STARTING THE BOT
keep_alive()

# 4. RUN THE DISCORD BOT
client.run(TOKEN)
