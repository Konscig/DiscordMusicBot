import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["рудз"], help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(f"""
```
Bot commands:
/help - displays all the available commands
/play <keywords for Youtube || Yandex/Youtube URL> - finds the song and plays it
/skip - skips the current song being played
/pause - pauses the song being played or resumes if already paused
/resume - resumes playing the current song
/queue|list - displays the current music queue
/remove (number) - removes #number song from the queue
/clear - clears the queue
/leave - disconnected the bot from the voice channel
```
""")
