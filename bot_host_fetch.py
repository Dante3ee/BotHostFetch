import discord
from discord.ext import commands
import json
from Rasp_System_Info import get_system_info
import subprocess
import asyncio

#config 
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

command_Prefix = "host."  #you could change it if you want (the shown prefix in the commands will also be changed)
bot = commands.Bot(command_prefix=command_Prefix, intents=intents,  help_command=None)

embed_color = discord.Color.blurple() #you can change the embed color here (the color on the left of the embed)
ownership_protection = True           #default is True, can be changed with the command  

#for the interactive embed
class SysInfoView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

#REFRESH THE INFOs
    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.blurple)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        #ownership check
        if interaction.user.id != self.ctx.author.id and ownership_protection==True:
            return await interaction.response.send_message(
                "You don't own the bot", ephemeral=True
            )

        info = get_system_info()
        embed = discord.Embed(
            title="System infos - Raspberry Pi",
            color=embed_color
        )

        for k, v in info.items():
            embed.add_field(name=k, value=str(v), inline=False)

        embed.set_footer(text="BotHostFetch - Managing your bot hosting Raspberry Pi")
        await interaction.response.edit_message(embed=embed, view=self)

#UPDATE THE RASP
    @discord.ui.button(label="Update System", style=discord.ButtonStyle.green)
    async def update_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id and ownership_protection==True:
            return await interaction.response.send_message("You don't own this bot.", ephemeral=True)

        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Updating system...", ephemeral=True)

        try:
            process = await asyncio.create_subprocess_shell(
                "sudo apt update && sudo apt upgrade -y",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            result = stdout.decode()[-1500:] if stdout else stderr.decode()[-1500:]
            await interaction.followup.send(f"Update completed:\n```\n{result}\n```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error while updating: {e}", ephemeral=True)
        finally:
            button.disabled = False
            await interaction.edit_original_response(view=self)

#REBOOT THE RASP
    @discord.ui.button(label="Reboot", style=discord.ButtonStyle.red)
    async def reboot_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id and ownership_protection==True:
            return await interaction.response.send_message("Unfortnunately You don't own this bot.", ephemeral=True)

        await interaction.response.send_message("Rebooting...", ephemeral=True)
        await asyncio.sleep(2)
        subprocess.Popen(["sudo", "reboot"])


@bot.event
async def on_ready():
    print(f"UP {bot.user} ({bot.user.id})")
    await bot.change_presence(activity=discord.Game(f"BotHostFetch! {command_Prefix}help"))


@bot.command()
async def fetch(ctx):
    if ctx.author.id != config["owner_id"] and ownership_protection==True:
        return await ctx.send("You don't own this bot.")
    info = get_system_info()

    embed = discord.Embed(
        title="Full Fetch - Raspberry Pi",
        color=embed_color)

    for k, v in info.items():
        embed.add_field(name=k, value=str(v), inline=False)

    embed.set_footer(text="BotHostFetch - Raspberry Monitor")

    view = SysInfoView(ctx)
    await ctx.send(embed=embed, view=view)


@bot.command()
async def network(ctx):
    if ctx.author.id != config["owner_id"] and ownership_protection==True:
        return await ctx.send("You don't own this bot.")
    
    info = get_system_info()
    subset = {k: info[k] for k in ["Hostname", "Local IP", "Public IP"]}

    embed = discord.Embed(title="Network Information", color=embed_color)
    for k, v in subset.items():
        embed.add_field(name=k, value=str(v), inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def status(ctx):
    if ctx.author.id != config["owner_id"] and ownership_protection==True:
        return await ctx.send("You don't own this bot.")
    
    info = get_system_info()
    subset = {k: info[k] for k in ["CPU Usage", "CPU Freq", "Temperature", "Power/Throttling", "RAM", "Disk", "Uptime"]}

    embed = discord.Embed(title="System Information", color=embed_color)
    for k, v in subset.items():
        embed.add_field(name=k, value=str(v), inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def toggle_protection(ctx):
    if ctx.author.id != config["owner_id"]:
        return await ctx.send("You don't own this bot.")
    global ownership_protection
    ownership_protection = not ownership_protection
    status = "enabled" if ownership_protection else "disabled"
    await ctx.send(f"Ownership protection is now {status}.")


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="BotHostFetch Help",
        description="Available commands:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="YOU MUST OWN THE BOT TO USE THESE COMMANDS", value="", inline=False)
    embed.add_field(name=f"{command_Prefix}fetch", value="Get full system information with interactive buttons.", inline=False)
    embed.add_field(name=f"{command_Prefix}network", value="Get network-related information.", inline=False)
    embed.add_field(name=f"{command_Prefix}status", value="Get system status information.", inline=False)
    embed.add_field(name=f"{command_Prefix}help", value="Display this help message.", inline=False)
    embed.add_field(name=f"{command_Prefix}toggle_protection", value="Change the ownership protection.", inline=False)
    embed.set_footer(text="BotHostFetch - Managing your bot hosting Raspberry Pi")
    await ctx.send(embed=embed)

bot.run(config["token"])
