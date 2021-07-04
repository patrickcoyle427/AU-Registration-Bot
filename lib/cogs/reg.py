from random import choice, randint

from discord import Member
from discord.ext.commands import Cog
from discord.ext.commands import command

from datetime import datetime, timezone

from ..db import db

class Reg(Cog):

    def __init__(self, bot):

        self.bot = bot
        self.authorized_users = (450433098811703317, 505180557165068298)

    @command(name='register', aliases=['reg'])
    async def register(self, ctx):

        message_info = {
            self.bot.giantcard: ('Attack of the Giant Card', 'https://forms.gle/vT7vJath35k1Zvmn8'),
            self.bot.obeliskdeck: ('the Obelisk Structure Deck Event', 'https://forms.gle/KbhRL7oSd4JaP1jw7'),
            self.bot.sliferdeck: ('the Slifer Structure Deck Event', 'https://forms.gle/xrqMuLBNfawhJ2Xp8'),
            self.bot.speedduel: ('the Speed Duel Event', 'https://forms.gle/xoc4zYjLWCzk3T7X7'),
            self.bot.winamat: ('the Win a Mat Event', 'https://forms.gle/mjfFYDXA7G3qDvNu7')
            }

        from_channel = ctx.message.channel.id

        if from_channel in self.bot.target_channels:

            if from_channel == self.bot.giantcard and self.bot.giant_card_active == False:
            # Only lets people register for Attack of the Giant Card when the user makes registration active.

                await ctx.message.author.send('Sorry this event has already started!')

            else:

                await ctx.message.author.send(f'Here is the link to register for {message_info[from_channel][0]}!: {message_info[from_channel][1]}')
                await ctx.message.author.send('Once you have filled out that form, type **!done** to confirm your registration. If you do not your enrollment will not be complete.')
            
                self.bot.reg_from[ctx.message.author.id] = ctx.message.channel.id
                # Stores the channel ID from where the user called the !register command
                # When the user tells the bot !done to finish registration, it will use this info
                # to add the player to the appropriate table for the event!


    @command(name='giantcardgo')
    async def run_giant_card(self, ctx):

        # Gets the names of players that registered for the giant card event and sends them to the scorekeeper.
        # The Giant card event starts at a set time, not when there are a certain number of registered players.

        if ctx.message.author.id in self.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM giantcard')

            if counted[0][0] == 0:

               await self.bot.scorekeeper.send('There are 0 players registered for the Giant Card event. Event can not be started.')

            else:

                if self.bot.giant_card_active:

                    event_role = 'AttackOfTheGiantCard'

                    role = await self.bot.guild.create_role(name=event_role, mentionable=True)

                    channel_name = 'Attack of the Giant Card Event'

                    dm_to_send = ''

                    self.bot.giant_card_active = False

                    players = db.records('SELECT * FROM giantcard')

                    event_players = [i[0] for i in players] 

                    for player in event_players:

                        dm_to_send += f'<@{player}>\n'

                        to_give_role = self.bot.guild.get_member(player)

                        await to_give_role.add_roles(role)

                        self.bot.reg_from[player] = ''

                        db.execute('DELETE FROM giantcard where UserID = ?', player)

                    db.commit()

                    await self.bot.scorekeeper.send(f'Here is the list of players for Attack of the Giant Card. The role for the event is @{event_role} Please check to make sure they all have paid.')
                    await self.bot.scorekeeper.send(dm_to_send)

                    channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                    await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

                else:

                    await self.bot.scorekeeper.send('Cannot start the event because it is not active!')

    @command(name='giantcardopen')
    async def giant_card_open(self, ctx):

        if ctx.message.author.id in self.authorized_users:

            if self.bot.giant_card_active == False:

                self.bot.giant_card_active = True

                await ctx.reply('Giant card registration is now open!')

            else:

                await ctx.message.send('Giant card event registration is already open!')


    @command(name='obeliskgo')
    async def obelisk_start(self, ctx):

        if ctx.message.author.id in self.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM obeliskdeck')

            if counted[0][0] == 0:

               await self.bot.scorekeeper.send('There are 0 players registered for the Obelisk Structure Deck event. Event can not be started.')

            else:

                event_role = f'ObeliskStructure{self.bot.obelisk_deck_event_id}'

                role = await self.bot.guild.create_role(name=event_role, mentionable=True)

                channel_name = f'Obelisk Structure Event {self.bot.obelisk_deck_event_id}'

                self.bot.obelisk_deck_event_id += 1

                dm_to_send = ''

                players = db.records('SELECT * FROM obeliskdeck')

                event_players = [i[0] for i in players]

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.bot.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.bot.reg_from[player] = ''

                    db.execute('DELETE FROM obeliskdeck where UserID = ?', player)

                db.commit()

                await self.bot.scorekeeper.send(f'Here is the list of players for the Obelisk Strucutre Deck Event. The role for the event is @{event_role} Please check to make sure they all have paid.')
                await self.bot.scorekeeper.send(dm_to_send)

                channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

    @command(name='slifergo')
    async def slifer_start(self, ctx):

        if ctx.message.author.id in self.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM sliferdeck')

            if counted[0][0] == 0:

               await self.bot.scorekeeper.send('There are 0 players registered for the Slifer Structure Deck event. Event can not be started.')

            else:

                event_role = f'SliferStructure{self.bot.slifer_deck_event_id}'

                role = await self.bot.guild.create_role(name=event_role, mentionable=True)

                channel_name = f'Slifer Structure Event {self.bot.slifer_deck_event_id}'

                self.bot.slifer_deck_event_id += 1

                dm_to_send = ''

                players = db.records('SELECT * FROM sliferdeck')

                event_players = [i[0] for i in players]

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.bot.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.bot.reg_from[player] = ''

                    db.execute('DELETE FROM sliferdeck where UserID = ?', player)

                db.commit()

                await self.bot.scorekeeper.send(f'Here is the list of players for the Slifer Strucutre Deck Event. The role for the event is @{event_role}. Please check to make sure they all have paid.')
                await self.bot.scorekeeper.send(dm_to_send)

                channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

    @command(name='speedduelgo')
    async def speed_duel_start(self, ctx):

        if ctx.message.author.id in self.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM speedduel')

            if counted[0][0] == 0:

               await self.bot.scorekeeper.send('There are 0 players registered for the Speed Duel event. Event can not be started.')

            else:

                event_role = f'SpeedDuel{self.bot.speed_duel_event_id}'

                role = await self.bot.guild.create_role(name=event_role, mentionable=True)

                channel_name = f'Speed Duel Event {self.bot.speed_duel_event_id}'

                self.bot.speed_duel_event_id += 1

                dm_to_send = ''

                players = db.records('SELECT * FROM speedduel')

                event_players = [i[0] for i in players]

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.bot.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.bot.reg_from[player] = ''

                    db.execute('DELETE FROM speedduel where UserID = ?', player)

                db.commit()

                await self.bot.scorekeeper.send(f'Here is the list of players for the Speed Duel Event. The role for the event is @{event_role}. Please check to make sure they all have paid.')
                await self.bot.scorekeeper.send(dm_to_send)

                channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

    @command(name='winamatgo')
    async def win_a_mat_start(self, ctx):

        if ctx.message.author.id in self.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM winamat')

            if counted[0][0] == 0:

                await self.bot.scorekeeper.send('There are 0 players registered for the Win A Mat event. Event can not be started.')

            else:

                event_role = f'WinAMat{self.bot.win_a_mat_event_id}'

                role = await self.bot.guild.create_role(name=event_role, mentionable=True)

                channel_name = f'Win a Mat Event {self.bot.win_a_mat_event_id}'

                self.bot.win_a_mat_event_id += 1

                dm_to_send = ''

                players = db.records('SELECT * FROM winamat')

                event_players = [i[0] for i in players]

                for player in event_players:

                    dm_to_send += f'<@{player}>\n'

                    to_give_role = self.bot.guild.get_member(player)

                    await to_give_role.add_roles(role)

                    self.bot.reg_from[player] = ''

                    db.execute('DELETE FROM winamat where UserID = ?', player)

                db.commit()

                await self.bot.scorekeeper.send(f'Here is the list of players for the Win A Mat Event. The role for the event is @{event_role} Please check to make sure they all have paid.')
                await self.bot.scorekeeper.send(dm_to_send)

                channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

    @command(name='count')
    async def reg_num(self, ctx, event_type=''):

        possible_counts = ('giantcard', 'obeliskdeck', 'sliferdeck', 'speedduel', 'winamat')

        if event_type in possible_counts:

            counted = db.records(f'SELECT COUNT (*) FROM {event_type}')

            count = counted[0][0]

            if count == 1:

                await ctx.send('There is 1 player registered for that event')

            else:

                await ctx.send(f'There are {count} players registered for that event')

        else:

            await ctx.send('Tournament type not recognized. Please type one of the following to get the count:\ngiantcard\nobeliksdeck\nsliferdeck\nspeedduel\nwinamat\n')

    @Cog.listener()
    async def on_ready(self):

        if not self.bot.ready:

            self.bot.cogs_ready.ready_up('reg')


def setup(bot):

    bot.add_cog(Reg(bot))
