"""This is Infin's base module.

It contains standard bot commands, like ping and info."""
import datetime
import random
import time
import discord
from discord.ext import commands


class BaseModule:
    """Contains commands that are usual for a Discord bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Finds the delay between sending a message and sending one back."""
        ping_message = await ctx.send(':ping_pong: in **...** ms')
        latency_delta = ping_message.created_at - ctx.message.created_at
        message_latency = latency_delta.total_seconds() * 1000
        await ping_message.edit(content=f':ping_pong: in **{message_latency}** ms')

    @commands.command(name='rping')
    async def rping(self, ctx):
        """Finds the delay between sending a message and recieving said message."""
        latency_delta = datetime.datetime.utcfromtimestamp(
            time.time()) - ctx.message.created_at
        discord_latency = latency_delta.total_seconds() * 1000
        await ctx.send(f':clock10: in **{discord_latency}** ms')

    @commands.command(name='invite')
    async def invite(self, ctx):
        """Sends an invite to the official Infin server in private messages."""
        await ctx.message.add_reaction('📬')
        await ctx.message.author.send('https://discord.gg/7UnvACY')

    @commands.command(name='decide')
    async def decide(self, ctx, *choices):
        """Chooses an item out of a list of items."""
        await ctx.send(f':white_check_mark: **I choose...** {random.choice(choices)}')

    @commands.command(name='info')
    async def info(self, ctx):
        """Sends an embed containing information about the bot."""
        info_embed = discord.Embed(colour=discord.Colour.blue())
        info_embed.set_author(name='Infin', icon_url=self.bot.user.avatar_url)
        info_embed.add_field(name='Database', value='PostgreSQL')
        info_embed.add_field(name='Version', value=self.bot.config['infin_version'])
        info_embed.add_field(
            name='Bot Library',
            value='[discord.py](https://discordpy.readthedocs.io/en/rewrite/)')
        info_embed.add_field(
            name='Developed By',
            value='[InitializeSahib#0001](https://github.com/InitializeSahib)')
        info_embed.add_field(name='Help Command', value='infin help')
        info_embed.add_field(name='License', value='BSD-2-Clause')
        info_embed.set_footer(text='Open source: https://github.com/infinbot')
        await ctx.send(embed=info_embed)


def setup(bot):
    """Required to properly add the module to Infin."""
    bot.add_cog(BaseModule(bot))
