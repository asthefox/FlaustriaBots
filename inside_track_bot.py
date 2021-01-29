import discord
from discord.ext import commands
import token_loader
import random

class InsideTrackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_token = token_loader.GUILD

    @commands.Cog.listener()
    async def on_ready(self):
        guild = discord.utils.find(lambda g: g.name == self.guild_token, self.bot.guilds)
        if guild:
            print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
        else:
            print(f"Can't connect to guild:{self.guild_token}")

    @commands.Cog.listener()
    async def on_message(self,message):
        inside_track_command = '!profit' in message.content.lower()

        if message.author == self.bot.user or not inside_track_command: 
            return
        
        #examined = 'market' in message.content.lower()
        response = 'some thing about money, space cat! dig money? you know i do!'
        await message.channel.send(response)



def setup(bot):
    bot.add_cog(InsideTrackCog(bot))