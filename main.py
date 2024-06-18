import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
import sys
import getlatest
import getvnc
import time
from datetime import datetime, timedelta
import patch
import imei

start_time = datetime.utcnow()
total_errors = 0
processed_commands = 0
load_dotenv()

version = "2.3.0_mini-2_dev1"
debug = True
# Configure logging
out_stream_handler = logging.StreamHandler(sys.stdout)
out_stream_handler.setLevel(logging.DEBUG)
out_stream_handler.addFilter(lambda record: record.levelno <= logging.INFO)
err_stream_handler = logging.StreamHandler(sys.stderr)
err_stream_handler.setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s",
    handlers=[out_stream_handler, err_stream_handler],
)
logging.info("logging configured")

# Configure the bot
logging.info("configure bot")


# Unhandled Exception Handler
def handle_exception(exc_type, exc_value, exc_traceback):
    global total_errors
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    total_errors += 1
    user = client.fetch_user(int(os.getenv("DEVELOPER_ID")))

    embed = discord.Embed(
        title="Uncatched Exception",
        description=f"Non-discord.py exception: {exc_type} {exc_value}",
        color=0xFF0000,
    )

    embed.add_field(name="Traceback", value=f"```{exc_traceback}```")
    embed.add_field(name="Error", value=str(exc_value))

    user.send(embed=embed)
    logging.info("send dev errorlog")

    exit(1) # PM2 will restart the bot


sys.excepthook = handle_exception


class botclient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.synced = False

    async def on_command_error(self, ctx: commands.Context, error):
        total_errors += 1
        logging.error(f"Error processing command: {type(error)} {error}, {error.__traceback__}")

        # send to dev
        user = await client.fetch_user(os.getenv("DEVELOPER_ID"))

        embed = discord.Embed(
            title="Uncatched Exception",
            description=f"Error processing command: {type(error)} {error}",
            color=0xFF0000,
        )
        embed.add_field(name="Command", value=ctx.command.name)
        embed.add_field(name="Author", value=ctx.author.display_name)
        embed.add_field(name="Channel", value=ctx.channel.name)
        embed.add_field(name="Guild", value=ctx.guild.name)
        embed.add_field(name="Error", value=str(error))
        embed.add_field(name="Traceback", value=f"```{error.__traceback__}```")
        await user.send(embed=embed)
        logging.info("send dev errorlog")




    async def on_ready(self):
        await self.wait_until_ready()
        logging.info(f"Logged in as {self.user}")
        if not self.synced:
            await tree.sync()
            self.synced = True
        self.synced = True
        logging.info("synced commands")


client = botclient()
tree = app_commands.CommandTree(client)


#@tree.command(name="patch", description="Patches the R1 apk and sends it to you") # NOT YET ON PROD
async def patch_command(interaction: discord.Interaction):
    global total_errors, processed_commands
    logging.info(f"patch request from {interaction.user.display_name}")
    await interaction.response.send_message("Patching the Launcher. Please wait")
    patch_result = patch.patch(interaction.user.id)
    if patch_result is False:
        logging.error("Failed to patch launcher")
        await interaction.edit_original_response(
            content="Failed to patch the Launcher. Try again later"
        )
        total_errors += 1
    else:
        logging.info("patched successfully")
        await interaction.edit_original_response(
            content="Launcher patched. Uploading to MediaFire"
        )
        logging.info("sent")
        time.sleep(2)
        await interaction.edit_original_response(
            content="Failed to upload to MediaFire. Try again later"
        )
        total_errors += 1


