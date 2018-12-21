"""This is Infin's voice module.

It is responsible for handling the playback of music on Discord."""
import asyncio
import discord
from discord.ext import commands
import functools
import os
import youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ''
youtube_dl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_opts = {
    'before_options': '-nostdin',
    'options': '-vn'
}
yt = youtube_dl.YoutubeDL(youtube_dl_opts)


class VoicePlayback(discord.PCMVolumeTransformer):
    """A wrapper around discord.FFmpegPCMAudio that allows volume changing."""

    def __init__(self, src, *, data, volume=0.6):
        super().__init__(src, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, video, *, loop=None):
        """Uses youtube_dl to get a direct URL to pass to ffmpeg."""
        loop = loop or asyncio.get_event_loop()
        info = await loop.run_in_executor(None, functools.partial(yt.extract_info, video, download=False))
        url = ''
        if 'entries' in info:
            info = info['entries'][0]
        for format in info['formats']:
            if format['format'] == info['format']:
                url = format['url']
        audio = cls(discord.FFmpegPCMAudio(url, **ffmpeg_opts), data=info)
        return audio


class VoiceEntry:
    def __init__(self, msg, audio):
        self.queuer = msg.author
        self.chan = msg.channel
        self.audio = audio

    def __str__(self):
        duration_minutes = round(self.audio.data['duration'] / 60)
        duration_seconds = self.audio.data['duration'] % 60
        duration = f'{duration_minutes}m{duration_seconds}s'
        queuer_name = self.queuer.nick
        if queuer_name is None:
            queuer_name = self.queuer.name
        entry_string = f"*{self.audio.title}* uploaded by *{self.audio.data['uploader']}*, added by *{queuer_name}* [{duration}]"
        return entry_string.replace('@', '')

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.conn = None
        self.bot = bot
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()
        self.secondary_queue = []
        self.skips = set()
        self.player = self.bot.loop.create_task(self.player_task())

    def skip(self):
        """Clears the skip set and then skips."""
        self.skips.clear()
        if self.conn.is_playing():
            self.conn.stop()

    def toggle_next(self, err):
        """Causes playback of the next song."""
        self.skips.clear()
        self.bot.loop.call_soon_threadsafe(self.next.set)

    async def player_task(self):
        """Detects when next has been set, then plays the next song in the queue."""
        while True:
            self.next.clear()
            self.current = await self.queue.get()
            if self.conn.is_playing():
                self.conn.stop()
            self.skips.clear()
            await self.current.chan.send(f':radio: **Playing**: {str(self.current)}')
            self.conn.play(self.current.audio, after=self.toggle_next)
            self.secondary_queue.remove(str(self.current))
            await self.next.wait()


