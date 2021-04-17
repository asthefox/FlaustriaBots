import discord
from discord.ext import commands
import token_loader

class PersonalityTestCog(commands.Cog):
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

    @commands.command(name="question")
    async def question(self, ctx):
      await self.ask_question(ctx.channel)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
      if reaction.count > 1:
        response = f'answer: {reaction.emoji}'
        await reaction.message.channel.send(response)
        await self.ask_question(reaction.message.channel)

    async def ask_question(self, channel):
      question = "What's the answer to the question?\n🐔 - chickens\n🐍 - snakes"
      answers = ['🐍', '🐔']
      msg = await channel.send(question)
      for answer in answers:
        await msg.add_reaction(emoji=answer)


def setup(bot):
    bot.add_cog(PersonalityTestCog(bot))