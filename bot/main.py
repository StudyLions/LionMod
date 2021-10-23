from discord import Intents
from cmdClient.cmdClient import cmdClient

from config import Conf
from logger import log


# ----------------------------------------------------------------------------
# Initialise config
# ----------------------------------------------------------------------------
conf = Conf("config/bot.conf")
prefix = conf['prefix']
owners = conf.bot.getintlist('owners')
moderators = set(conf.bot.getintlist('moderators'))


# ----------------------------------------------------------------------------
# Initialise client
# ----------------------------------------------------------------------------
intents = Intents.all()
client = cmdClient(prefix=conf.bot['prefix'], owners=owners, intents=intents)
client.conf = conf
client.log = log


# ----------------------------------------------------------------------------
# Utils
# ----------------------------------------------------------------------------
def is_moderator(ctx):
    return ctx.author.id in moderators


# ----------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------
@client.cmd("networkban",
            aliases=('nban', 'gban'))
async def cmd_networkban(ctx):
    ...


# ----------------------------------------------------------------------------
# Setup done, log and execute!
# ----------------------------------------------------------------------------
client.log("Initial setup complete, logging in", context='SETUP')
client.run(conf['TOKEN'])
