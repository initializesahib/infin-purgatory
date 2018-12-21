"""This is the Infin core.

It handles connecting to Discord and the database, and managing modules."""
import aioredis
import asyncio
import asyncpg
import json
import discord
from discord.ext import commands
from managers import RequestManager, ModuleManager, BlacklistManager
import motor.motor_asyncio

print('Infin 1.0.1 © 2018 Sahibdeep Nann')
print('Licensed under BSD-2-Clause, see LICENSE for details')

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
config['infin_version'] = '1.0.1'

bot = commands.Bot(command_prefix='infin ',
                   description='The modularized, open Discord bot of the future.',
                   pm_help=True)
bot.config = config
bot.blacklist = []

@bot.event
async def on_ready():
    """Tells when we're connected to Discord and sets the default status."""
    print('Connected to Discord')
    await bot.change_presence(activity=discord.Activity(name='infinbot.github.io'))


@bot.event
async def on_message(msg):
    """Ignores the message of bots."""
    if not msg.author.bot:
        # Ignores blacklisted people.
        if not str(msg.author.id) in bot.blacklist:
            await bot.process_commands(msg)


async def start_infin():
    """Connects to the database and Discord."""
    if bot.config['database']['type'] == 'postgres':
        bot.pool = await asyncpg.create_pool(user=bot.config['database']['user'],
                                             host=bot.config['database']['host'],
                                             port=bot.config['database']['port'],
                                             password=bot.config['database']['password'],
                                             database='infin')
        print('Connected to PostgreSQL')
        async with bot.pool.acquire() as conn:
            await conn.execute("CREATE TABLE IF NOT EXISTS blacklisted(id text);")
            blacklisted = await conn.fetch('SELECT * FROM blacklisted;')
            for user in blacklisted:
                bot.blacklist.append(user['id'])
    elif bot.config['database']['type'] == 'mongodb':
        bot.pool = motor.motor_asyncio.AsyncIOMotorClient(bot.config['database']['host'],
                                                          bot.config['database']['port'])
        print('Connected to MongoDB')
        blacklisted = bot.pool['infin']['blacklisted'].find()
        async for user in blacklisted:
            bot.blacklist.append(user['id'])
    elif bot.config['database']['type'] == 'redis':
        bot.pool = await aioredis.create_pool(f"redis://{bot.config['database']['host']}")
        print('Connected to Redis')
        blacklisted = await bot.pool.execute('LRANGE', 'blacklisted', 0, -1)
        for user in blacklisted:
            bot.blacklist.append(user)
    print('Loaded blacklist')
    await bot.login(bot.config['token'])
    await bot.connect(reconnect=True)

if __name__ == '__main__':
    bot.add_cog(BlacklistManager.BlacklistManager(bot))
    print('Loaded manager BlacklistManager')
    bot.add_cog(ModuleManager.ModuleManager(bot))
    print('Loaded manager ModuleManager')
    bot.add_cog(RequestManager.RequestManager(bot))
    print('Loaded manager RequestManager')
    for module in bot.config['modules']:
        bot.load_extension(module)
        print(f'Loaded module {module}')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_infin())
    loop.close()
