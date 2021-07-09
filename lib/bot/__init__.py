'''
AURegistrationBot - Written by Patrick Coyle

Bot to assist with registration for side events and for reporting results for the
main event of the Konami Remote Duel YCS, an online yugioh tournament played over
webcam, faciilated by Discord.

This was written specifically for this tournament and as is only functions on
the Alternate Universes RDYCS discord server it was written for. To use it
on your own server, you will need to update any of the guild and user IDs for
for your own server and users. I have labeled anything that needs to be changed
to do this.

List of commands can be found at:
https://github.com/patrickcoyle427/AU-Registration-Bot/blob/main/README.md
'''

from discord import Intents, Embed, File, DMChannel, Client
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, CommandOnCooldown
from discord.ext.commands import Context

from glob import glob
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..db import db

import asyncio

PREFIX = '!'
OWNER_IDS = [450433098811703317]
COGS = ['reg']
# Finds and returns the name of all the cogs in the cog folder

class Ready(object):

    # gets cog commands ready to be used

    def __init__(self):

        for cog in COGS:

            setattr(self, cog, False)

    def ready_up(self, cog):

        setattr(self, cog, True)
        print(f'{cog} cog ready')

    def all_ready(self):

        return all ([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    
    def __init__(self):

        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        # Guild ID, this is set in on_ready
        self.scheduler = AsyncIOScheduler()

        self.me_scorekeeper = None
        # User ID of the main event scorekeeper, used for receiving main event results.
        # This is set in on_ready
        
        self.pe_scorekeeper = None
        # User ID of the side event scorekeeper so they know when an event can start.
        # Tuple so you can have multiple public event scorekeepers
        # this is set in on_ready()

        self.giantcard_active = False
        # if set to true, announcements for attack of the giant card will be active and registration can be taken

        self.obeliskdeck_active = False
        self.sliferdeck_active = False
        self.speedduel_active = False
        self.winamat_active = False

        self.announcement_timer = 420
        # Edit this to change registration annoucement frequency, time is in seconds

        self.event_category = None
        # Edit this to change where tournament text channels are created, set in on_ready()
    
        self.target_channels = (859851969664778270,
                                859852025869369364,
                                859852221340844092,
                                859852277195603988,
                                859852092738109470)
        # IDs of the channels the bot will be active in
        
        self.giantcard = self.target_channels[0]
        self.obeliskdeck = self.target_channels[1]
        self.sliferdeck = self.target_channels[2]
        self.speedduel = self.target_channels[3]
        self.winamat = self.target_channels[4]
        # I set channel IDs from the target channel list to variables for cleaner code

        self.reg_from = {}
        # dict to hold the user ID of a player, and the channel that the registered from so
        # the bot knows what registration form to send them

        self.reports = {}
        # dict to hold the user ID and result of a player for a round. If they have a report already it won't let them report again.
        # Use the !clearreports command to clear all previous round reports.

        self.me_round_count = 1
        # Counts the round number, updated when !clearreports is used
        
        self.obelisk_deck_event_id = 1
        self.slifer_deck_event_id = 1
        self.speed_duel_event_id = 1
        self.win_a_mat_event_id = 1
        # increments the ID numbers for creating channels and assigning roles

        db.autosave(self.scheduler)
        
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, help_command=None, intents=Intents.all())
        
    def setup(self):

        for cog in COGS:

            self.load_extension(f'lib.cogs.{cog}')
            print(f' {cog} cog loaded')

        print('setup complete')

    def run(self, VERSION):
        
        self.VERSION = VERSION

        print('running setup...')
        self.setup()

        with open('./lib/bot/token.0', 'r', encoding='utf-8') as tf:
            
            self.TOKEN = tf.read()

            print('Bot has launched!')
            
            super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send('Not ready for commands yet! Please wait a few seconds!')
        
    async def on_connect(self):
        
        print('Bot connected to discord!')

    async def on_disconnect(self):
        
        print('Bot disconnected')

    async def on_error(self, err, *args, **kwargs):
        
        if err == 'on_command_error':

            await args[0].send('Something went wrong.')

        await args[0].send('An error occured')

        raise

    async def on_command_error(self, ctx, exc):
        
        if isinstance(exc, CommandNotFound):

            pass

        if isinstance(exc, CommandOnCooldown):

            await ctx.reply(f'That command is on cooldown. Try again in {exc.retry_after:,.2f} seconds.')

        elif hasattr(exec, 'original'):

            raise exc.original

        else:

            raise exc

    async def on_ready(self):
        
        if not self.ready:

            while not self.cogs_ready.all_ready():
                await asyncio.sleep(0.5)

            self.guild = bot.get_guild(853704416325533716)
            # Set the server ID here

            self.me_scorekeeper = self.guild.get_member(450433098811703317)
            # Set main event scorekeeper's User ID here.

            self.pe_scorekeeper = (self.guild.get_member(505180557165068298),
                                   self.guild.get_member(171871625052946433))
            # Set public events scorekeeper's User ID here.

            self.event_category = self.get_channel(853704417329152004)
            # Edit to change the category where public events channels are created.

            self.ready = True

            print('Bot ready!')

            self.loop.create_task(self.tournament_announcement())

        else:
            print('Bot reconnected!')

    async def on_message(self, message):
        
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):

                ctx = await self.get_context(message, cls=Context)
                
                if message.content == '!done':

                    await self.add_to_event_table(ctx.message.author.id)

                else:
                    await message.channel.send('Sorry, I do not recognize that command!')

            else:
                await self.process_commands(message)

    async def tournament_announcement(self):
    
    # Sends a message any specified channel on how to register for a tournament.

        event_text = {
            self.giantcard: 'Attack of the Giant Card',
            self.obeliskdeck: 'Obelisk Strucutre Deck',
            self.sliferdeck: 'Slifer Structure Deck',
            self.speedduel: 'Speed Duel',
            self.winamat: 'Win a Mat'
            }
        
        await self.wait_until_ready()

        while not bot.is_closed():

            for channel_id in self.target_channels:

                channel = self.get_channel(id=channel_id)

                if self.giantcard_active == True and channel_id == self.giantcard:
                # Skips annoucing the how to register if the event has already started

                    message = f'If you would like to register for the {event_text[channel_id]} side event, type **!register** and I will DM you with the details on how to do so!'
                    await channel.send(message)

                if self.obeliskdeck_active == True and channel_id == self.obeliskdeck:

                    message = f'If you would like to register for the {event_text[channel_id]} side event, type **!register** and I will DM you with the details on how to do so!'
                    await channel.send(message)

                if self.sliferdeck_active == True and channel_id == self.sliferdeck:

                    message = f'If you would like to register for the {event_text[channel_id]} side event, type **!register** and I will DM you with the details on how to do so!'
                    await channel.send(message)

                if self.speedduel_active == True and channel_id == self.speedduel:

                    message = f'If you would like to register for the {event_text[channel_id]} side event, type **!register** and I will DM you with the details on how to do so!'
                    await channel.send(message)

                if self.winamat_active == True and channel_id == self.winamat:

                    message = f'If you would like to register for the {event_text[channel_id]} side event, type **!register** and I will DM you with the details on how to do so!'
                    await channel.send(message)

            await asyncio.sleep(self.announcement_timer)
            # Loop waits x seconds before sending the message again

    async def add_to_event_table(self, user_id):

        player_event = self.reg_from.get(user_id)
        user_to_dm = self.guild.get_member(user_id)

        reg_success = False
        # True if registration completed successfully

        dm_to_send = ''
        # Will have player ID's added to it to be DM'd to the scorekeeper

        event_can_start = False
        # True if event has enough players to start

        event_name = ''
        # Hold the name of an event that can start

        if player_event == self.giantcard:

            reg_success = True

            db.execute('REPLACE INTO giantcard(UserID,EventNumber) VALUES(?,?)', user_id, 0)
            db.commit()

        elif player_event == self.obeliskdeck:

            reg_success = True

            db.execute('REPLACE INTO obeliskdeck(UserID,EventNumber) VALUES(?,?)', user_id, self.obelisk_deck_event_id)
            db.commit()

            count = db.records("SELECT COUNT (*) FROM obeliskdeck")

            if count[0][0] == 8:

                # 8 is how many players are needed to start an event

                players = db.records('SELECT * FROM obeliskdeck LIMIT 8')

                event_players = [i[0] for i in players]

                event_role = f'ObeliskStructure{self.obelisk_deck_event_id}'

                channel_name = f'Obelisk Structure Event {self.obelisk_deck_event_id}'

                role = await self.guild.create_role(name=event_role, mentionable=True)

                self.obelisk_deck_event_id += 1

                event_can_start = True

                event_name = 'Obelisk Structure Deck'

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.reg_from[player] = ''
                    # removes the player record from the dict so the player can eneter another event later.

                    db.execute('DELETE FROM obeliskdeck where UserID = ?', player)

                channel = await self.guild.create_text_channel(channel_name, category=self.event_category, position=0)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

                db.commit()

            elif count[0][0] == 4:

                # You are able to play an event with 4, so there is an option to start with that number if it is an
                # event with low attendance.

                for sk in self.pe_scorekeeper:

                    await self.sk.send('You have 4 players for an obelisk structure event. If you would like to start this event now, go to the obelisk structure deck event registration channel and type **!obeliskgo**')
                    await self.sk.send('If you are wating for 8 players, no action is needed')

        elif player_event == self.sliferdeck:

            reg_success = True

            db.execute('REPLACE INTO sliferdeck(UserID,EventNumber) VALUES(?,?)', user_id, self.slifer_deck_event_id)
            db.commit()

            count = db.records("SELECT COUNT (*) FROM sliferdeck")

            if count[0][0] == 8:

                players = db.records('SELECT * FROM sliferdeck LIMIT 8')

                event_players = [i[0] for i in players]

                event_role = f'SliferStructure{self.slifer_deck_event_id}'

                channel_name = f'Slifer Structure Event {self.slifer_deck_event_id}'

                role = await self.guild.create_role(name=event_role, mentionable=True)

                self.slifer_deck_event_id += 1

                event_can_start = True

                event_name = 'Slifer Structure Deck'

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.reg_from[player] = ''

                    db.execute('DELETE FROM sliferdeck where UserID = ?', player)

                channel = await self.guild.create_text_channel(channel_name, category=self.event_category, position=0)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

                db.commit()

            elif count[0][0] == 4:

                for sk in self.pe_scorekeeper:

                    await self.sk.send('You have 4 players for a slifer structure event. If you would like to start this event now, go to the slifer structure deck event registration channel and type **!slifergo**')
                    await self.sk.send('If you are wating for 8 players, no action is needed')


        elif player_event == self.speedduel:

            reg_success = True

            db.execute('REPLACE INTO speedduel(UserID,EventNumber) VALUES(?,?)', user_id, self.speed_duel_event_id)
            db.commit()

            count = db.records("SELECT COUNT (*) FROM speedduel")

            if count[0][0] == 8:

                players = db.records('SELECT * FROM speedduel LIMIT 8')

                event_players = [i[0] for i in players]

                event_role = f'SpeedDuel{self.speed_duel_event_id}'

                channel_name = f'Speed Duel Event {self.speed_duel_event_id}'

                role = await self.guild.create_role(name=event_role, mentionable=True)

                self.speed_duel_event_id += 1

                event_can_start = True

                event_name = 'Speed Duel'

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.reg_from[player] = ''

                    db.execute('DELETE FROM speedduel where UserID = ?', player)

                channel = await self.guild.create_text_channel(channel_name, category=self.event_category, position=0)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

                db.commit()

            elif count[0][0] == 4:

                for sk in self.pe_scorekeeper:

                    await self.sk.send('You have 4 players for a speed duel event. If you would like to start this event now, go to the speed duel event registration channel and type **!speedduelgo**')
                    await self.sk.send('If you are wating for 8 players, no action is needed')


        elif player_event == self.winamat:

            reg_success = True

            db.execute('REPLACE INTO winamat(UserID,EventNumber) VALUES(?,?)', user_id, self.win_a_mat_event_id)
            db.commit()

            count = db.records("SELECT COUNT (*) FROM winamat")

            if count[0][0] == 8:

                players = db.records('SELECT * FROM winamat LIMIT 8')

                event_players = [i[0] for i in players]

                event_role = f'WinAMat{self.win_a_mat_event_id}'

                channel_name = f'Win A Mat Event {self.win_a_mat_event_id}'

                role = await self.guild.create_role(name=event_role, mentionable=True)

                self.win_a_mat_event_id += 1

                event_can_start = True

                event_name = 'Win a Mat'

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.reg_from[player] = ''

                    db.execute('DELETE FROM winamat where UserID = ?', player)

                channel = await self.guild.create_text_channel(channel_name, category=self.event_category, position=0)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

            elif count[0][0] == 4:

                for sk in self.pe_scorekeeper:

                    await self.sk.send('You have 4 players for a win a mat event. If you would like to start this event now, go to the win a mat event registration channel and type **!winamatgo**')
                    await self.sk.send('If you are wating for 8 players, no action is needed')

                db.commit()

        else:
            
            await user_to_dm.send('You have not started the registration process yet! Please go to the channel for the event you wish to play in and type **!register**!')

        if reg_success:

            await user_to_dm.send(f'Your registration is complete! Please look for a notification about the start of round 1!')

        if event_can_start:

            for sk in self.pe_scorekeeper:

                await self.sk.send(f'You have enough players to start a {event_name} event. The role for the event is @{event_role}')
                await self.sk.send('Here is the list of players. Please check to make sure they all have paid')
                await self.sk.send(dm_to_send)

bot = Bot()
