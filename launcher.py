'''
AURegistrationBot - Written by Patrick Coyle

Bot to assist with registration for side events and for reporting results for the
main event of the Konami Remote Duel YCS, an online yugioh tournament played over
webcam, faciilated by Discord.

This was written specifically for this tournament and as is only functions on
the Alternate Universes RDYCS discord server it was written for. To use it
on your own server, you will need to update any of the guild and user IDs for
for your own server and users. I have labeled anything that needs to be changed
to do this in the bot __init__ file.

List of commands can be found at:
https://github.com/patrickcoyle427/AU-Registration-Bot/blob/main/README.md
'''

from lib.bot import bot

VERSION = '2'

bot.run(VERSION)
