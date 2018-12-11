"""This is Infin's blacklist manager.

It handles preventing certain users from using commands."""
import discord
from discord.ext import commands

class BlacklistManager:
    """Allows to owner to prevent certain users from using the bot."""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='blappend')
    @commands.is_owner()
    async def blappend(self, ctx, *, blacklisted: discord.Member):
        """Appends a user to the global blacklist."""
        if str(blacklisted.id) in self.bot.blacklist:
            await ctx.message.add_reaction('⛔')
        else:
            self.bot.blacklist.append(str(blacklisted.id))
            if self.bot.config['database']['type'] == 'postgres':
                async with self.bot.pool.acquire() as conn:
                    await conn.execute(f"INSERT INTO blacklisted VALUES ('{blacklisted.id}');")
            elif self.bot.config['database']['type'] == 'mongodb':
                collection = self.bot.pool['infin']['blacklisted']
                await collection.insert_one({id: str(blacklisted.id)})
            elif self.bot.config['database']['type'] == 'redis':
                await self.bot.pool.lpush('blacklisted', str(blacklisted.id))
            await ctx.message.add_reaction('✅')
    
    @commands.command(name='blremove')
    @commands.is_owner()
    async def blremove(self, ctx, *, blacklisted: discord.Member):
        """Removes a user from the global blacklist."""
        if str(blacklisted.id) not in self.bot.blacklist:
            await ctx.message.add_reaction('⛔')
        else:
            self.bot.blacklist.remove(str(blacklisted.id))
            if self.bot.config['database']['type'] == 'postgres':
                async with self.bot.pool.acquire() as conn:
                    await conn.execute(f"DELETE FROM blacklisted WHERE id='{blacklisted.id}';")
            elif self.bot.config['database']['type'] == 'mongodb':
                collection = self.bot.pool['infin']['blacklisted']
                await collection.delete_many({id: str(blacklisted.id)})
            elif self.bot.config['database']['type'] == 'redis':
                await self.bot.pool.lrem('blacklisted', 1, str(blacklisted.id))
            await ctx.message.add_reaction('✅')  

    @commands.command(name='lsbl')
    @commands.is_owner()
    async def lsbl(self, ctx):
        """Lists all blacklisted users."""
        display_message = f':white_check_mark: **{len(self.bot.blacklist)}** blacklisted users: '
        for user in self.bot.blacklist:
            display_message = f'{display_message}<@{user}> '
        await ctx.message.author.send(display_message)
