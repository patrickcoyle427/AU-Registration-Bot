from discord import Member
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown 
from discord.utils import get

from ..db import db

class SideEvents(Cog):

    def __init__(self, bot):

        self.bot = bot

    @command(name='add')
    async def add_player(self, ctx, member: Member, *, event_type=''):

        # Adds a player to an event table, and goes thru the steps as if that player did the process themselves.

        if ctx.message.author.id in self.bot.authorized_users:

            if event_type in self.bot.events:

                to_add = member.id

                add_into = exec(f'self.bot.{event_type}')

                self.bot.reg_from[to_add] = add_into

                self.bot.add_to_event_table(to_add)

                await ctx.reply(f'<@{to_add}> successfully added into the {event_type} event!')

            else:

                await ctx.reply('Tournament type not recognized. Please type one of the following to get the count:\ngiantcard\nobeliksdeck\nsliferdeck\nspeedduel\nwinamat\n')

    @command(name='close')
    async def close_event(self, ctx, event_type=''):

        # closes registration for a specific event

        if ctx.message.author.id in self.bot.authorized_users:

            if event_type in self.bot.events:

                exec(f'self.bot.{event_type}_active = False')

                await ctx.reply(f'{event_type} registration is now closed!')

            else:

                await ctx.reply('Tournament type not recognized. Please use one of the following to close registration:\ngiantcard\nobeliksdeck\nsliferdeck\nspeedduel\nwinamat\n')

    @command(name='closeall')
    async def close_all_events(self, ctx):

        # Closes registration for all events.

        if ctx.message.author.id in self.bot.authorized_users:

            for event in self.bot.events:

                exec(f'self.bot.{event}_active = False')

            await ctx.reply('Registration for all events has been closed!')

    @command(name='count')
    async def reg_num(self, ctx, event_type=''):

        # Tells the user how many players are registered for an event

        if event_type in self.bot.events:

            counted = db.records(f'SELECT COUNT (*) FROM {event_type}')

            count = counted[0][0]

            if count == 1:

                await ctx.reply('There is 1 player registered for that event')

            else:

                await ctx.reply(f'There are {count} players registered for that event')

        else:

            await ctx.reply('Tournament type not recognized. Please type one of the following to get the count:\ngiantcard\nobeliksdeck\nsliferdeck\nspeedduel\nwinamat\n')

    @command(name='done')
    @cooldown(1, 60, BucketType.user)
    async def done_sike(self, ctx):

        # Command to alert the player that they need to say !done to the bot in DMs, not in the chat.

        if self.bot.reg_from.get(ctx.message.author.id, False) != False:

            await ctx.reply(f'You need to say this command to AURegistrationBot in your DMs to finalize your registration for this event!')

        else:

            await ctx.reply('You have not started registration for an event! After you have finished registering, DM AURegistrationBot !done to finalize your registration!')

    @command(name='giantcardgo')
    async def run_giant_card(self, ctx):

        # Gets the names of players that registered for the giant card event and sends them to the scorekeeper.
        # The Giant card event starts at a set time, not when there are a certain number of registered players.

        if ctx.message.author.id in self.bot.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM giantcard')

            if counted[0][0] == 0:

                for sk in self.bot.pe_scorekeeper:

                    await sk.send('There are 0 players registered for the Giant Card event. Event can not be started.')

            else:

                if self.bot.giantcard_active:

                    event_role = 'AttackOfTheGiantCard'

                    role = await self.bot.guild.create_role(name=event_role, mentionable=True)

                    channel_name = 'Attack of the Giant Card Event'

                    dm_to_send = ''

                    self.bot.giantcard_active = False

                    players = db.records('SELECT * FROM giantcard')

                    event_players = [i[0] for i in players] 

                    for player in event_players:

                        dm_to_send += f'<@{player}>\n'

                        to_give_role = self.bot.guild.get_member(player)

                        await to_give_role.add_roles(role)

                        self.bot.reg_from[player] = ''

                        db.execute('DELETE FROM giantcard where UserID = ?', player)

                    db.commit()

                    for sk in self.bot.pe_scorekeeper:

                        await sk.send(f'Here is the list of players for Attack of the Giant Card. The role for the event is @{event_role} Please check to make sure they all have paid.')
                        await sk.send(dm_to_send)

                    channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                    await channel.set_permissions(role, read_messages=True, send_messages=True)
                    await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

                else:

                    for sk in self.bot.pe_scorekeeper:

                        await sk.send('Cannot start the event because it is not active!')

    @command(name='list')
    async def list_players(self, ctx, event_type=''):

        # Responds to the user with a list of all players currently registered for the specified event.

        if ctx.message.author.id in self.bot.authorized_users:

            if event_type in self.bot.events:

                to_list = db.column(f'SELECT UserID FROM {event_type}')

                to_send = ''

                for user_id in to_list:

                    to_send += f'<@{user_id}>\n'

                await ctx.reply(f'The players currently registered are:\n{to_send}')

            else:

                await ctx.reply('Tournament type not recognized. Please use one of the following:\ngiantcard\nobeliksdeck\nsliferdeck\nspeedduel\nwinamat\n')

    @command(name='obeliskdeckgo', aliases=['obeliskgo'])
    async def obelisk_start(self, ctx):

        # Starts the event with the players who are currently registered. This is so a public event scorekeeper could force a tournament to start
        # with any number of players, rather than when you have 8. !sliferdeckgo, !speedduelgo, and !winamatgo all function the same way.

        if ctx.message.author.id in self.bot.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM obeliskdeck')

            if counted[0][0] == 0:

                for sk in self.bot.pe_scorekeeper:

                    await sk.send('There are 0 players registered for the Obelisk God Deck event. Event can not be started.')

            else:

                event_role = f'ObeliskGodDeck{self.bot.obelisk_deck_event_id}'

                role = await self.bot.guild.create_role(name=event_role, mentionable=True)

                channel_name = f'Obelisk God Deck Event {self.bot.obelisk_deck_event_id}'

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

                for sk in self.bot.pe_scorekeeper:

                    await sk.send(f'Here is the list of players for the Obelisk Strucutre Deck Event. The role for the event is @{event_role} Please check to make sure they all have paid.')
                    await sk.send(dm_to_send)

                channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                await channel.set_permissions(role, read_messages=True, send_messages=True)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

    @command(name='open')
    async def open_event(self, ctx, event_type=''):

        # opens registration for a specific event

        if ctx.message.author.id in self.bot.authorized_users:

            if event_type in self.bot.events:

                exec(f'self.bot.{event_type}_active = True')

                await ctx.reply(f'{event_type} registration is now open!')

            else:

                await ctx.reply('Tournament type not recognized. Please use one of the following to open registration:\ngiantcard\nobeliksdeck\nsliferdeck\nspeedduel\nwinamat\n')

    @command(name='openall')
    async def open_all_events(self, ctx):

        # Opens registration for all events.

        if ctx.message.author.id in self.bot.authorized_users:

            for event in self.bot.events:

                exec(f'self.bot.{event}_active = True')

            await ctx.reply('Registration for all events has been opened!')


    @command(name='register', aliases=['reg'])
    @cooldown(1, 60, BucketType.user)
    async def register(self, ctx):

        # Assists the user in registering for an event. This will DM that user a link to sign up for an event. Once they are finished filling out the form
        # that is sent to them, they can finish and confirm their registration by typing !done.

        message_info = {
            self.bot.giantcard: ('Attack of the Giant Card', 'https://forms.gle/vT7vJath35k1Zvmn8'),
            self.bot.obeliskdeck: ('the Obelisk God Deck Event', 'https://forms.gle/KbhRL7oSd4JaP1jw7'),
            self.bot.sliferdeck: ('the Slifer God Deck Event', 'https://forms.gle/xrqMuLBNfawhJ2Xp8'),
            self.bot.speedduel: ('the Speed Duel Event', 'https://forms.gle/xoc4zYjLWCzk3T7X7'),
            self.bot.winamat: ('the Win a Mat Event', 'https://forms.gle/eQzQY9xL8XSpb4Qi8')
            }

        close_text = 'Sorry, registration for this event is not open!'

        from_channel = ctx.message.channel.id

        if from_channel in self.bot.target_channels:

            if from_channel == self.bot.giantcard and self.bot.giantcard_active == False:
            # Only lets people register for Attack of the Giant Card when the user makes registration active.

                await ctx.message.author.send(close_text)

            elif from_channel == self.bot.giantcard:

                await ctx.message.author.send(f'Here is the link to register for {message_info[from_channel][0]}!: {message_info[from_channel][1]}')
                await ctx.message.author.send('Once you have filled out that form, type **!done** to confirm your registration. If you do not your enrollment will not be complete.')
            
                self.bot.reg_from[ctx.message.author.id] = ctx.message.channel.id
                # Stores the channel ID from where the user called the !register command
                # When the user tells the bot !done to finish registration, it will use this info
                # to add the player to the appropriate table for the event!

            if from_channel == self.bot.obeliskdeck and self.bot.obeliskdeck_active == False:

                await ctx.message.author.send(close_text)

            elif from_channel == self.bot.obeliskdeck:

                await ctx.message.author.send(f'Here is the link to register for {message_info[from_channel][0]}!: {message_info[from_channel][1]}')
                await ctx.message.author.send('Once you have filled out that form, type **!done** to confirm your registration. If you do not your enrollment will not be complete.')
            
                self.bot.reg_from[ctx.message.author.id] = ctx.message.channel.id

            if from_channel == self.bot.sliferdeck and self.bot.sliferdeck_active == False:

                await ctx.message.author.send(close_text)

            elif from_channel == self.bot.sliferdeck:

                await ctx.message.author.send(f'Here is the link to register for {message_info[from_channel][0]}!: {message_info[from_channel][1]}')
                await ctx.message.author.send('Once you have filled out that form, type **!done** to confirm your registration. If you do not your enrollment will not be complete.')
            
                self.bot.reg_from[ctx.message.author.id] = ctx.message.channel.id

            if from_channel == self.bot.speedduel and self.bot.speedduel_active == False:

                await ctx.message.author.send(close_text)

            elif from_channel == self.bot.speedduel:

                await ctx.message.author.send(f'Here is the link to register for {message_info[from_channel][0]}!: {message_info[from_channel][1]}')
                await ctx.message.author.send('Once you have filled out that form, type **!done** to confirm your registration. If you do not your enrollment will not be complete.')
            
                self.bot.reg_from[ctx.message.author.id] = ctx.message.channel.id

            if from_channel == self.bot.winamat and self.bot.winamat_active == False:

                await ctx.message.author.send(close_text)

            elif from_channel == self.bot.winamat:

                await ctx.message.author.send(f'Here is the link to register for {message_info[from_channel][0]}!: {message_info[from_channel][1]}')
                await ctx.message.author.send('Once you have filled out that form, type **!done** to confirm your registration. If you do not your enrollment will not be complete.')
            
                self.bot.reg_from[ctx.message.author.id] = ctx.message.channel.id

    @command(name='remove')
    async def remove_player(self, ctx, member: Member, *, event_type=''):

        # Removes a player from an event table

        if ctx.message.author.id in self.bot.authorized_users:

            if event_type in self.bot.events:

                to_drop = member.id

                db.execute(f'DELETE FROM {event_type} where UserID = ?', to_drop)

                db.commit()
                    
                await ctx.reply(f'<@{to_drop}> successfully removed from the {event_type}')

            else:

                await ctx.reply('Tournament type not recognized. Please type one of the following to get the count:\ngiantcard\nobeliksdeck\nsliferdeck\nspeedduel\nwinamat\n')

    @command(name='seteventid')
    async def set_event_number(self, ctx, event_type='', *, num=''):

        # Sets the specified event's event ID number to the provided number
        # Useful if the bot crashes and you need to change the event ID Number,
        # As it defaults to 1.

        if ctx.message.author.id in self.bot.authorized_users:

            if event_type in self.bot.events:

                try:

                    event_num = int(num)

                except ValueError:

                    await ctx.reply('Your event number is not a number! Please use a number greater than 0 and less than 100')
                    return

                if len(event_num) == 0:

                    await ctx.reply('Please enter an updated event number')

                elif event_num == 0:

                    await ctx.reply('Event number cannot be 0! Please use a number greater than 0 and less than 100')

                elif event_type == 'giantcard':

                    await ctx.reply('You cannot change the Attack of the Giant Card event number!')

                elif len(event_num) > 2:

                    await ctx.reply('I seriously doubt you are running event number 100. Please enter a number greater than 0 and less than 100')

                else:

                    exec(f'self.bot.{event_type}_event_id = {event_num)}')

                    await ctx.reply(f'The {event_type} event\'s event ID number has been updated to {num}!')

            else:

                await ctx.reply('Tournament type not recognized. Please use one of the following:\ngiantcard\nobeliksdeck\nsliferdeck\nspeedduel\nwinamat\n')                
        
    @command(name='sliferdeckgo', aliases=['slifergo'])
    async def slifer_start(self, ctx):

        # See obelisk_start for usage

        if ctx.message.author.id in self.bot.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM sliferdeck')

            if counted[0][0] == 0:

                for sk in self.bot.pe_scorekeeper:

                   await sk.send('There are 0 players registered for the Slifer God Deck event. Event can not be started.')

            else:

                event_role = f'SliferGodDeck{self.bot.slifer_deck_event_id}'

                role = await self.bot.guild.create_role(name=event_role, mentionable=True)

                channel_name = f'Slifer God Deck Event {self.bot.slifer_deck_event_id}'

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

                for sk in self.bot.pe_scorekeeper:

                    await sk.send(f'Here is the list of players for the Slifer Strucutre Deck Event. The role for the event is @{event_role}. Please check to make sure they all have paid.')
                    await sk.send(dm_to_send)

                channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                await channel.set_permissions(role, read_messages=True, send_messages=True)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

    @command(name='speedduelgo')
    async def speed_duel_start(self, ctx):

        # See obelisk_start for usage

        if ctx.message.author.id in self.bot.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM speedduel')

            if counted[0][0] == 0:

                for sk in self.bot.pe_scorekeeper:

                    await sk.send('There are 0 players registered for the Speed Duel event. Event can not be started.')

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

                for sk in self.bot.pe_scorekeeper:

                    await sk.send(f'Here is the list of players for the Speed Duel Event. The role for the event is @{event_role}. Please check to make sure they all have paid.')
                    await sk.send(dm_to_send)

                channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                await channel.set_permissions(role, read_messages=True, send_messages=True)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

    @command(name='winamatgo')
    async def win_a_mat_start(self, ctx):

        # See obelisk_start for usage

        if ctx.message.author.id in self.bot.authorized_users:

            counted = db.records('SELECT COUNT (*) FROM winamat')

            if counted[0][0] == 0:

                for sk in self.bot.pe_scorekeeper:

                    await sk.send('There are 0 players registered for the Win A Mat event. Event can not be started.')

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

                for sk in self.bot.pe_scorekeeper:

                    await sk.send(f'Here is the list of players for the Win A Mat Event. The role for the event is @{event_role} Please check to make sure they all have paid.')
                    await sk.send(dm_to_send)

                channel = await self.bot.guild.create_text_channel(channel_name, category=self.bot.event_category, position=0)
                await channel.set_permissions(role, read_messages=True, send_messages=True)
                await channel.send(f'<@&{role.id}> your event is starting soon! All your pairings and results will be posted here! Good luck players!')

    @Cog.listener()
    async def on_ready(self):

        if not self.bot.ready:

            self.bot.cogs_ready.ready_up('sideevents')


def setup(bot):

    bot.add_cog(SideEvents(bot))
