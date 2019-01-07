"""This is Infin's meta module.

It is used to get or set information related to the bot itself."""
import asyncio
import inspect
import subprocess
import os
import discord
from discord.ext import commands


class MetaModule:
    """Contains commands related to the bot itself, such as version."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='status')
    @commands.is_owner()
    async def status(self, ctx, *, new_status):
        """Changes the bot's status on Discord."""
        new_game = discord.Game(name=new_status)
        await self.bot.change_presence(status=discord.Status.online, game=new_game)
        await ctx.message.add_reaction('✅')


    @commands.command(name='source')
    async def source(self, ctx, *, cmd: str = None):
        """Displays source code of a given command."""
        root = 'https://github.com/infinbot'
        if cmd is None:
            await ctx.send(root)
        else:
            real_cmd = self.bot.get_command(cmd.replace('.', ' '))
            if real_cmd is None:
                await ctx.message.add_reaction('⛔')
            else:
                src = real_cmd.callback.__code__
                lines, first_line = inspect.getsourcelines(src)
                location = os.path.relpath(src.co_filename).replace('\\', '/')
                module_name = location.split('/')[0]
                rest = ''.join(location.split('/')[1:])
                root = 'https://github.com/initializesahib/infin-stable'
                if not location.startswith('managers'):
                    source_url = f'<{root}/{module_name}/blob/master/{rest}#L{first_line}-L{first_line + len(lines) - 1}>'
                else:
                    source_url = f'<{root}/blob/master/{module_name}/{rest}#L{first_line}-L{first_line + len(lines) - 1}>'
                await ctx.send(source_url)

def setup(bot):
    """Required to properly add the module to Infin."""
    bot.add_cog(MetaModule(bot))
