"""This is the Infin core.

It handles connecting to Discord and the database, and managing modules."""
import aioredis
import asyncio
import asyncpg
import json
import discord
from discord.ext import commands
from managers import ModuleManager, BlacklistManager
import motor.motor_asyncio

print('Infin 1.0.2 © 2019 Sahibdeep Nann')
print('Licensed under BSD-2-Clause, see LICENSE for details')

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
config['infin_version'] = '1.0.2'

bot = commands.Bot(command_prefix='infin ',
                   description='The modular, open-source Discord bot of the future.',
                   activity=discord.Game('infin info'),
                   pm_help=True)
bot.config = config
bot.blacklist = []

@bot.event
async def on_ready():
    """Tells when we're connected to Discord."""
    print('Connected to Discord')


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
        bot.pool = await asyncpg.create_pool(user='infin',
                                             host='localhost',
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
    for module in bot.config['modules']:
        bot.load_extension(module)
        print(f'Loaded module {module}')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_infin())
    loop.close()