class VoiceModule:
    def __init__(self, bot):
        self.bot = bot
        self.states = {}

    def retrieve_state(self, guild):
        """Retrieves the given guild's voice state."""
        state = self.states.get(guild.id)
        if state is None:
            state = VoiceState(self.bot)
            self.states[guild.id] = state
        return state

    async def connect(self, chan):
        """Connects to the given voice channel."""
        conn = await chan.connect()
        state = self.retrieve_state(chan.guild)
        state.conn = conn

    def __unload(self):
        for state in self.states.values():
            try:
                state.player.cancel()
                if state.conn:
                    self.bot.loop.create_task(state.conn.disconnect())
            except BaseException:
                pass

    @commands.command(name='summon')
    @commands.guild_only()
    async def summon(self, ctx):
        """Connects to your voice channel."""
        voice_state = ctx.message.author.voice
        if voice_state is None:
             await ctx.message.add_reaction('⛔')
        elif voice_state.channel is None:
             await ctx.message.add_reaction('⛔')
        else:
            try:
                await self.connect(voice_state.channel)
            except BaseException:
                await ctx.message.add_reaction('⛔')
            else:
                await ctx.message.add_reaction('✅')
          
    @commands.command(name='play')
    @commands.guild_only()
    async def play(self, ctx, *, url: str):
        """Enqueues a song based on the given URL."""
        async def start_playback():
            audio = await VoicePlayback.from_url(url)
            entry = VoiceEntry(ctx.message, audio)
            await ctx.send(f':radio: **Enqueued** {str(entry)}')
            await state.queue.put(entry)
            state.secondary_queue.append(str(entry))
        state = self.retrieve_state(ctx.message.guild)
        if state.conn is None:
            voice_state = ctx.message.author.voice
            if voice_state is None:
                 await ctx.message.add_reaction('⛔')
            elif voice_state.channel is None:
                 await ctx.message.add_reaction('⛔')
            else:
                try:
                    await self.connect(voice_state.channel)
                    await start_playback()
                except BaseException:
                    await ctx.message.add_reaction('⛔')
        else:
            await start_playback()

    @commands.command(name='volume')
    @commands.guild_only()
    async def volume(self, ctx, *, value: int):
        """Changes the volume of the bot."""
        state = self.retrieve_state(ctx.message.guild)
        if state.conn.is_playing():
            conn = state.conn
            old_volume = conn.source.volume
            new_volume = value / 100
            if value > 500:
                await ctx.send(f':no_good: Maximum volume is **500**%')
            else:
                conn.source.volume = value / 100
                volume_difference = round((new_volume - old_volume) * 100, 1)
                await ctx.send(f':radio: Set volume to **{round(value, 1)}**% [{volume_difference}% change]')

    @commands.command(name='pause')
    @commands.guild_only()
    async def pause(self, ctx):
        """Pauses playback of the song."""
        state = self.retrieve_state(ctx.message.guild)
        if state.conn.is_playing():
            conn = state.conn
            conn.pause()
            await ctx.message.add_reaction('✅')

    @commands.command(name='resume')
    @commands.guild_only()
    async def resume(self, ctx):
        """Resumes playback of the song."""
        if ctx.voice_client:
            ctx.voice_client.resume()
            await ctx.message.add_reaction('✅')

    @commands.command(name='stop')
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops playing music, then leaves the channel."""
        state = self.retrieve_state(ctx.message.guild)
        if state.conn.is_playing():
            state.conn.stop()
        try:
            state.player.cancel()
            del self.states[ctx.message.guild.id]
            await state.conn.disconnect()
            await ctx.message.add_reaction('✅')
        except BaseException:
            pass

    @commands.command(name='forceskip')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def forceskip(self, ctx):
        """Force skips the song if the user has enough permissions."""
        state = self.retrieve_state(ctx.message.guild)
        if not state.conn.is_playing():
            await ctx.message.add_reaction('⛔')
        else:
            await ctx.send(':radio: **Force skipping** song')
            state.skip()

    @commands.command(name='skip')
    @commands.guild_only()
    async def skip(self, ctx):
        """Skips the song if there are 3 votes, or if the queuer wants to."""
        state = self.retrieve_state(ctx.message.guild)
        if not state.conn.is_playing():
            await ctx.message.add_reaction('⛔')
        else:
            voter = ctx.message.author
            if voter == state.current.queuer:
                await ctx.send(':radio: **Skipping** song')
                state.skip()
            elif voter.id not in state.skips:
                state.skips.add(voter.id)
                votes = len(state.skips)
                if votes >= 3:
                    await ctx.send(':radio: **Skipping** song')
                    state.skip()
                else:
                    await ctx.send(f':radio: **Vote** passed [{votes}/3]')
            else:
                await ctx.message.add_reaction('⛔')

    @commands.command(name='playing')
    @commands.guild_only()
    async def playing(self, ctx):
        """Displays information about the currently playing song."""
        state = self.retrieve_state(ctx.message.guild)
        if state.current is None:
            await ctx.message.add_reaction('⛔')
        else:
            votes = len(state.skips)
            await ctx.send(f':radio: **Playing** {str(state.current)} [skips {votes}/3]')

    @commands.command(name='queue')
    @commands.guild_only()
    async def queue(self, ctx):
        """Displays all voice entries in the queue."""
        state = self.retrieve_state(ctx.message.guild)
        if state.current is None:
            await ctx.message.add_reaction('⛔')
        else:
            queue_message = f'**Now playing**: {str(state.current)}\n'
            current_position = 0
            for current_entry in state.secondary_queue:
                current_position = current_position + 1
                queue_message = f'{queue_message}**{current_position}**: {str(current_entry)}\n'
            await ctx.send(queue_message)


def setup(bot):
    """Required for proper addition of the module to Infin."""
    bot.add_cog(VoiceModule(bot))
