"""This is Infin's module manager.

It handles loading and unloading modules."""
import discord
from discord.ext import commands


class ModuleManager:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload(self, ctx, *, module):
        """Unloads then loads a given module."""
        self.bot.unload_extension(f'modules.{module}')
        self.bot.load_extension(f'modules.{module}')
        await ctx.message.add_reaction('✅')

    @commands.command(name='unload')
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads the given module."""
        self.bot.unload_extension(f'modules.{module}')
        self.bot.config['modules'].remove(f'modules.{module}')
        await ctx.message.add_reaction('✅')

    @commands.command(name='load')
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Loads the given module."""
        self.bot.load_extension(f'modules.{module}')
        self.bot.config['modules'].append(f'modules.{module}')
        await ctx.message.add_reaction('✅')

    @commands.command(name='modules')
    async def modules(self, ctx):
        """Lists all loaded modules."""
        module_message = f":white_check_mark: There are **{len(self.bot.config['modules'])}** modules loaded:\n"
        for module in self.bot.config['modules']:
            module_message = f'{module_message}**{module[:-7]}**\n'
        module_message = f'{module_message}Run **infin help** for commands.'
        await ctx.message.add_reaction('✅')
        await ctx.message.author.send(module_message)
