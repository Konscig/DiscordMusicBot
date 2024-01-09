import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(f"""
```
Bot commands:
/help - displays all the available commands
/play <keywords/URL> - finds the song on youtube and plays it
/skip - skips the current song being played
/pause - pauses the song being played or resumes if already paused
/resume - resumes playing the current song
/queue - displays the current music queue
/remove - removes last song from the queue
/clear - clears the queue
/leave - disconnected the bot from the voice channel
```
""")
