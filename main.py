import asyncio
import os
import random
from pathlib import Path

import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from youtubesearchpython import SearchVideos

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('DISCORD_PREFIX')
USER_ID = os.getenv('DISCORD_USER_ID')

bot = commands.Bot(command_prefix=PREFIX)
isPlaying = True
is_skipping = False
playlist = []


async def autoplay(ctx):
    global is_skipping
    voice = get(bot.voice_clients, guild=ctx.guild)
    while isPlaying:
        if playlist:
            song = playlist.pop()
            await ctx.channel.send('Now playing ' + song[1])
            voice.play(discord.FFmpegPCMAudio(f'audio_cache/{song[0]}.webm'))
            while voice.is_playing():
                if is_skipping:
                    is_skipping = False
                    voice.stop()
                    break
                else:
                    await asyncio.sleep(.1)
        else:
            song = get_random_song().strip('\n')
            audio = [song, song.split("=")[-1]]
            await download_file(audio[0], audio[1])


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command(pass_context=True, name='summon', help='Connect the bot to voice channel')
async def summon(ctx):
    if not await check_if_user_connected(ctx):
        return

    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice:
        await ctx.channel.send('Bot is already connected to voice channel')
        return

    channel = ctx.author.voice.channel
    await channel.connect()
    loop = asyncio.get_event_loop()
    loop.create_task(autoplay(ctx))
    await ctx.channel.send(f'Connected to {channel}')


@bot.command(pass_context=True, aliases=['p', 'play'], help='play music')
async def play_music(ctx, *, arg):
    if not await check_if_user_connected(ctx):
        return

    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.channel.send('Bot is not connected to voice channel, Please summon the bot first')
        return

    await search_video(ctx.channel, arg)


@bot.command(pass_context=True, aliases=['s', 'skip'], help='Skip music')
async def skip_music(ctx):
    global is_skipping

    if not await check_if_user_connected(ctx):
        return

    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.channel.send('Bot is not connected to voice channel, Please summon the bot first')
        return

    is_skipping = True


async def check_if_user_connected(ctx):
    connected = ctx.author.voice
    if not connected:
        await ctx.channel.send('You are not connected to any voice channel')
        return False
    return True


async def search_video(channel, search):
    search = SearchVideos(search, offset=1, mode="list", max_results=1)

    if len(search.result()) != 1:
        await channel.send('Unable to find any Video')
    else:
        await channel.send('Added to queue ' + search.result()[0][3])
        await download_file(search.result()[0][2], search.result()[0][1])


async def download_file(url, key):
    file_path = f'audio_cache/{key}.webm'

    if Path(file_path).is_file():
        playlist.append([key, url])
        return

    try:
        ydl_opts = {
            'outtmpl': file_path,
            'format': 'bestaudio/best',
        }
        youtube_dl.YoutubeDL(ydl_opts).download([url])
        playlist.append([key, url])
        clear_cache()
    finally:
        pass


def clear_cache():
    path, dirs, files = next(os.walk("audio_cache"))
    if len(files) > 1:
        print(path)


def get_random_song():
    return random.choice(list(open('autoplaylist.txt')))


bot.run(TOKEN)
