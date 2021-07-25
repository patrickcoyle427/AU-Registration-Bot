from discord import Member
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown 
from discord.utils import get

from ..db import db

class MainEvent(Cog):

    def __init__(self, bot):

        self.bot = bot
        # User IDs of anyone who has access to some of the registration commands.
        # Add discord User IDs here to grant access
        # The only commands that users who are not in this list can use are !count and !register

    @command(name='clearreports')
    async def clear_all_reports(self, ctx):

        # Clears out all reports from the previous round to let players report again.
        # Also increments the round count

        if ctx.message.author.id in self.bot.authorized_users:

            if self.bot.mainevent_active == True:

                self.bot.reports.clear()

                await ctx.reply(f'Round {self.bot.me_round_count} reports have been cleared!')

                self.bot.me_round_count += 1

            else:

                await ctx.reply('The main event is closed!')

    @command(name='closemain')
    async def close_main_event(self, ctx):

        # Closes reporting and dropping from the main event

        if ctx.message.author.id in self.bot.authorized_users:

            if self.bot.mainevent_active == True:

                self.bot.mainevent_active = False

                await ctx.reply('Main event is now closed!')

            else:

                await ctx.reply('Main event is already closed! Use !openmain if you would like to open the main event!')

    @command(name='dropme')
    async def drop_from_me(self, ctx):

        # Alters the main event scorekeeper that the player who uses this command would like to be dropped from the main event.

        if self.bot.mainevent_active == True:

            name = ctx.message.author.nick

            if name == None:

                name = ctx.message.author.name

            await self.bot.me_scorekeeper.send(f'Drop {name} from the main event!')

            await ctx.reply('You have been dropped from the main event! Thanks for playing!')

        else:

            await ctx.reply('The main event is closed!')

    @command(name='openmain')
    async def open_main_event(self, ctx):

        # Opens reporting and dropping from the main event

        if ctx.message.author.id in self.bot.authorized_users:

            if self.bot.mainevent_active == False:

                self.bot.mainevent_active = True

                await ctx.reply('Main event is now open!')

            else:

                await ctx.reply('Main event is already open! Use !closemain if you would like to close the main event!')

    @command(name='report')
    @cooldown(1, 10, BucketType.user)
    async def report_result(self, ctx, result='', *, table=''):

        # Alerts the main event scorekeeper whether the player who uses the command, has won, lost, or drew their match

        accept_results = ('win', 'won', 'lost', 'lose', 'loss', 'draw', 'drew')

        if self.bot.mainevent_active == True:

            try:

                table_num = int(table)

                if table == '':

                    await ctx.reply('Please enter a table number!')
                    return

                elif table_num > 3:

                    await ctx.reply('Table number too high. Your table number is definitely less than 1000.')
                    return

            except ValueError:

                await ctx.reply('That is not a table number! Please only enter a number between 1 and 100!')
                return

            name = ctx.author.nick
            # Players are supposed to change their discord nickname to their real name for online events.

            if name == None:

                name = ctx.message.author.name
                # If they have no nickname set, send their username

            userid = ctx.message.author.id

            result = result.lower()

            get_report = self.bot.reports.get(userid, False)

            if get_report == False:

                if result in accept_results:

                    if result == accept_results[0] or result == accept_results[1]:

                        await ctx.reply('Your result has been accepted! Thank you!')
                        await self.bot.me_scorekeeper.send(f'{name} won at table {table} round {self.bot.me_round_count}!')

                        self.bot.reports[userid] = f'win at table {table} for round {self.bot.me_round_count}'

                    elif result == accept_results[2] or result == accept_results[3] or result == accept_results[4]:

                        await ctx.reply('Your result has been accepted! Thank you!')
                        await self.bot.me_scorekeeper.send(f'{name} lost at table {table} round {self.bot.me_round_count}!')

                        self.bot.reports[userid] = f'loss at table {table} for round {self.bot.me_round_count}'

                    elif result == accept_results[5] or result == accept_results[6]:

                        await ctx.reply('Your result has been accepted! Thank you!')
                        await self.bot.me_scorekeeper.send(f'{name} drew at table {table} round {self.bot.me_round_count}')

                        self.bot.reports[userid] = f'draw at table {table} for round {self.bot.me_round_count}'

                else:

                    await ctx.reply(f'That is not an accepted result. Please type either:\nwin\nlose\ndraw\nYou must also include the table number! See the FAQ for correct usage! Please message <@{self.bot.me_scorekeeper.id}> if you have a problem!')
                    return
                
            else:

                await ctx.reply(f'You have already reported a {get_report}. If this is not correct, please DM <@{self.bot.me_scorekeeper.id}>')

        else:

            await ctx.reply('The main event is closed!')

    @command(name='rolecall')
    async def roles_for_all(self, ctx):

        # Janky way of assigning the correct role to players in event.
        # TODO: Make this less janky, find a way to only allow players in the main event to get the correct role.

        role = get(self.bot.guild.roles, id=853704416325533717)

        if ctx.message.author.id in self.bot.authorized_users:

            for mem in self.bot.guild.members:

                if len(mem.roles) < 2:

                    await mem.add_roles(role)

            await ctx.reply('Finished Assigning Roles!')

    @command(name='setroundnum')
    async def set_round_number(self, ctx, num=''):

        # Changes the main event's round number. Useful if this bot crashes and you need to change the round count.

        if ctx.message.author.id == self.bot.me_scorekeeper.id:
            # Only the main event scorekeeper can use this command

            try:

                event_num = int(num)

            except ValueError:

                await ctx.reply('Your round number is not a number! Please use a number greater than 0 and less than 100')
                return

            except NameError:

                await ctx.reply('Please enter an updated round number!')

            if len(num) == 0:

                await ctx.reply('Please enter an updated round number!')

            elif event_num == 0:

                await ctx.reply('Round number cannot be 0! Please use a number greater than 0 and less than 100')

            elif len(num) > 2:

                await ctx.reply('I seriously doubt you are on that round. Please enter a number greater than 0 and less than 100')

            else:

                self.bot.me_round_count = event_num

                await ctx.reply(f'The main event\'s round number has been updated to {num}!')
        
    @Cog.listener()
    async def on_ready(self):

        if not self.bot.ready:

            self.bot.cogs_ready.ready_up('mainevent')


def setup(bot):

    bot.add_cog(MainEvent(bot))