@tree.command(name="r1_imei", description="Generates a random IMEI or validates an IMEI")
async def imeicheck(interaction: discord.Interaction, imei_input: str = None):
    global total_errors, processed_commands
    logging.info(f"imeicheck request for {interaction.user.display_name}")
    if imei_input is None:
        logging.info("No IMEI provided")
        imei_a = imei.generate_imei()
        await interaction.response.send_message(f"Generated IMEI: {imei_a}")
    else:
        logging.info("IMEI provided")
        if len(imei_input) < 5:
            await interaction.response.send_message(f"IMEI {imei_input} is invalid.")
            return
        try:
            int(imei_input)
        except ValueError:
            await interaction.response.send_message(f"IMEI {imei_input} is invalid.")
            return
        except Exception as e:
            logging.error(e)
            await interaction.response.send_message(f"Error processing request")
            total_errors += 1
        result = imei.validate_imei(imei_input)
        if result:
            logging.info("valid IMEI")
            await interaction.response.send_message(f"IMEI {imei_input} is valid.")
        else:
            logging.info("invalid IMEI")
            await interaction.response.send_message(f"IMEI {imei_input} is invalid.")
    processed_commands += 1


@tree.command(name="vnc", description="Gets a VNC URL from Rabbit")
@app_commands.describe(service="Choose the service")
@app_commands.choices(service=[
    app_commands.Choice(name="Midjourney", value="midjourney"),
    app_commands.Choice(name="Spotify", value="spotify"),
    app_commands.Choice(name="Apple Music", value="appleMusic"),
    app_commands.Choice(name="Uber", value="uber"),
    app_commands.Choice(name="DoorDash", value="doorDash")
])
async def vnc(interaction: discord.Interaction, service: app_commands.Choice[str]):
    global total_errors, processed_commands
    vnc_type = service.value

    await interaction.response.send_message("Getting VNC. Please wait")
    vnc_url = getvnc.getVNC(vnc_type)

    if vnc_url is False:
        logging.error("Failed to get VNC")
        await interaction.edit_original_response(
            content="Failed to get VNC. Try again later"
        )
        total_errors += 1
        return
    elif vnc_url == "timeout-vnc":
        await interaction.edit_original_response(
            content="Connection timeout while waiting for Rabbit to send the VNC URL. Try again later!"
        )
        total_errors += 1
        return
    else:
        logging.info("Getting expiration date")
        now = datetime.utcnow()
        expiration = now + timedelta(minutes=5)
        expiration_str = expiration.strftime("%Y-%m-%d %H:%M:%S")
        logging.info("Creating embed")
        embed = discord.Embed(
            title=f"VNC for {interaction.user.display_name}",
            description="Successfully generated a VNC instance\nNote that this VNC **expires** after 5 minutes!",
            color=0x00FF00,
            url=vnc_url,
        )
        embed.add_field(name="VNC URL", value=vnc_url, inline=False)
        embed.add_field(name="VNC Type", value=vnc_type, inline=False)
        embed.add_field(name="Expiration date (UTC-0)", value=expiration_str, inline=True)
        embed.set_author(
            name="RabbitTools",
            icon_url="https://i.postimg.cc/GtBr3JW4/IMG-5068.jpg",
            url="https://discord.gg/RbFpvs2ArY",
        )
        await interaction.edit_original_response(content="", embed=embed)
        logging.info("sent")
        logging.info(f"Processed request for VNC from {interaction.user.display_name}")
        processed_commands += 1


