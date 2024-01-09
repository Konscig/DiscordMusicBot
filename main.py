from music import MusicCog
from help import HelpCog
import discord, asyncio, os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
bot = commands.Bot(command_prefix=['/', '.'],
                   activity=discord.Streaming(name=":3", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
                   intents=discord.Intents.all())
bot.remove_command('help')


async def main():
    async with bot:
        await bot.add_cog(MusicCog(bot))
        await bot.add_cog(HelpCog(bot))
        await bot.start(os.getenv('TOKEN'))


asyncio.run(main())
