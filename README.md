# AU-Registration-Bot
A Discord bot written in python to help with registering players for Alternate Universe's Remote Duel YCS, an online yugioh tournament played over webcam, for Konami. This was written specifically for this tournament and as is only functions on the discord server it was written for. 

This bot DMs users a link to sign up and pay for the tournament they want to play in and once enough players are signed up it alerts the scorekeeper for the event that it can start, creates a channel, and a role for the event as well.

This can be bipassed as well in case the user wants to start an event with less than 8 players.

One of the events, Attack of the Giant Card, starts at a specific time. I have included commands for the scorekeeper to open and close registration so that it can start with any number of entrants.

# Commands

## General User Commands

### !count 'event type'
  
  Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, giantcard
  
  Returns a count of how many players are registered for that particular event.
  
### !register (or !reg)
  
  Only works in the specified registration channels. The specified registration channels are where annoucements on what event and how to register are made. When a user used the command, they will be DM'd by AuRegistrationBot with a link to a google sheet with information on how to register for that event. Once they are done, they can type !done to confirm and finish their registration. 
  
## Commands for Authorized Users Only
  
  To use these commands, your discord ID must be stored in the authorized_users tuple that is stored in reg.py. If it is not there these commands will not work.
  
### !close 'event name'

Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, giantcard

Closes registration for the specific event. Closed registration means the !registration command won't work for that event. The user will be DM'd that registration is closed.

### !closeall

Closes registration for all events.

### !drop '@user' 'event name'

Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, giantcard

Drops the specified user from an event table.

### !giantcardgo

Starts the Attack of the Giant Card event. Closes registration for the event, DM's a list of all users who registered to the scorekeeper so that they can be entered into KTS. Creates the @AttackOftheGiantCard role and assigns all registered users to that role. Creates a new channel for the event, then makes a post alerting all users with the newly created role that their event will start soon, and to let them know where all their event info will be.

There are 4 more commands that work the same way, !obeliskdeckgo, !sliferdeckgo, !speedduelgo, and !winamatgo

### !obeliskdeckgo or !obeliskgo

See !giantcardgo. The only difference is that this will not close registration.

### !open 'event type'

Event type options: giantcard, obeliskdeck, sliferdeck, speedduel, giantcard

Opens registration for the specified event, making the !register command active

### !openall

Opens registration for all events.

### !sliferdeckgo

See !giantcardgo. The only difference is that this will not close registration.

### !speedduelgo

See !giantcardgo. The only difference is that this will not close registration.

### !winamatgo

See !giantcardgo. The only difference is that this will not close registration.

# MY BOT HAS COME A LONG WAY

I have included the original file as OLDAUregistrationbot to show how much I have learned while creating this.

The only thing that isn't included is the token0 file. You will have to create your own in the bot folder if you would like to see this in action, as well as change any channels, categories and guilds to your own server. I have marked this wherever necessary.
  
  
