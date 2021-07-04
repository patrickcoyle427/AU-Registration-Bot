from discord import Intents, Embed, File, DMChannel, Client
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
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
        self.scorekeeper = None
        # User ID of the side event scorekeeper so they know when an event can start, this is set in on_ready()

        self.giant_card_active = False
        # if set to true, announcements for attack of the giant card will be active and registration can be taken

        self.announcement_timer = 300
        # Edit this to change registration annoucement frequency

        self.event_category = None
        # Edit this to change where tournament text channels are created, set in on_ready()
    
        self.target_channels = (855907986060083220,
                                856229554585337916,
                                859860618188947496,
                                861317602894020618,
                                861317718190981201)
        # IDs of the channels the bot will be active in
        
        self.giantcard = self.target_channels[0]
        self.obeliskdeck = self.target_channels[1]
        self.sliferdeck = self.target_channels[2]
        self.speedduel = self.target_channels[3]
        self.winamat = self.target_channels[4]
        # I set channel IDs from the target channel list to variables for cleaner code

        #self.giant_card_start = datetime(2021, 7, 11, 13, 00, tzinfo=timezone.utc)

        db.autosave(self.scheduler)
        
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=Intents.all())

        self.reg_from = {}
        # table to hold the user ID of a player, and the channel that the registered from so
        # the bot knows what registration form to send them
        
        self.obelisk_deck_event_id = 1
        self.slifer_deck_event_id = 1
        self.speed_duel_event_id = 1
        self.win_a_mat_event_id = 1
        # increments the ID numbers for creating channels and assigning roles

        self.giant_card_role = ''
        self.obelisk_deck_roles = {}
        self.slifer_deck_roles = {}
        self.speed_duel_roles = {}
        self.win_a_mat_roles = {}
        # dicts for holding created roles. Key is event number

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

        elif hasattr(exec, 'original'):

            raise exc.original

        else:

            raise exc

    async def on_ready(self):
        
        if not self.ready:

            while not self.cogs_ready.all_ready():
                await asyncio.sleep(0.5)

            self.guild = bot.get_guild(575100789735948322)

            self.scorekeeper = self.guild.get_member(450433098811703317)

            self.event_category = self.get_channel(575100790461431815)
            # Edit to change the category where events channels are created

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

                if channel_id == self.giantcard and self.giant_card_active == False:
                # Skips annoucing the how to register if the event has already started

                    pass

                else:

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

                await self.scorekeeper.send('You have 4 players for an obelisk structure event. If you would like to start this event now, go to the obelisk structure deck event registration channel and type **!obeliskgo**')
                await self.scorekeeper.send('If you are wating for 8 players, no action is needed')

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

                await self.scorekeeper.send('You have 4 players for a slifer structure event. If you would like to start this event now, go to the slifer structure deck event registration channel and type **!slifergo**')
                await self.scorekeeper.send('If you are wating for 8 players, no action is needed')


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

                await self.scorekeeper.send('You have 4 players for a speed duel event. If you would like to start this event now, go to the speed duel event registration channel and type **!speedduelgo**')
                await self.scorekeeper.send('If you are wating for 8 players, no action is needed')


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

                db.commit()

        else:
            
            await user_to_dm.send('You have not started the registration process yet! Please go to the channel for the event you wish to play in and type **!register**!')

        if reg_success:

            await user_to_dm.send(f'Your registration is complete! Please look for a notification about the start of round 1!')

        if event_can_start:

                await self.scorekeeper.send(f'You have enough players to start a {event_name} event. The role for the event is @{event_role}')
                await self.scorekeeper.send('Here is the list of players. Please check to make sure they all have paid')
                await self.scorekeeper.send(dm_to_send)

bot = Bot()
