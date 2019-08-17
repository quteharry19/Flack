# Flack Messenger

Project 2 : CS50 web Programming with Python and JavaScript

A Chat Application anyone can log in by just giving the Display name which will be stored locally on his/her computer browser
in localStorage and will be remmembered until user press the logout button from the navbar or clears the browser files.

channel name on first login will be School the default channel name already defined in global variable.
once logged in every change of channel will update the localStorage Variable on client.

a sidebar navigation is used to display the existing channel and a link to add a new unique channel

username , time stamp  is properly displayed with every message

represented self name as "me" 

only 100 recent messages per channel will be stored

sketchy bootstrap is used from www.bootswatch.com for a different visual.

used ios style chat bubble messages with css properties 

ionicon css for icons library

i had Deployed this app to azure on https://flack.azurewebsites.net
the config file is web.config

no database is used to store messages or channels everything is stored in python global variables


# Personal Touch

1. user can delete his/her own messages by pressing the red delete icon near his message - socket connection used for this to delete mesaage from server side.

2. user can send the private message to any user who had already send atleast one message in any chat by clicking on the username/display name associated with the message.