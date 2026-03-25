import asyncio
import os
import discord
from dotenv import load_dotenv
from datetime import datetime
import requests
from time import sleep
import threading

load_dotenv()
PEBBLEHOST_API_KEY = os.getenv('pebblehost_api_key')
BOT_TOKEN = os.getenv('bot_token')
channel_id = int(os.getenv('channel_id'))
server_id = os.getenv('server_id')

intents = discord.Intents.default() #this is what the bot intends to do
#intents.guild_messages = True # I don't know what intents we need to send messages. It may be none.
client = discord.Client(intents=intents) # this is the object that interacts with discord api

# Dictionary that contains all users we know of. Every 5 seconds, check the players endpoint from pebblehost. Go through each user. If they exist in online_status.keys(), then update the value to reflect offline or online. If a known user's status changes, send a notification to the channel. If they don't exist as a key, add them as a key and update their status. Send a notification to the channel if they're online (they should be).
online_status = {}

COMMAND_URL = f'https://panel.pebblehost.com/api/client/servers/{server_id}/command'
LOGS_URL = f'https://panel.pebblehost.com/api/client/servers/{server_id}/files/contents?file=logs%2Flatest.log'
auth_header = {'Authorization': f'Bearer {PEBBLEHOST_API_KEY}'}
accept_header = {'-H': 'accept: application/json'}
async def check_status(): 
    '''
    Queries the pebblehost players API endpoint to check the status of all players on the server. If 
    '''
    if True:
        requests.post(COMMAND_URL, headers=auth_header, json={"command": "list"})

        log_file = requests.get(LOGS_URL, headers=auth_header | accept_header)
        logs = log_file.text.split('\n')
        # logs[-2] will be the latest log. log[-1] is always \n.
        #print(logs[-2])
        if '[Server thread/INFO]: There are' in logs[-2]:
            words = logs[-2].split(' ') # we are going to filter out everything until we're left with a list of players
            indexes_to_delete = []
            for index in range(13):
                del words[0] # Delete the first 11 words from words
            players = words # this is a list of players by username
            players = [x.replace(',', '') for x in players]
            print(f'Playerlist: {players}')
            if players == ['']:
                for player in online_status.keys():
                    if online_status[player] == True: # Was the player previously online?
                        # The player just went offline
                        await send_offline(player)
                    online_status[player] = False
            else: #if there are more than 0 players online
                for online_player in players:
                    if online_player in online_status.keys(): #if we already know about this player
                        if online_status[online_player] == False: #player just got online
                            await send_online(online_player)
                        online_status[online_player] = True
                    else: #if we don't know about this player
                        await send_online(online_player)
                        online_status[online_player] = True

        else:
            raise Exception('The latest log was not list.')
        

async def send_offline(player_name: str):
    # send a discord message saying this player went offline
    channel = client.get_channel(channel_id)
    await channel.send(f'{player_name} went offline.')

async def send_online(player_name: str):
    # send a discord message saying this player came online
    channel = client.get_channel(channel_id)
    await channel.send(f'{player_name} came online.')


@client.event
async def on_ready():
    print(f'{client.user} has connect to discord!')
    while True:
        await check_status()
        await asyncio.sleep(5)
    #channel = client.get_channel(channel_id)
    #await channel.send('Testing...')

if __name__ == '__main__':
    client.run(BOT_TOKEN)
