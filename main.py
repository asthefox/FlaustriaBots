#test discord bot script

#import modules and setup
import os
from dotenv import load_dotenv
import random
import discord
from discord.ext import commands
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix='!')


#event handlers
@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    if guild:
        print(
            f"{bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})"
        )
        print_guild_members(guild)
    else:
        print(f"Can't connect to guild:{GUILD}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    examined = 'philosophy' in message.content.lower()
    response = 'The unexamined life is not worth living.' if examined else get_random_response(
        message.author)
    await message.channel.send(response)


#helper functions
def get_random_response(interlocutor):
    responses = [
        'Surely!', 'Certainly!', 'Of course!',
        'How could it be any other way?', f'Yes, {interlocutor}.',
        f'Your mind is a marvel, {interlocutor}!'
    ]
    return random.choice(responses)


def print_guild_members(guild):
    members_len = len(guild.members)
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members ({members_len}):\n - {members}')


keep_alive()
bot.run(TOKEN)

#this is something David is adding to test version control
print("david is testing version control")