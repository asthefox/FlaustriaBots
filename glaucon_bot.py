import discord
from discord.ext import commands
import token_loader
import random

class GlauconCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_token = token_loader.GUILD

    @commands.Cog.listener()
    async def on_ready(self):
        guild = discord.utils.find(lambda g: g.name == self.guild_token, self.bot.guilds)
        if guild:
            print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
            self.print_guild_members(guild)
        else:
            print(f"Can't connect to guild:{self.guild_token}")

    @commands.Cog.listener()
    async def on_message(self,message):
        glaucon_command = '!glaucon' in message.content.lower()

        if message.author == self.bot.user or not glaucon_command: 
            return
        
        examined = 'philosophy' in message.content.lower()
        response = 'The unexamined life is not worth living.' if examined else self.get_random_response(message.author)
        await message.channel.send(response)

    def print_guild_members(self,guild):
        members_len = len(guild.members)
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members ({members_len}):\n - {members}')

    def get_random_response(self,interlocutor):
        responses = [
            'Surely!', 'Certainly!', 'Of course!',
            'How could it be any other way?', f'Yes, {interlocutor}.',
            f'Your mind is a marvel, {interlocutor}!'
        ]
        return random.choice(responses)
    

def setup(bot):
    bot.add_cog(GlauconCog(bot))