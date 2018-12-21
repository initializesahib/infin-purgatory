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

    @commands.command(name='version')
    async def version(self, ctx):
        """Launches Git processes to get the latest commit versions of each module."""
        versions_message = f"**infin**: {self.bot.config['infin_version']}\n"
        commit = subprocess.Popen(['git', 'ls-remote', 'git://github.com/initializesahib/infin-purgatory.git'], stdout=subprocess.PIPE)
        commit.name = "commit"
        done = False
        while not done:
          finished = commit.poll()
          if finished is not None:
            dat = commit.stdout.read().decode('utf-8').split('\n')[0].split(' ')[0][:-5]
            versions_message = f'{versions_message}**{commit.name}**: {dat}\n'
            done = True
            break
          else:
            await asyncio.sleep(0.1)
            continue
        await ctx.send(versions_message)

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
                if location.startswith('managers'):
                    root = 'https://github.com/infinbot/core'
                if not location.startswith('managers'):
                    source_url = f'<{root}/{module_name}/blob/master/{rest}#L{first_line}-L{first_line + len(lines) - 1}>'
                else:
                    source_url = f'<{root}/blob/master/{module_name}/{rest}#L{first_line}-L{first_line + len(lines) - 1}>'
                await ctx.send(source_url)

def setup(bot):
    """Required to properly add the module to Infin."""
    bot.add_cog(MetaModule(bot))
