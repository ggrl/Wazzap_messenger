# README

## Wazzap Messenger

Wazzap messenger is a chat-application written in python, with a client- and server-script.

## Setup - local

To use the chat locally, run the server from the folder, where the 'server.py' and 'users.dat' are located. (e.g. 'python3 server.py')

Run the client and choose 1, if asked if you want to connect locally or remotely.

You can run as many clients as you want.

## Setup - remote

To use the chat remotely, run the server from the folder, where the 'server.py' and 'users.dat' are located. (e.g. 'python3 server.py')

**IMPORTANT: The server must be running before the next step!**

In another terminal run this command:
```bash
ssh -p 443 -R0:localhost:42000 tcp@a.pinggy.io
```
pinggy will create a ssh-tunnel to your chat-server.
It will display a tcp-link (e.g. **'tcp://xyz.pinggy.link:12345'**)

You need this link and the 'client.py' to connect to the server.

Start the client, choose '2' for remote connection and paste the tcp-link to the program.

## User-management

When you connect to the server, you will be asked for a username and password. If you already have a username and password, enter these, when asked.
If you want to create a new user, type your desired username and password, and a new user will be created, unless the username already exists.

## Chat

After sucessful user-login or -creation, you will join the chat.
Everything you write in the terminal will be broadcastet to every client connected to the server.

'/' is a escape-character which is used to send commands to the server.

Available commands:

- /help               -- Displays all commands
- /users              -- Lists currently connected users
- /pm <user> <text>   -- Sends a private message to the user
- /quit               -- Disconnects from the server


### created by:

Maryam and Gregor for the cybersteps-program