@tree.command(name="ota", description="Gets the latest OTA update information")
async def getlatestotacommand(interaction: discord.Interaction):
    global total_errors, processed_commands
    logging.info(f"Processing request for latest OTA from {interaction.user.display_name}")
    await interaction.response.send_message("Getting latest OTA. Please wait")
    ota = getlatest.getLatestOTA()
    if ota is False:
        logging.error("Failed to get latest OTA")
        await interaction.edit_original_response(
            content="Failed to get latest OTA. Try again later"
        )
        total_errors += 1
        return
    else:
        logging.info("Creating update embed")
        embed = discord.Embed(
            title="Latest OTA",
            description="Successfully fetched the latest OTA",
            color=0x00FF00,
            url=ota["url"],
        )
        embed.set_author(
            name="RabbitTools",
            icon_url="https://i.postimg.cc/GtBr3JW4/IMG-5068.jpg",
            url="https://discord.gg/RbFpvs2ArY",
        )
        embed.add_field(name="Version", value=ota["version"], inline=False)
        embed.add_field(name="Name", value=ota["name"], inline=True)
        embed.add_field(name="Update URL", value=ota["url"], inline=False)
        embed.add_field(name="Update Info", value=ota["info"], inline=True)
        streaming = False

        if "property_files" in ota:
            logging.info("Update is streaming")
            streaming = True

        embed.add_field(name="Streaming", value=streaming, inline=False)

        if streaming:
            update_embed = discord.Embed(title="Streaming Information", color=0x00FF00)
            for file in ota["property_files"]:
                logging.info(f"Adding {file['filename']}")
                mb = round(file["size"] / (1024 * 1024), 2)
                update_embed.add_field(
                    name=file["filename"],
                    value=f"{mb} MB\n{file['size']} bytes\nOffset: {file['offset']}",
                    inline=True,
                )
                logging.info("Field added")
            await interaction.channel.send(embed=embed)
            await interaction.channel.send(embed=update_embed)
        else:
            await interaction.channel.send(embed=embed)
        await interaction.edit_original_response(content="Got the latest OTA")
        logging.info("Sent")
        processed_commands += 1


@tree.command(name="help", description="Displays help information")
async def help_command(interaction: discord.Interaction):
    global total_errors, processed_commands
    logging.info(f"Processing request for help from {interaction.user.display_name}")
    embed = discord.Embed(
        title="Help",
        color=0x00FF00,
        description="Made by Proton0 and Rabbit R[eborn]",
        url="https://discord.gg/RbFpvs2ArY",
    )
    embed.set_author(
        name="RabbitTools",
        icon_url="https://i.postimg.cc/GtBr3JW4/IMG-5068.jpg",
        url="https://discord.gg/RbFpvs2ArY",
    )

    embed.add_field(name="/ota", value="Gets the latest OTA from Rabbit", inline=False)
    embed.add_field(name="/vnc [type]",
                    value="Generates a VNC instance. Valid types are: midjourney, spotify, uber, doordash",
                    inline=False)
    embed.add_field(name="/r1_imei [imei]", value="Validates or generates an IMEI", inline=False)
    #embed.add_field(name="/patch", value="Patches the Launcher then sends it to you", inline=False)

    if not debug:
        embed.set_footer(text=f"Version {version}")
    else:
        embed.set_footer(text=f"This version is a development build. Bugs will occur ({version})")
    await interaction.response.send_message(embed=embed)
    logging.info("Processed request for help")
    processed_commands += 1


@client.event
async def on_message(message):
    global total_errors, processed_commands
    if message.author == client.user:
        print("return")
        return
    if int(message.author.id) != int(os.getenv("DEVELOPER_ID")):
        logging.warning(
            f"Unauthorized user {message.author.display_name} with an ID of {message.author.id} tried to access dev commands")
        return
    if message.content == "..dev_stats":
        logging.info("Processing dev stats request")

        # Create embed
        embed = discord.Embed(
            title="Bot data",
            color=0x00FF00,
            description="Bot data",
            url="https://discord.gg/RbFpvs2ArY",
        )

        # Set footer
        if not debug:
            embed.set_footer(text=f"Version {version}")
        else:
            embed.set_footer(text=f"This version is a development build. Bugs will occur ({version})")

        # Add fields
        embed.add_field(name="Bot uptime", value=str(datetime.utcnow() - start_time), inline=False)
        embed.add_field(name="Bot latency", value=f"{round(client.latency * 1000)}ms", inline=False)
        embed.add_field(name="Errors", value=total_errors, inline=False)
        embed.add_field(name="Commands Processed", value=processed_commands, inline=False)

        # Send embed
        await message.channel.send(embed=embed)
        processed_commands += 1


client.run(os.getenv("BOT_TOKEN"))
