# AU-Registration-Bot
A Discord bot written in python to help with registering players for Alternate Universe's Remote Duel YCS, an online yugioh tournament played over webcam, for Konami. This was written specifically for this tournament and as is only functions on the discord server it was written for. 

This bot DMs users a link to sign up and pay for the tournament they want to play in and once enough players are signed up it alerts the scorekeeper for the event that it can start, creates a channel, and a role for the event as well.

Events can also be started with less than 8 people if needed with commands.

There are also commands to open and close registration to control event flow.

Want to see the bot when it was in action? You can check out the discord server it was used on by checking
https://discord.gg/RkU5fV2nS7 

## VERSION 2.0 ##

Removed the reg cog, its commands have been separated into two cogs, sideevents and mainevent.

Added more helpful commands, such as !list, !add, !seteventnum, and !setroundnum

# COMMANDS

  If a command says "This command can only be used by Authorized Users", it is referring to the tuple 
  self.authorized_users in the bot's __init__.py file. These commands can only be used by users who's discord UserID
  is added to this tuple.

## Mainevent Cog Commands

### !clearreports

  This command can only be used by Authorized Users.

  Removes all the win/loss/draw reports for the current round and then updates the current round count. This command
  will not function if the main event is closed.
  
  If you don't do this before moving onto the next round, players will not be able to report results for the latest
  round!
  
### !closemain

  This command can only be used by Authorized Users.

  Closes the main event, which stops players from being able to use the !report and !dropme commands. Closed is the
  defualt status for the main event.
  
### !dropme

  Alerts the main event scorekeeper that the player who used this command would like to drop from the main event
  
### !openmain

  This command can only be used by Authorized Users.

  Opens the main event, meaning the !report and !dropme commands will work for players!
  
### !report 'result' 'table#number

  Sends a DM from this bot to the main event scorekeeper with the result of that player's round. 
  Accepted results are: win, won, lose, lost, draw, drew.
  
  Table# is the table that the player was at for that round.
  
  Usage looks like: !report win 27 or !report loss 4 or !report draw 190
  
### !rolecall

  This command can only be used by Authorized Users.

  Currently this gives a specified role to all users without a role. This was necessary for the YCS so that users could
  access all the necessary channels for the event. In the future I plan to rewrite this to be more useful.
  
### !setroundnum 'num'

  This command can only be used by Authorized Users.

  Sets the current round of the main event to the specified number. This is useful if the bot crashes and you need to
  reset the round number, as it defaults to 1.
  
  Usage looks like: !setroundnum 5
  
## Sideevent Cog Commands

### !add '@member' 'eventtype'

  This command can only be used by Authorized Users.
  
  Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, winamat
  
  Adds a player to a side event table. Used for when you need to move a player to another event or if a player didn't
  properly finish registration but you still think they should be able to play. This will trigger the notifications for
  4 players are in an event and if that player is the 8th player, this will create the event room, assign roles for that
  event and alert the side event scorekeepers that an event can start.
  
  Usage looks like !add @pcrulez winamat
  
### !close 'event type'

  This command can only be used by Authorized Users.
  
  Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, winamat
  
  Closes the specified event, meaning that event won't be advertised and the !register command won't function in that
  event's channel.
  
  Usage looks like: !close speedduel
  
### !closeall

  This command can only be used by Authorized Users.
  
  Closes all public events, meaning no public event will be advertised and the !register command won't function in
  any of their channels.
  
### !count 'event type'
  
  Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, winamat
  
  Returns a count of how many players are registered for that particular event.
  
  Usage looks like !count sliferdeck
  
### !done

  All this command does is respond to the user telling them they need to say !done to the AURegistrationBot in a DM
  if they want to finish registering for the event they registered for. Basically it alerts the user they aren't using
  the bot in the correct way.
  
### !giantcardgo

  This command can only be used by Authorized Users.

  Starts the Attack of the Giant Card event. Closes registration for the event, DM's a list of all users who registered 
  to the scorekeeper so that they can be entered into KTS. Creates the @AttackOftheGiantCard role and assigns 
  all registered users to that role. Creates a new channel for the event, then makes a post alerting all users 
  with the newly created role that their event will start soon, and to let them know where all their event info 
  will be. This also closes registration for this event.
  
### !list 'event type'

  This command can only be used by Authorized Users.
  
  Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, winamat

  Replys to the user with a list of all players currently registered for the specified event.
  
  Usage looks like: !list obeliskdeck
  
### !obeliskdeckgo

  This command can only be used by Authorized Users.

  Starts the Obelisk God Deck event. Closes registration for the event, DM's a list of all users who registered 
  to the scorekeeper so that they can be entered into KTS. Creates the @ObeliskDecKEvent{event_number} role and assigns 
  all registered users to that role. Creates a new channel for the event, then makes a post alerting all users 
  with the newly created role that their event will start soon, and to let them know where all their event info 
  will be. Once that is complete, the obelisk deck event number is incremented by 1.

  There are 3 more commands that work the same way: !sliferdeckgo, !speedduelgo, and !winamatgo
 
### !open 'event type'

  This command can only be used by Authorized Users.

  Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, winamat

  Opens registration for the specified event, making the !register command active.
  
  Usage looks like: !open giantcard

### !openall

  This command can only be used by Authorized Users.
  
  Opens registration for all public events, meaing the !register command will be active for all users.
  
### !register (or !reg)
  
  Only works in the specified registration channels. The specified registration channels are where annoucements on what event and how to register are made. When a user used the command, they will be DM'd by AuRegistrationBot with a link to a google sheet with information on how to register for that event. Once they are done, they can type !done to confirm and finish their registration. 

### !remove '@user' 'event name'

  This command can only be used by Authorized Users.

  Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, winamat

  Drops the specified user from an event table.
  
  Usage looks like: !remove @pcrulez winamat
  
### seteventid 'event type' 'event num'

  This command can only be used by Authorized Users.
  
  Event type options: obeliskdeck, sliferdeck, speedduel, winamat
  
  Event num must be greater than 0 and less than 100.
  
  Changes the event ID number for the specified event to the provided number. This is useful if the bot crashes and you
  need to change the event number to what it should be, as each event defaults to 1.
  
  Usage looks like !seteventid speedduel 6

### !sliferdeckgo

  This command can only be used by Authorized Users.

  See !obeliskdeckgo. The only difference is that this will not close registration.

### !speedduelgo

  This command can only be used by Authorized Users.

  See !obeliskdeckgo. The only difference is that this will not close registration.

### !winamatgo

  This command can only be used by Authorized Users.

  See !obeliskdeckgo. The only difference is that this will not close registration.

# MY BOT HAS COME A LONG WAY

I have included the original file as OLDAUregistrationbot to show how much I have learned while creating this.

The only thing that isn't included is the token0 file. You will have to create your own in the bot folder if you would like to see this in action, as well as change any channels, categories and guilds to your own server. I have marked this wherever necessary.
  
  
