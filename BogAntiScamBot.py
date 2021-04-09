# Requires Python 3.6+ and discord.py 1.4+
import discord
import time
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands

TOKEN = 'ODI5OTEzNDQyOTM2NTUzNTEy.YG_DHw.JrA53uVV9HvzGu0pBUoLRarS964'
intents = discord.Intents.default()
intents.members = True

bot_prefix = "as!"
client = Bot(command_prefix=bot_prefix, intents=intents)


# Notify console bot has started
@client.event
async def on_ready():
    print(f"{client.user.name} started --- {client.user.id}")


# When the bot is mentioned, display the prefix
# This is pretty common practice, why not add it here as well
@client.event
async def on_message(message):
    if message.content == "<@!829913442936553512>" or message.content == "<@829913442936553512>":
        await message.reply(f"My prefix is `{bot_prefix}`")
    await client.process_commands(message)


# If a member that's joining has a username that's on the list of blacklisted names, remove them
@client.event
async def on_member_join(member):
    f = open("usernames.txt", "r")
    usernames = f.read().splitlines()
    for name in usernames:
        if member.name.lower() == name:
            await member.guild.ban(member, reason="User's username matched an entry on the username blacklist.")


# Ping command that can check if the bot is still alive or not
@client.command(name='ping')
async def ping(context):
    before_ping = time.monotonic()
    ping_message = await context.send("Pong!")
    ping_time = (time.monotonic() - before_ping) * 1000
    await ping_message.edit(content=f"Pong! `{int(ping_time)}ms`")


# Command for admins and trusted users to add strings to the user filter
# These users/attributes pass the check:
# Bot owner (DonkeyBlaster#4051), server administrators, users with role "Bogmod", users with role "Bogdev"
@client.command(name='add')
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True), commands.has_any_role('Bogmod', 'Bogdev'))
async def add(context, *, to_add: str = None):
    if to_add is None:
        await context.reply(f"Command usage: `{bot_prefix}add <username>`")
    else:
        # Lower the user's input so it's easier to match later
        to_add = to_add.lower()
        # Simply pass on the username to the file, append it to a new line
        f = open("usernames.txt", "a")
        f.write(f"\n{to_add}")
        f.close()

        # Allow the user to press a reaction to view the current list of usernames
        confirm_msg = await context.reply(f"Added `{to_add}` to the filter list. Click to display current list of filtered usernames.")
        await confirm_msg.add_reaction("\U00002705")

        def reaction_check(reaction, user):
            return user == context.author and str(reaction.emoji) == '✅'

        try:
            await client.wait_for('reaction_add', timeout=20.0, check=reaction_check)
        except asyncio.TimeoutError:
            await confirm_msg.remove_reaction("\U00002705", client.user)
        else:
            f = open("usernames.txt", "r")
            msg = await context.send(f"```f.read()```")
            f.close()
            # Allow the user to press the x button to remove the list
            await msg.add_reaction("\U0000274c")

            def remove_reaction_check(reaction, user):
                return user == context.author and str(reaction.emoji) == '❌'

            try:
                await client.wait_for('reaction_add', timeout=30.0, check=remove_reaction_check)
            except asyncio.TimeoutError:
                await msg.remove_reaction("\U0000274c", client.user)
            else:
                await msg.delete()


# Same thing as command above, see description up there, including permissions
@client.command(name='remove')
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True), commands.has_any_role('Bogmod', 'Bogdev'))
async def remove(context, *, to_remove: str = None):
    if to_remove is None:
        await context.reply(f"Command usage: `{bot_prefix}remove <username>`")
    else:
        # Open up the text file and retrieve all the usernames, throw them into a list
        # There's no better option for this storage format
        f = open("usernames.txt", "r")
        usernames = f.read().splitlines()
        f.close()
        # Iterate through said list and remove lines that match input
        f = open("usernames.txt", "w+")
        for name in usernames:
            if to_remove.lower() != name:
                f.write(name)
        f.close()

        # Allow the user to press a reaction to view the current list of usernames
        confirm_msg = await context.reply(f"Removed instances of `{to_remove}` from the filter list. Click to display current list of filtered usernames.")
        await confirm_msg.add_reaction("\U00002705")

        def reaction_check(reaction, user):
            return user == context.author and str(reaction.emoji) == '✅'

        try:
            await client.wait_for('reaction_add', timeout=20.0, check=reaction_check)
        except asyncio.TimeoutError:
            await confirm_msg.remove_reaction("\U00002705", client.user)
        else:
            f = open("usernames.txt", "r")
            try:
                msg = await context.reply(f"```f.read()```")
                f.close()
                # Allow the user to press the x button to hide the list
                await msg.add_reaction("\U0000274c")

                def reaction_check(reaction, user):
                    return user == context.author and str(reaction.emoji) == '❌'

                try:
                    await client.wait_for('reaction_add', timeout=30.0, check=reaction_check)
                except asyncio.TimeoutError:
                    await msg.remove_reaction("\U0000274c", client.user)
                else:
                    await msg.delete()
            except discord.HTTPException:
                f.close()
                await context.reply(f"The filter list appears to be empty. Try using `{bot_prefix}add <username>` to add a username.")


# Same permissions as commands to add/remove usernames to the blacklist; I assume we don't want people just looking at the list and bypassing immediately
@client.command(name='displaylist', aliases=['list', 'display'])
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True), commands.has_any_role('Bogmod', 'Bogdev'))
async def displaylist(context):
    f = open("usernames.txt", "r")
    try:
        msg = await context.reply(f"```f.read()```")
        f.close()
        # Allow the user to press the x button to hide the list
        await msg.add_reaction("\U0000274c")

        def reaction_check(reaction, user):
            return user == context.author and str(reaction.emoji) == '❌'

        try:
            await client.wait_for('reaction_add', timeout=30.0, check=reaction_check)
        except asyncio.TimeoutError:
            await msg.remove_reaction("\U0000274c", client.user)
        else:
            await msg.delete()
    except discord.HTTPException:
        f.close()
        await context.reply(f"The filter list appears to be empty. Try using `{bot_prefix}add <username>` to add a username.")

client.run(TOKEN)
