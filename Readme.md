## Discord Music Bot

MusicBot is the original Discord music bot written for ``Python 3.6+``, using the ``discord.py`` library. It plays requested songs from YouTube into a Discord server (or multiple servers). Besides, if the queue becomes empty MusicBot will play from recomendation existing songs with configuration. The bot features a permission system allowing owners to restrict commands to certain people. As well as playing songs.

![Capture](https://user-images.githubusercontent.com/70603773/119663019-9ebfdd00-be4f-11eb-8621-d3adf1ed518a.PNG)

## Setup
1). Clone the repo to your system. 

2). edit the ``.env_example`` and save it ``.env``

3). You have two ways to run the bot.

A). The First and the easier way install docker in your system from ``"https://docs.docker.com/engine/install/ubuntu/"`` and just go to the folder and run ``sudo docker build . -t musicbot``.

*). outcome will be ⤵️⤵️ .

![Capture2](https://user-images.githubusercontent.com/70603773/119664161-b055b480-be50-11eb-80a1-89e9268a025f.PNG)

*) now just run the command ``sudo docker run musicbot`` to start your musicbot and if u want to run it unless stopped manually than run the following command             ``docker   run -d --restart unless-stopped musicbot``

This is the Easiest way to run your musicbot

<h2>The Second way to run the musicbot is by python</h2>

1). The first 2 steps are same

2). Know u should have pip3 in your system && install it by following commands ``sudo apt-get update && sudo apt-get -y install python3-pip``

3). Now install the Requirement.txt from pip by ``pip3 install -r requirements.txt``

4). You should also have FFmpeg install it by ``sudo apt update && sudo apt install ffmpeg``

5). Run the main.py with ``python3`` 

And Ya Peace Out ✌️✌️☮️☮️

<h2>Bot Commands</h2>

There are many commands that can be used with the bot. Most notably, the play <url> command (preceded by your command prefix) will download, process, and play a song from YouTube. 
  
A full list of commands is available by ``help``(preceded by your command prefix).



