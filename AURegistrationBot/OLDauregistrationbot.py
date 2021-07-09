#!/usr/bin/env python3

'''
AURegistrationBot.py

Messages users information on how to register for a tournament. Used in our Remote Duel YCS,
an online Yugioh tournament played over webcam, run for Konami.

-Written by Patrick Coyle
'''

import os, asyncio, discord
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime, timezone

'''
os - reads .env for discord token
asyncio - used for the timer for making auto registration annoucements
discord - platform that the bot runs on, includes all commands to make the bot actually work
dotenv import load_dotenv - Loads the .env
discord.ext import commands - imports bot commands
datetime import datetime, timezone - Used for setting event start times and making sure the bot
                                     doesn't advertise events that have already begun.
'''

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Load's discord token from .env file

bot = commands.Bot(command_prefix='!', case_insensitive=True)
# Calls the bot class

global target_channels
# Global allows all functions to use this list of channels if needed

target_channels = (855907986060083220, 856229554585337916)
# Specifies all channels that the bot will be active in
# the number is the ID of the target channel

global giant_card_start
giant_card_start = datetime(2021, 6, 20, 13, 30, tzinfo=timezone.utc)
# Sets a start time for the attack of the giant card event

async def tournament_announcement():
    # Sends a message any specified channel on how to register for a tournament.

    giant_card_channel = target_channels[1]
    current_time = datetime.now(timezone.utc)

    every_x_seconds = 180
    # Edit this to change annoucement frequency

    await bot.wait_until_ready()

    while not bot.is_closed():

        for channel_id in target_channels:

            channel = bot.get_channel(id=channel_id)

            if channel_id == giant_card_channel and current_time > giant_card_start:
                # Skips annoucing the how to register if the event has already started

                pass

            else:

                await channel.send('If you would like to register for an event, type **!register** and this bot '
                                'will DM you with the details on how to get started!')
                
        await asyncio.sleep(every_x_seconds)
        # Loop waits x seconds before sending the message again

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    bot.loop.create_task(tournament_announcement())
    # Sets up the tournament annoucement loop when bot connects

@bot.command()
async def register(ctx):

    giant_card_channel = target_channels[1]

    current_time = datetime.now(timezone.utc)
    #gets the current time when 

    if ctx.message.channel.id in target_channels:
        # Only sends message if user's bot command call is in the tuple of target channels.

        if ctx.message.channel.id == giant_card_channel and current_time > giant_card_start:
            # Only sends reg info if event hasn't started yet

            await ctx.message.author.send('Sorry this event has already started!')

        else:

            await ctx.message.author.send('Hey: https://www.google.com')

bot.run(TOKEN)
