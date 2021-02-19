import os
from random import randint
import re
import discord
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()
# Get Variables from the .env file
token = os.getenv('DISCORD_TOKEN')
logfile = os.getenv('LOG_FILE')

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(filename=logfile, encoding='utf-8', mode='w', maxBytes=1048576, backupCount=20)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    guild = message.channel.guild
    channel = message.channel
    content = message.content
    guild_id = message.channel.guild.id
    discord_id = message.author.id
    username = message.author.mention

    if content == "/help":
        msg = "Bot usage:\n"
        msg += "\tRoll Wizard - Roll the a number of 10 side dice and provided results base on Diff. Default Difficulty is 6.\n"
        msg += "\t\t/rw #[NUMBER_OF_DICE] [OPTIONS]\n"
        msg += "\t\tOptions:\n"
        msg += "\t\t\tdiff[DIFFICULTY] - Change the Default Difficulty of 6 to something else\n"
        msg += "\t\t\tdif[DIFFICULTY] - Change the Default Difficulty of 6 to something else (One F version)\n"
        msg += "\t\t\tspec - Sepcialization effects roll causing 10s to be double Successes\n"
        msg += "\t\t\tno1 - Set the system to not subtract ones\n"
        msg += "\t\t\t| [Comment] - Anything after the | is added as a comment\n"
        msg += "\tExample:\n"
        msg += "\t\t/rw #5 - Roll Five dice with a Difficulty 6\n"
        msg += "\t\t/rw #5 diff6 - Roll Five dice with a Difficulty 6\n"
        msg += "\t\t/rw #5 diff6 spec - Roll Five dice with a Difficulty 6 with Specializations\n"
        msg += "\t\t/rw #5 diff6 no1 - Roll Five dice with a Difficulty 6 but don't subtracted 1s\n"
        await channel.send(msg)
    elif content.startswith("/rw "):
        msg = standard_roll(channel=channel,username=username,content=content)
        await channel.send(content=msg,allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False))

def standard_roll(channel=None,username=None,content=None):
    successes=0
    reroll = 0
    rolls = []
    num_of_dice = 0
    difficulty = 6
    # modifier = 0 
    specialization = False
    specialization_msg = ""
    ones_msg = ""
    no_botch=False
    possible_botch=False
    count_ones=True
    comment=None

    m = re.search("#(?P<dice>\d+)",content, re.IGNORECASE)
    if m:
        num_of_dice = int(m.group('dice'))

    m = re.search("dif(f|)(?P<dif>\d+)",content, re.IGNORECASE)
    if m:
        difficulty = int(m.group('dif'))

    m = re.search("#(?P<mod>[+-]\d+)",content, re.IGNORECASE)
    if m:
        num_of_dice = int(m.group('dice'))
    m = re.search("#(?P<mod>[+-]\d+)",content, re.IGNORECASE)
    if m:
        num_of_dice = int(m.group('dice'))
    if re.search(" spec(\s|$)", content) is not None:
        specialization = True
        specialization_msg = " with specilizations"
    if re.search(" no1", content) is not None:
        count_ones = False
        ones_msg = " with ones not subtracted"
    m = re.search("(?P<comment>\|.*$)",content, re.IGNORECASE)
    if m:
        comment = m.group('comment')

    for x in range(0, num_of_dice):
        y = randint(1, 10)
        if specialization and y == 10:
            successes += 1
        if (y >= difficulty):
            successes += 1
            no_botch=True
            rolls.append("**{0}**".format(y))
        elif (y == 1) and count_ones:
            successes -= 1
            rolls.append(str(y))
            possible_botch=True
        else: 
            rolls.append("~~{0}~~".format(y))

    if successes < 0:
        successes = 0;

    list_of_rolls = ", ".join(rolls)
    if successes < 1 and not no_botch and possible_botch:
        msg = "{username} got **Botched**".format(username=username)
    else:
        msg = "{username} got **{successes}** successes".format(username=username,successes=successes)
    if comment:
        msg += " {comment}".format(comment=comment)
    msg += "\n{dice} dice at difficulty {diff}{spec}{ones}. Rolls: {rolls}".format(dice=num_of_dice,diff=difficulty,spec=specialization_msg,ones=ones_msg,rolls=list_of_rolls)

    return msg


client.run(token)