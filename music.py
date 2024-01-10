import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import asyncio

bot = commands.Bot(command_prefix=['/', '.'],
                   activity=discord.Streaming(name=":3", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
                   intents=discord.Intents.all())


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.queue = []
        self.vc = None  # !!!!
        self.ffmpeg_opt = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                           'options': '-vn'}
        self.ydl_opt = {'format': "bestaudio/best",
                        'source_address': '0.0.0.0',
                        'noplaylist': 'True',
                        'cookiefile': 'cookies.txt'}
        self.ydl = YoutubeDL(self.ydl_opt)

    def search_yt(self, req):
        if req.startswith("https://"):
            title = self.ydl.extract_info(req, download=False)["title"]
            return {'source': req, 'title': title}
        search = VideosSearch(req, limit=1)
        if search.result()["result"]:
            return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}
        else:
            return False

    async def play_next(self):
        if len(self.queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.queue[0][0]['source']

            # remove the first element as you are currently playing it
            self.queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ydl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.ffmpeg_opt),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.queue) > 0:
            self.is_playing = True

            m_url = self.queue[0][0]['source']
            # try to connect to voice channel if you are not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.queue[0][1].connect()

                # in case we fail to connect
                if self.vc is None:
                    await ctx.send("```Could not connect to the voice channel```")
                    return
            else:
                await self.vc.move_to(self.queue[0][1])
            # remove the first element as you are currently playing it
            self.queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ydl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.ffmpeg_opt),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))

        else:
            self.is_playing = False

    @bot.command(name="play", aliases=["p", "playing", "з", "здфн"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("```❌ You are not in voice channel!```")
            return
        if self.is_paused:
            await self.resume(ctx)
            await self.play(ctx, query)
        else:
            if "playlist?list" in query:
                await ctx.send("```❌ I can't work with playlists!```")
                return
            song = self.search_yt(query)
            if not song:
                await ctx.send("```❌ Incorrect format!```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.queue) + 2} '{song['title']}'** added to the queue")
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")
                self.queue.append([song, voice_channel])
                if self.is_playing is False:
                    await self.play_music(ctx)

    @bot.command(name="pause", aliases=["зфгыу"], help="Pauses the current song being played")
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
        await ctx.send("```⏸️ Paused```")

    @bot.command(name="resume", aliases=["r", "куыгьу", "continue", "unpause"], help="Resumes playing")
    async def resume(self, ctx):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
        await ctx.send("```▶️ Resumed```")

    @bot.command(name="skip", aliases=["s", "ылшз", "ы"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            self.vc.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)
            await ctx.send("```⏭️ Skipped```")

    @bot.command(name="queue", aliases=["q", "й", "йгугу"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.queue)):
            retval += f"{i + 1}. " + self.queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @bot.command(name="clear", aliases=["c", "сдуфк"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if not self.queue:
            await ctx.send("```✅ Queue is already empty```")
        else:
            self.queue = []
            await ctx.send("```✅ Queue cleared```")

    @bot.command(name="leave", aliases=["disconnect", "l", "d", "дуфму"], help="Kick the bot from VC")
    async def leave(self, ctx):
        if self.vc:
            self.is_playing = False
            self.is_paused = False
            self.clear(ctx)
            await ctx.send("```💔```")
            await self.vc.disconnect()

    @bot.command(name="remove", aliases=["re", "ку", "куьщму"], help="Removes last song added to queue")
    async def remove(self, ctx):
        self.queue.pop()
        await ctx.send("```✅ Last song removed```")
