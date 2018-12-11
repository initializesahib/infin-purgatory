"""This is Infin's image module.

It is used to manipulate images."""
import discord
from discord.ext import commands


class ImageModule:
    """Contains commands related to image manipulation."""

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    """Required to properly add the module to Infin."""
    bot.add_cog(ImageModule(bot))
