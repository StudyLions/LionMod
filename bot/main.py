import asyncio
import discord
import datetime
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
log_channel = conf.bot.getint('log_channel')


# ----------------------------------------------------------------------------
# Initialise client
# ----------------------------------------------------------------------------
intents = discord.Intents.all()
client = cmdClient(prefix=conf.bot['prefix'], owners=owners, intents=intents)
client.conf = conf
client.log = log


# ----------------------------------------------------------------------------
# Utils
# ----------------------------------------------------------------------------
def is_moderator(ctx):
    return ctx.author.id in moderators or ctx.author.id in owners


# ----------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------
@client.cmd("networkban",
            aliases=('nban', 'gban'))
async def cmd_networkban(ctx):
    # Ignore if the user isn't a permitted moderator
    if not is_moderator(ctx):
        return

    # Parse the provided users
    splits = (userid.strip('<@> ') for userid in ctx.args.split(','))
    splits = [split for split in splits if split]

    if not splits or not all(split.isdigit() for split in splits):
        return await ctx.error_reply(
            "**Usage:** `{}nban userid1, userid2, userid3, ...`".format(prefix)
        )
    if len(splits) > 10:
        return await ctx.error_reply(
            "Maximum 10 users at a time please!"
        )

    # Ensure that these users actually exist
    userids = list(set(int(split) for split in splits))
    users = []
    for userid in userids:
        try:
            user = ctx.client.get_user(userid)
            if not user:
                user = await ctx.client.fetch_user(userid)
            users.append(user)
        except discord.NotFound:
            return await ctx.error_reply(
                "Couldn't find the user `{}` on Discord at all! No users were banned.".format(userid)
            )

    # Collect the reason
    reason = None
    files = []
    if ctx.msg.attachments:
        files = [await attachment.to_file() for attachment in ctx.msg.attachments]
    else:
        # Request the reason and justification
        out_msg = await ctx.reply(
            "Please enter the global ban reason, and upload justifying screenshot(s) as evidence:"
        )

        def check(msg):
            valid = msg.author == ctx.author
            valid = valid and msg.channel == ctx.ch
            valid = valid and msg.attachments
            return valid
        try:
            message = await ctx.client.wait_for('message', check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.error_reply(
                "Timed out waiting for the reason. No users were banned."
            )
        finally:
            try:
                await out_msg.delete()
            except discord.HTTPException:
                pass

        reason = message.content
        files = [await attachment.to_file() for attachment in message.attachments]

        try:
            await message.delete()
        except discord.HTTPException:
            pass

    audit_reason = "Network ban by {}{}".format(
        ctx.author.id,
        ': {}'.format(reason if len(reason) < 128 else reason[:125] + '...') if reason else ''
    )

    # Execute the ban
    progress_msg = await ctx.reply(
        embed=discord.Embed(
            description="Banning {} from all network servers, please wait...".format(
                users[0].mention if len(users) == 1 else '`{}` users'.format(len(users))
            )
        )
    )
    ctx.client.log(
        "Executing network ban by '{}' (uid: {}) of the following users: {}".format(
            ctx.author.name,
            ctx.author.id,
            ', '.join(str(user.id) for user in users)
        ),
        context="NETWORK_BAN"
    )
    notes = []
    for guild in ctx.client.guilds:
        try:
            for user in users:
                await guild.ban(user, delete_message_days=0, reason=audit_reason)
        except discord.Forbidden:
            notes.append("Insufficient permissions to ban from **{}** (`{}`).".format(guild.name, guild.id))
        except discord.HTTPException:
            notes.append("Unknown error while banning from **{}** (`{}`).".format(guild.name, guild.id))

    try:
        await progress_msg.edit(
            embed=discord.Embed(description="Network ban complete!", colour=discord.Colour.green())
        )
    except discord.HTTPException:
        pass

    # Post to the log
    embed = discord.Embed(
        title="Network ban",
        colour=discord.Colour.red(),
        timestamp=datetime.datetime.utcnow()
    )
    if reason:
        embed.description = reason
    embed.add_field(
        name="Target{}".format('s' if len(users) > 1 else ''),
        value='\n'.join(user.mention for user in users)
    )
    embed.add_field(
        name="Moderator",
        value=ctx.author.mention
    )
    if notes:
        embed.add_field(
            name="Notes",
            value='\n'.join(notes),
            inline=False
        )

    channel = ctx.client.get_channel(log_channel)
    if len(files) > 1:
        await channel.send(
            embed=embed,
            files=files
        )
    else:
        embed.set_image(url="attachment://{}".format(files[0].filename))
        await channel.send(
            embed=embed,
            file=files[0]
        )


# ----------------------------------------------------------------------------
# Setup done, log and execute!
# ----------------------------------------------------------------------------
client.log("Initial setup complete, logging in", context='SETUP')
client.run(conf['TOKEN'])
