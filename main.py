import discord
from dotenv import load_dotenv
import os
import logging
import sys
import getlatest
import getvnc
from datetime import datetime, timedelta
load_dotenv()

version = "2.0"

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True
# Configure logging
out_stream_handler = logging.StreamHandler(sys.stdout)
out_stream_handler.setLevel(logging.DEBUG)
out_stream_handler.addFilter(lambda record: record.levelno <= logging.INFO)
err_stream_handler = logging.StreamHandler(sys.stderr)
err_stream_handler.setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s', handlers=[out_stream_handler, err_stream_handler])
logging.info("logging configured")

client = discord.Client(intents=intents)
@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')

# On Message
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author.bot:
        return

    if message.content.startswith(".debug-stop"):
        if message.author.id == 557899982238122000:
            logging.info("stopping the bot")
            await message.channel.send("Stopping bot")
            try:
                logging.info("closing discord bot")
                await client.close()
            except Exception:
                pass
            exit()
        else:
            logging.warning(f"Unauthorized user {message.author.display_name} tried to restart the bpt")
            return

    if message.content.startswith(".help"):
        logging.info(f"processing request for help {message.author.display_name}")
        embed = discord.Embed(title="Help", color=0x00ff00,description="Made by Proton0 and Rabbit R[eborn]", url="https://discord.gg/RbFpvs2ArY")
        embed.set_author(name="RabbitTools", icon_url="https://i.postimg.cc/GtBr3JW4/IMG-5068.jpg",
                         url="https://discord.gg/RbFpvs2ArY")
        embed.set_footer(text=f"Version {version}")
        embed.add_field(name=".ota", value="Gets the latest OTA from Rabbit", inline=False)
        embed.add_field(name=".vnc [type]", value="Generates a VNC instance. Valid types are: midjourney, spotify, uber, doordash", inline=False)
        await message.channel.send(embed=embed)
        logging.info("Processed request for help")

    if message.content.startswith(".talk"):
        logging.info(f"processing request for talk {message.author.display_name}")
        message_content = message.content.split(" ", 1)
        if len(message_content) > 1:
            logging.info(f"message is {message_content}")
            await message.reply("Processing. Please wait")
            try:
                response = talk.sendMessage(message_content)
                if not response:
                    await message.reply("Failed to get response from Rabbit. Try again later")
                    logging.error("failed to get talk")
                    return
                else:
                    await message.reply(response)
                    logging.info("sent response")
            except Exception as e:
                await message.reply("Failed to get response from Rabbit. Try again later")
                logging.error(e)
        else:
            await message.reply("No message provided. Usage : .talk [message]")


    if message.content.startswith(".ota"):
        logging.info(f"processing request for latest ota {message.author.display_name}")
        await message.reply("Getting latest OTA. Please wait")
        ota = getlatest.getLatestOTA()
        if ota == False:
            logging.error("Failed to get latest OTA")
            await message.reply("Failed to get latest OTA. Try again later")
        else:
            logging.info("creating update embed")
            embed = discord.Embed(title="Latest OTA", description="Successfully fetched the latest OTA", color=0x00ff00, url=ota["url"])
            embed.set_author(name="RabbitTools", icon_url="https://i.postimg.cc/GtBr3JW4/IMG-5068.jpg",
                               url="https://discord.gg/RbFpvs2ArY")
            embed.add_field(name="Version", value=ota["version"], inline=False)
            embed.add_field(name="Name", value=ota["name"], inline=True)
            embed.add_field(name="Update URL", value=ota["url"], inline=False)
            embed.add_field(name="Update Info", value=ota["info"], inline=True)
            streaming = False

            if "property_files" in ota:
                logging.info("update is streaming")
                streaming = True

            embed.add_field(name="Streaming", value=streaming, inline=False)

            if streaming:
                update = discord.Embed(title="Streaming information", color=0x00ff00)
                for file in ota["property_files"]:
                    logging.info(f"add {file['filename']}")
                    mb = round(file['size'] / (1024 * 1024), 2)
                    update.add_field(name=file["filename"], value=f"{mb} MB\n{file['size']} bytes\nOffset: {file['offset']}", inline=True)
                    logging.info("made field")
                await message.channel.send(embed=embed)
                await message.channel.send(embed=update)
            else:
                await message.channel.send(embed=embed)
            logging.info("sent")

    if message.content.startswith('.vnc'):
        logging.info(f"processing request for vnc {message.author.display_name}")
        vnc_type = message.content.split(" ")
        if len(vnc_type) > 1:
            if vnc_type[1].lower() == "midjourney":
                vnc_type = "midjourney"
            elif vnc_type[1].lower() == "spotify" or vnc_type[1].lower() == "music":
                vnc_type = "spotify"
            elif vnc_type[1].lower() == "uber" or vnc_type[1].lower() == "ride share":
                vnc_type = "uber"
            elif vnc_type[1].lower() == "doordash" or vnc_type[1].lower() == "food":
                vnc_type = "doorDash"
            else:
                logging.info(f"user selected invalid vnc type {vnc_type[1]}")
                await message.reply(f"Invalid VNC type {vnc_type[1]}. Valid types are: midjourney, spotify, uber, doordash\nDefaulting to midjourney vnc")
                vnc_type = "midjourney"
        else:
            logging.info("defaulting to midjourney vnc")
            vnc_type = "midjourney"
        await message.reply("Getting VNC. Please wait")
        vnc = getvnc.getVNC(vnc_type)
        if vnc == False:
            logging.error("Failed to get VNC")
            await message.reply("Failed to get VNC. Try again later")
        elif vnc == "timeout-vnc":
            await message.reply("Connection timeout while waiting for rabbit to send the VNC URL. Try again later!")
        else:
            logging.info("getting expiration date")
            now = datetime.utcnow()
            expiration = now + timedelta(minutes=5)
            expiration_str = expiration.strftime("%Y-%m-%d %H:%M:%S")
            logging.info("creating embed")
            embed = discord.Embed(title=f"VNC for {message.author.display_name}", description="Successfully generated a VNC Instance\nNote that this VNC **expires** after 5 minutes!", color=0x00ff00, url=vnc)
            embed.add_field(name="VNC URL", value=vnc, inline=False)
            embed.add_field(name="VNC Type", value=vnc_type, inline=False)
            embed.add_field(name="Expiration date (UTC-0)", value=expiration, inline=True)
            embed.set_author(name="RabbitTools", icon_url="https://i.postimg.cc/GtBr3JW4/IMG-5068.jpg", url="https://discord.gg/RbFpvs2ArY")
            await message.channel.send(embed=embed)
            logging.info("sent")
            logging.info(f"processed request for vnc {message.author.display_name}")

client.run(os.getenv("BOT_TOKEN"))