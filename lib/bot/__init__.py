from discord import Intents, File, DMChannel, Client
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, CommandOnCooldown
from discord.ext.commands import Context

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..db import db

import asyncio

PREFIX = '!'
OWNER_IDS = [450433098811703317]
COGS = ['sideevents', 'mainevent']
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
        self.scheduler = AsyncIOScheduler()

        self.guild = None
        # Guild ID, this is set in on_ready

        self.me_scorekeeper = None
        # User ID of the main event scorekeeper, used for receiving main event results.
        # This is set in on_ready
        
        self.pe_scorekeeper = None
        # User ID of the side event scorekeeper so they know when an event can start.
        # Tuple so you can have multiple public event scorekeepers
        # this is set in on_ready()

        self.authorized_users = (450433098811703317,
                                 505180557165068298,
                                 171871625052946433)
        # User IDs of anyone who has access to tournament administration commands in the SideEvents and MainEvent cogs
        # Add discord User IDs here to grant access
        # Only certain commands can be used by those who are not part of this list

        self.mainevent_active = False
        self.giantcard_active = False
        self.obeliskdeck_active = False
        self.sliferdeck_active = False
        self.speedduel_active = False
        self.winamat_active = False
        # if any of these are set to true, players will be able to register for events and
        # public event annoucmenets will be made.
        # Set to False by default, can be set to true by using !open <event> or !openall
        # The main event is only opened with the !openmain command.

        self.announcement_timer = 900
        # Edit this to change registration annoucement frequency, time is in seconds

        self.event_category = None
        # Holds the category ID of where tournament text channels are created,
        # This is set in on_ready()

        self.events = ('giantcard', 'obeliskdeck', 'sliferdeck', 'speedduel', 'winamat')
        # Tuple of public events that can be run, if you add any to this, make sure to add a target channel for that event as wellS

        self.giantcard = 844072472797380611
        self.obeliskdeck = 844072472797380611
        self.sliferdeck = 844072472797380611
        self.speedduel = 866883765032189972
        self.winamat = 844072472797380611
        # Set the channel IDs for the different side event types
    
        self.target_channels = (self.giantcard,
                                self.obeliskdeck,
                                self.sliferdeck,
                                self.speedduel,
                                self.winamat)
        # tuple of the channels for checking in if statements

        self.reg_from = {}
        # dict to hold the user ID of a player, and the channel that the registered from so
        # the bot knows what registration form to send them

        self.reports = {}
        # dict to hold the user ID and result of a player for a round. If they have a report already it won't let them report again.
        # Use the !clearreports command to clear all previous round reports.

        self.me_round_count = 1
        # Counts the round number, updated when !clearreports is used
        
        self.obeliskdeck_event_id = 1
        self.sliferdeck_event_id = 1
        self.speedduel_event_id = 1
        self.winamat_event_id = 1
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

            self.guild = bot.get_guild(844072472797380608)
            # Set the server ID here

            self.me_scorekeeper = self.guild.get_member(450433098811703317)
            # Set main event scorekeeper's User ID here.

            self.pe_scorekeeper = (self.guild.get_member(450433098811703317),)
            # Set public events (AKA Side Events) scorekeepers' User ID here.
            # Tuple is used in case there are multiple public events scorekeepers

            self.event_category = self.get_channel(844072472797380609)
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
            self.obeliskdeck: 'Obelisk God Deck',
            self.sliferdeck: 'Slifer God Deck',
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

            db.execute('REPLACE INTO obeliskdeck(UserID,EventNumber) VALUES(?,?)', user_id, self.obeliskdeck_event_id)
            db.commit()

            count = db.records("SELECT COUNT (*) FROM obeliskdeck")

            if count[0][0] == 8:

                # 8 is how many players are needed to start an event

                players = db.records('SELECT * FROM obeliskdeck LIMIT 8')

                event_players = [i[0] for i in players]

                event_role = f'ObeliskGodDeck{self.obeliskdeck_event_id}'

                channel_name = f'Obelisk God Deck Event {self.obeliskdeck_event_id}'

                role = await self.guild.create_role(name=event_role, mentionable=True)

                self.obeliskdeck_event_id += 1

                event_can_start = True

                event_name = 'Obelisk God Deck Deck'

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.reg_from[player] = ''
                    # removes the player record from the dict so the player can eneter another event later.

                    db.execute('DELETE FROM obeliskdeck where UserID = ?', player)

                channel = await self.guild.create_text_channel(channel_name, category=self.event_category, position=0)
                await channel.set_permissions(role, read_messages=True, send_messages=True)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

                db.commit()

            elif count[0][0] == 4:

                # You are able to play an event with 4, so there is an option to start with that number if it is an
                # event with low attendance.

                for sk in self.pe_scorekeeper:

                    await sk.send('You have 4 players for an obelisk structure event. If you would like to start this event now, go to the obelisk structure deck event registration channel and type **!obeliskgo**')
                    await sk.send('If you are wating for 8 players, no action is needed')

        elif player_event == self.sliferdeck:

            reg_success = True

            db.execute('REPLACE INTO sliferdeck(UserID,EventNumber) VALUES(?,?)', user_id, self.sliferdeck_event_id)
            db.commit()

            count = db.records("SELECT COUNT (*) FROM sliferdeck")

            if count[0][0] == 8:

                players = db.records('SELECT * FROM sliferdeck LIMIT 8')

                event_players = [i[0] for i in players]

                event_role = f'SliferGodDeck{self.sliferdeck_event_id}'

                channel_name = f'Slifer God Deck Event {self.sliferdeck_event_id}'

                role = await self.guild.create_role(name=event_role, mentionable=True)

                self.sliferdeck_event_id += 1

                event_can_start = True

                event_name = 'Slifer God Deck Deck'

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.reg_from[player] = ''

                    db.execute('DELETE FROM sliferdeck where UserID = ?', player)

                channel = await self.guild.create_text_channel(channel_name, category=self.event_category, position=0)
                await channel.set_permissions(role, read_messages=True, send_messages=True)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

                db.commit()

            elif count[0][0] == 4:

                for sk in self.pe_scorekeeper:

                    await sk.send('You have 4 players for a slifer structure event. If you would like to start this event now, go to the slifer structure deck event registration channel and type **!slifergo**')
                    await sk.send('If you are wating for 8 players, no action is needed')


        elif player_event == self.speedduel:

            reg_success = True

            db.execute('REPLACE INTO speedduel(UserID,EventNumber) VALUES(?,?)', user_id, self.speedduel_event_id)
            db.commit()

            count = db.records("SELECT COUNT (*) FROM speedduel")

            if count[0][0] == 8:

                players = db.records('SELECT * FROM speedduel LIMIT 8')

                event_players = [i[0] for i in players]

                event_role = f'SpeedDuel{self.speed_duelevent_id}'

                channel_name = f'Speed Duel Event {self.speedduel_event_id}'

                role = await self.guild.create_role(name=event_role, mentionable=True)

                self.speedduel_event_id += 1

                event_can_start = True

                event_name = 'Speed Duel'

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.reg_from[player] = ''

                    db.execute('DELETE FROM speedduel where UserID = ?', player)

                channel = await self.guild.create_text_channel(channel_name, category=self.event_category, position=0)
                await channel.set_permissions(role, read_messages=True, send_messages=True)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

                db.commit()

            elif count[0][0] == 4:

                for sk in self.pe_scorekeeper:

                    await sk.send('You have 4 players for a speed duel event. If you would like to start this event now, go to the speed duel event registration channel and type **!speedduelgo**')
                    await sk.send('If you are wating for 8 players, no action is needed')


        elif player_event == self.winamat:

            reg_success = True

            db.execute('REPLACE INTO winamat(UserID,EventNumber) VALUES(?,?)', user_id, self.winamat_event_id)
            db.commit()

            count = db.records("SELECT COUNT (*) FROM winamat")

            if count[0][0] == 8:

                players = db.records('SELECT * FROM winamat LIMIT 8')

                event_players = [i[0] for i in players]

                event_role = f'WinAMat{self.winamat_event_id}'

                channel_name = f'Win A Mat Event {self.winamat_event_id}'

                role = await self.guild.create_role(name=event_role, mentionable=True)

                self.winamat_event_id += 1

                event_can_start = True

                event_name = 'Win a Mat'

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.reg_from[player] = ''

                    db.execute('DELETE FROM winamat where UserID = ?', player)

                channel = await self.guild.create_text_channel(channel_name, category=self.event_category, position=0)
                await channel.set_permissions(role, read_messages=True, send_messages=True)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

            elif count[0][0] == 4:

                for sk in self.pe_scorekeeper:

                    await sk.send('You have 4 players for a win a mat event. If you would like to start this event now, go to the win a mat event registration channel and type **!winamatgo**')
                    await sk.send('If you are wating for 8 players, no action is needed')

                db.commit()

        else:
            
            await user_to_dm.send('You have not started the registration process yet! Please go to the channel for the event you wish to play in and type **!register**!')

        if reg_success:

            await user_to_dm.send(f'Your registration is complete! Please look for a notification about the start of round 1!')

        if event_can_start:

            for sk in self.pe_scorekeeper:

                await sk.send(f'You have enough players to start a {event_name} event. The role for the event is @{event_role}')
                await sk.send('Here is the list of players. Please check to make sure they all have paid')
                await sk.send(dm_to_send)

bot = Bot()
