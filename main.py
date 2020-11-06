import asyncio
import json
import os
import random
from pathlib import Path

import discord
import requests
import youtube_dl
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from youtubesearchpython import SearchVideos

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('DISCORD_PREFIX')
YOUTUBE_KEY = os.getenv('YOUTUBE_API1')

bot = commands.Bot(command_prefix=PREFIX)
is_playing = True
is_skipping = False
is_recommended = True
playlist = []
loop = asyncio.get_event_loop()
current_playing_song = ""


async def autoplay(ctx):
    global is_skipping, current_playing_song
    voice = get(bot.voice_clients, guild=ctx.guild)
    while is_playing:
        if playlist:
            song = playlist.pop()
            current_playing_song = song[0]
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
            if is_recommended:
                video_id = current_playing_song if current_playing_song else get_random_song()[-1]
                await get_recommended_song(ctx, video_id)
            else:
                audio = get_random_song()
                await download_file(ctx.channel, audio[0], audio[1])


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command(pass_context=True, name='summon', help='Connect the bot to voice channel')
async def summon(ctx):
    global is_playing
    if not await check_if_user_connected(ctx):
        return

    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice:
        await ctx.channel.send('Bot is already connected to voice channel')
        return

    is_playing = True
    channel = ctx.author.voice.channel
    await channel.connect()
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

    if is_playing:
        await ctx.channel.send('Skipping the song')
        is_skipping = True
    else:
        await ctx.channel.send('Nothing is playing')


@bot.command(pass_context=True, name='disconnect', help='Disconnect the bot')
async def disconnect(ctx):
    global is_playing
    if not await check_if_user_connected(ctx):
        return

    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.channel.send('Bot is not connected to voice channel, Please summon the bot first')
        return

    is_playing = False
    await ctx.channel.send('Bye Bye')
    await voice.disconnect()


@bot.command(pass_context=True, aliases=['sw', 'switch'], help='Switch play mode')
async def switch_mode(ctx):
    global is_recommended
    is_recommended = not is_recommended
    await ctx.channel.send(f"Autoplay mode changed to {'Recommended' if is_recommended else 'Autoplaylist'}")


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
        await channel.send('Added to stack ' + search.result()[0][3])
        await download_file(channel, search.result()[0][2], search.result()[0][1])


async def download_file(channel, url, key):
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
    except Exception as e:
        await channel.send(str(e))
        pass


def clear_cache():
    files = next(os.walk("audio_cache"))
    if len(files) > 100:
        pass


async def get_recommended_song(ctx, key):
    global YOUTUBE_KEY
    audio = get_random_song()
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId=" \
          f"{key}&type=video&key={YOUTUBE_KEY}"
    response = requests.get(url)
    if response.ok:
        songs = json.loads(response.content)['items']
        if len(songs) > 1:
            songs.pop(0)
            video_id = random.choice(songs)['id']['videoId']
            audio = [f"https://www.youtube.com/watch?v={video_id}", video_id]
    else:
        if YOUTUBE_KEY is os.getenv('YOUTUBE_API1'):
            YOUTUBE_KEY = os.getenv('YOUTUBE_API2')
        else:
            YOUTUBE_KEY = os.getenv('YOUTUBE_API1')

    await download_file(ctx.channel, audio[0], audio[1])


def get_random_song():
    song = random.choice(list(open('autoplaylist.txt'))).strip('\n')
    return [song, song.split("=")[-1]]


bot.run(TOKEN)
