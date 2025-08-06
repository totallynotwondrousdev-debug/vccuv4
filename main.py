import discord
import time
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

OWNER_ROLE_ID = 1325562102303424615
GUILD_ID = 1325560414422962298
blacklisted_users = set()
start_time = time.time()

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    # Only sync if not already synced
    if not hasattr(bot, 'synced'):
        await tree.sync(guild=guild)
        bot.synced = True
        print(f"✅ Synced slash commands to guild {GUILD_ID}")

    print(f"✅ Bot is alive as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Voltage Car Club"))

@bot.event
async def on_member_join(member):
    if member.id in blacklisted_users:
        try:
            await member.send("You are blacklisted from this server.")
        except:
            pass
        await member.ban(reason="Blacklisted")

# No @guilds(...) here — just define once
@tree.command(name="info", description="Get server info for Voltage Car Club")
async def info_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📌 Voltage Car Club Info",
        color=discord.Color.blue()
    )
    embed.add_field(name="Server Name", value="Voltage Car Club | Meets | Races", inline=False)
    embed.add_field(name="Join Code", value="VOLTAGE", inline=False)
    embed.add_field(name="Owner", value="Wonderman987654", inline=False)
    embed.add_field(name="Co-owners", value="22alien44, KoolraxOfficial", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ping", description="Check the bot's latency")
async def ping_command(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! {latency}ms")

@tree.command(name="uptime", description="Show how long the bot has been online")
async def uptime_command(interaction: discord.Interaction):
    elapsed = time.time() - start_time
    hours, rem = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(rem, 60)
    await interaction.response.send_message(f"⏱️ Uptime: {hours}h {minutes}m {seconds}s")

@tree.command(name="blacklist", description="Blacklist a user from the server")
async def blacklist_command(interaction: discord.Interaction, user: discord.User):
    member = interaction.guild.get_member(interaction.user.id)
    if not member or not any(role.id == OWNER_ROLE_ID for role in member.roles):
        return await interaction.response.send_message("❌ You don’t have permission to use this command.", ephemeral=True)

    blacklisted_users.add(user.id)
    try:
        await user.send("❌ You have been blacklisted from Voltage Car Club.")
    except:
        pass

    target = interaction.guild.get_member(user.id)
    if target:
        await target.ban(reason="Blacklisted")
    await interaction.response.send_message(f"🔒 User {user} has been blacklisted.")

@tree.command(name="unblacklist", description="Unblacklist a user and allow them to rejoin")
async def unblacklist_command(interaction: discord.Interaction, user: discord.User):
    member = interaction.guild.get_member(interaction.user.id)
    if not member or not any(role.id == OWNER_ROLE_ID for role in member.roles):
        return await interaction.response.send_message("❌ You don’t have permission to use this command.", ephemeral=True)

    if user.id in blacklisted_users:
        blacklisted_users.remove(user.id)
        try:
            await interaction.guild.unban(user, reason="Unblacklisted")
        except:
            pass
        try:
            await user.send("✅ You have been unblacklisted! You may now rejoin. Invite: https://discord.gg/xwrfKxrDRX")
        except:
            pass
        await interaction.response.send_message(f"✅ User {user} has been unblacklisted.")
    else:
        await interaction.response.send_message("⚠️ That user is not blacklisted.")

bot.run(os.getenv("DISCORD_TOKEN"))
