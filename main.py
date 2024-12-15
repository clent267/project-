import discord
from discord.ext import commands
from discord import app_commands

# Replace with your bot token
BOT_TOKEN = "MTIwNzUxODQxOTI1MTg5NjM2MA.Gefba4.obPDrlvhJJVx-GARg_ue-yCkxmHTaVl190C6ms"
OWNER_ID =  1195424202480697465 # Replace with your Discord User ID
NEW_CHANNEL_NAME = "bot-commands"  # Name of the new channel to create

# Configure intents for the bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Needed to read message content

# Initialize the bot with both prefix and slash commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Store the config channel ID after setup
config_channel_id = 1302582439595737119

@bot.event
async def on_ready():
    """Triggered when the bot is ready."""
    await bot.tree.sync()  # Sync slash commands with Discord
    print(f"Logged in as {bot.user}. Ready to send announcements and set up channels!")

# ---------------------- Helper Function ----------------------

async def send_announcement_to_all_guilds(message: str):
    """Send an announcement to the first available text channel in every guild."""
    for guild in bot.guilds:
        # Find the first text channel where the bot has send permission
        channel = next(
            (ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages),
            None,
        )

        if channel:
            try:
                await channel.send(f"📢 **Announcement:** {message}")
                print(f"Sent announcement to {guild.name} in #{channel.name}.")
            except Forbidden:
                print(f"Missing permissions in {guild.name}.")
        else:
            print(f"No valid channel in {guild.name} to send announcement.")

# ---------------------- Prefix Commands ----------------------

@bot.command()
async def setup(ctx):
    """Create a new 'hits' channel and webhook."""
    guild = ctx.guild

    # Check if 'hits' channel exists
    existing_channel = discord.utils.get(guild.channels, name=NEW_CHANNEL_NAME)
    if existing_channel:
        await ctx.send(f"Channel '{NEW_CHANNEL_NAME}' already exists.")
        return

    # Create 'hits' channel
    new_channel = await guild.create_text_channel(NEW_CHANNEL_NAME)
    await ctx.send(f"Created channel: {new_channel.mention}")

    try:
        # Create webhook in the 'hits' channel
        webhook = await new_channel.create_webhook(name="InfoWebhook")
        print(f"Webhook created: {webhook.url}")

        # Send embed with webhook URL and channel ID in the 'hits' channel
        embed = discord.Embed(title=f"Webhook Info for <#{new_channel.id}>", color=discord.Color.blue())
        embed.add_field(name="Webhook URL", value=f"```{webhook.url}```", inline=False)
        embed.add_field(name="Channel ID", value=f"{new_channel.id}", inline=False)
        embed.set_footer(text="Use this webhook to interact with the channel.")
        await new_channel.send(embed=embed)

        await ctx.send(f"Webhook created.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to create webhooks in that channel.")
    except discord.HTTPException as e:
        await ctx.send(f"Error creating webhook: {str(e)}")

@bot.command()
async def announcement(ctx, *, message: str):
    """Send an announcement to all servers (prefix command)."""
    if ctx.author.id != OWNER_ID:
        await ctx.send("You do not have permission to use this command.")
        return

    if config_channel_id != ctx.channel.id:
        await ctx.send("This command can only be used in the configured setup channel.")
        return

    await ctx.send("Sending announcement to all servers...")
    await send_announcement_to_all_guilds(message)
    await ctx.send("Announcement sent to all servers.")

# ---------------------- Slash Commands ----------------------

@bot.tree.command(name="announcement", description="Send announcement to all servers.")
async def slash_announcement(interaction: discord.Interaction, message: str):
    """Send an announcement to all servers (slash command)."""
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    if config_channel_id != interaction.channel.id:
        await interaction.response.send_message("This command can only be used in the configured setup channel.", ephemeral=True)
        return

    await interaction.response.send_message("Sending announcement to all servers...")
    await send_announcement_to_all_guilds(message)
    await interaction.followup.send("Announcement sent to all servers.")

# ---------------------- Run the Bot ----------------------

# Run the bot
bot.run(BOT_TOKEN)
