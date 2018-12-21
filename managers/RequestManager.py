"""This is Infin's request manager.

It handles automatically creating GitHub issues."""
import discord
from discord.ext import commands
from github import Github

class RequestManager:
    def __init__(self, bot):
        self.bot = bot
        self.github = Github(self.bot.config['github'])
    
    @commands.command(name='request')
    @commands.guild_only()
    async def request(self, ctx, name, *, function):
        """Creates a request for a command via GitHub."""
        repo_info = self.bot.config['repo'].split('/')
        org = self.github.get_organization(repo_info[0])
        core_repo = org.get_repo(repo_info[1])
        function = f"Automatic request made by {ctx.message.author.name}\n{function}"
        core_repo.create_issue(name, function)
        await ctx.message.add_reaction('✅')
