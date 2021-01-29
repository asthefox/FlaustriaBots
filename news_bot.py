import discord,random,asyncio,os
import flaustrian_headlines
from datetime import datetime
from discord.ext import commands

bot=commands.Bot(command_prefix='!')

send_time='12:00' #time is in 24hr format
message_channel_id='' #channel ID to send images to

file_name='some_file.txt' #replace with the name of your file with extension

if os.path.isfile(file_name):
		with open(file_name, "r") as f:
			message_list = f.read()
			message_list = message_list.strip().split("\n")

@bot.event
async def on_ready():
	print(bot.user.name)
	print(bot.user.id)

async def time_check():
	await bot.wait_until_ready()
	message_channel=bot.get_channel(message_channel_id)
	while not bot.is_closed:
		now=datetime.strftime(datetime.now(),'%H:%M')
		if now == send_time:
			message= random.choice(message_list)
			await bot.send_message(message_channel,message)
			time=90
		else:
			time=1
		await asyncio.sleep(time)

bot.loop.create_task(time_check())

bot.run('TOKEN')