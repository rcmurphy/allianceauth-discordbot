import random

# used for api calls
import requests

# regex
import re

# core discord.py library
import discord

from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color

# py file containing sensitive information (CLIENT_ID, OWNER_ID)
import secrets

# Google Text-to-Speech library for TTS commands
from gtts import gTTS



class TTS(commands.Cog):
    """
    TTS Tools
    """

    def __init__(self, bot):
        self.bot = bot

        self.voice_client = None

    @commands.command(pass_context=True)
    async def tts(self, ctx):
        """Announces a message in voice"""

        message = ctx.message
        # ensure the bot does not reply to itself
        if message.author.id == self.bot.user.id:
            await message.channel.send('No recursion allowed!')
            return

        split_msg = message.content.split()

        # play audio via GTTS of the user's message
        if len(split_msg) >= 2:

            # TODO: use bytestream object instead of saving .mp3 locally
            tts = gTTS(" ".join(split_msg[1:]), tld='com')
            tts.save('tts.mp3')

            if self.voice_client:
                await self.voice_client.disconnect()

            try:
                channel = message.author.voice.channel
            except AttributeError:
                await message.channel.send('User is not in accessible voice channel!')

            self.voice_client = await channel.connect(reconnect=False)
            audio_source = await discord.FFmpegOpusAudio.from_probe('tts.mp3')
            self.voice_client.play(audio_source)

            await message.channel.send('Playing TTS in {}'.format(channel))

            # TODO: add text limit/allow a stop command while bot is speaking
            # disconnect voice when bot is finished speaking
            while self.voice_client.is_playing():
                continue
            await self.voice_client.disconnect()
            await message.channel.send('Left channel.')

        # force bot to leave vc if it is stuck
        elif message.content.lower().endswith('leave vc'):
            try:
                await self.voice_client.disconnect()
                await message.channel.send('Forced left voice channel.')
            except AttributeError:
                await message.channel.send('I do not seem to be in a voice channel right now.')



def setup(bot):
    """
    setup the cog
    :param bot:
    """

    bot.add_cog(TTS(bot))
