import discord
import csv
import database
from discord.ext import commands
from discord.utils import find

class KeySender(commands.Cog):

  EAGLE_TYPE_ROLE = 832324674967830558
  DEBUG_ROLE = 840747216603447346
  DEBUG = False

  def __init__(self, bot):
      self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
      print('KeySender Cog Ready!')

  """
  @commands.command(name="list_eagles")
  async def admin_list_eagles(self, ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Sorry, only admins can perform this function.")
        return
    role = ctx.guild.get_role(KeySender.DEBUG_ROLE if KeySender.DEBUG else KeySender.EAGLE_TYPE_ROLE)
    if role == None:
      await ctx.send("The correct role could not be found.")
      return
    with open("user_invites.csv", "w", newline="") as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow(["Discord ID", "Member Name", "Key"])
      for member in role.members:
        writer.writerow([str(member.id), member.display_name, "-"])
      #member_list = str(len(role.member)) + " Members:\n"
      #member_list += "\n".join([member.id for member in role.members])
      await ctx.send("User list output.")
  """

  """
  @commands.command(name="mass_send_invites")
  async def admin_send_invites(self, ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Sorry, only admins can perform this function.")
        return

    with open("user_invites.csv", "r", newline="") as csvfile:
      reader = csv.reader(csvfile)
      header = next(reader) # skip header row
      for row in reader:
        id, name, code = row
        id = int(id)
        member = find(lambda m: m.id == id, ctx.guild.members)
        try:
          message = f"Good day! As you may have seen, Discord has disabled their games service, so the **Astronaut: The Best Alpha** is moving to Steam. The Discord will still be the place for discussion, feedback, and announcements! But to actually play the alpha, you'll need to redeem this key.\n\nYour Steam key is: **{code}**\n\nTo redeem, choose \"Activate a Product on Steam\" from the Games menu in the top bar of the Steam client.\n\nAs a reminder, I am a bot. If you need help or have questions, please ask in the <#832357355056267364>. Thanks for being a part of the **Astronaut: The Best Alpha**!"
          dm = await member.create_dm()
          await dm.send(message)
        except:
          print(f"Member {str(id)} ({name}) could not be sent a code. Please try to send the code manually.")
  """

  @commands.command(name="alpha_welcome")
  async def invite_to_alpha(self, ctx, member_name):
    if not ctx.author.guild_permissions.administrator:
      await ctx.send("Sorry, only admins can send alpha invites.")
      return
    member = ctx.guild.get_member_named(member_name)
    if member == None:
      await ctx.send("A Flaustrian named " + member_name + " cannot be found.")
      return

    ## GIVE ROLE
    try:
      role = ctx.guild.get_role(KeySender.DEBUG_ROLE if KeySender.DEBUG else KeySender.EAGLE_TYPE_ROLE)
      await member.add_roles(role)
    except BaseException as err:
      await ctx.send(f"Error: The Flaustrian {member_name} could not be given the role of Eagle-Type Person. {err}")
      return

    ## READ NEW KEY
    try:
      unused_keys = database.get("alpha_keys/unused")
      next_key = unused_keys[0]
      code = next_key.strip()
      updated_key_list = unused_keys[1:]

    except BaseException as err:
      await ctx.send(f"Error: Could not find any unused invites in database. Please replenish invite list. {err}")
      return

    ## SEND KEY
    try:
      message = f"Congratulations! As an Eagle-Type Person, you now have access to the **Astronaut: The Best Alpha**!\n\nHere is your Steam key: **{code}**\n\nTo play the Alpha, choose \"Activate a Product on Steam\" from the Games menu in the top bar of the Steam client, and enter that key.\n\nYou have also been granted access to the Alpha Command Center channels on our Discord.  If you need help or have questions, please ask in the <#832357355056267364>. Thanks for being a part of the **Astronaut: The Best Alpha**!"
      dm = await member.create_dm()
      await dm.send(message)

    except BaseException as err:
      await ctx.send(f"Error: Could not send a DM with the updated information.  Please open your DMs to this Welcome Inquisitor, or request help from a dev.")
      return

    ## UPDATE DATABASE
    try:
      used_key_data = {
        "id": member.id,
        "name": member.display_name,
        "key": code
      }
      database.set(f"alpha_keys/used/{code}", used_key_data)
      database.set("alpha_keys/unused", updated_key_list)
    except BaseException as err:
      await ctx.send(f"Error: Could not update database with information about new key. The devs will have to look into this one. {err}")
      return

  """
  @commands.command(name="init_db")
  async def init_db(self, ctx):
    if not ctx.author.guild_permissions.administrator:
      await ctx.send("Sorry, only admins can reinitialize DB.")
      return

    database.set("alpha_keys/unused", ["AAA", "BBB", "CCC"])
    database.set("alpha_keys/used", [])
    print("DB Initialized!")
  """

def setup(bot):
    bot.add_cog(KeySender(bot))



