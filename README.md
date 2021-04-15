# FNWhisperBot
This bot allows you to whisper with your Fortnite friends without running Fortnite. Since Epic removed this option from launcher I decided to create a simple bot using fortnitepy library.

This software requires Python 3.7 and fortnitepy library

Usage: install the required python libraries using install_libraries.bat or just run "pip install fortnitepy"

Start the software by running FNWhisperBot.py

You will be asked to enter your email and password.

If captcha is required open GetCaptcha.url and login using Epic account. It might require to use a private browser window if you were already logged in.

Enter the code from the captcha and proceed.

On start the bot will list all your friends which are online and their Epic-IDs.
Friend name: MyBestFriend, Epic-ID: abcdef0123456789abcdef0123456789

To whisper you need to use the following format: "epic-id:message". For example:
epic-id:message\abcdef0123456789abcdef0123456789:hello world

If you recieve a message it will look like this:
19:49:44: MyBestFriend (abcdef0123456789abcdef0123456789): "hello world"

In the config.json file you can setup whether or not the bot should accept party invitations or friend requests.

Once someone joins your party you will see their outfit CID and pickaxe.
