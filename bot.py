import discord
import asyncio
import random
import re
from discord.ext import commands
from datetime import datetime, timedelta
from colorama import Fore, Style
from discord.ui import *
from discord.ext.commands import has_permissions
from pytz import timezone


token = ''  

# apposto di ! Mettere il prefisso
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)


GUILD_ID = 123 #Server ID
TICKET_CHANNEL = 123 #Where the bot should send the Embed + SelectMenu

CATEGORY_ID1 = 123 #Support1 Channel
CATEGORY_ID2 = 123 #Support2 Channel

TEAM_ROLE1 = 123 #Permissions for Support1
TEAM_ROLE2 = 123 #Permissions for Support2

LOG_CHANNEL = 123 #Log Channel


# Comandi

# Giveaway Command
@bot.command(aliases=['start', 'g'])
@commands.has_permissions(manage_guild=True)
async def giveaway(ctx):
    await ctx.send("Seleziona il canale in cui vorresti avviare il giveaway.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg1 = await bot.wait_for('message', check=check, timeout=30.0)

        channel_converter = discord.ext.commands.TextChannelConverter()
        try:
            giveawaychannel = await channel_converter.convert(ctx, msg1.content)
        except commands.BadArgument:
            return await ctx.send("Questo canale non esiste, riprova.")

    except asyncio.TimeoutError:
        await ctx.send("Ci hai messo troppo tempo, per favore riprova!")

    if not giveawaychannel.permissions_for(ctx.guild.me).send_messages or not giveawaychannel.permissions_for(
            ctx.guild.me).add_reactions:
        return await ctx.send(
            f"Il bot non dispone delle autorizzazioni per inviare messaggi in quel canale: {giveawaychannel}\n **Permessi richiesti:** ``Add reactions | Send messages.``")

    await ctx.send("Quanti vincitori vorresti per il giveaway?")
    try:
        msg2 = await bot.wait_for('message', check=check, timeout=30.0)
        try:
            winerscount = int(msg2.content)
        except ValueError:
            return await ctx.send("Non hai specificato un numero di vincitori, riprova.")

    except asyncio.TimeoutError:
        await ctx.send("Ci hai messo troppo tempo, per favore riprova!")

    await ctx.send("Seleziona un periodo di tempo per il giveaway.")
    try:
        since = await bot.wait_for('message', check=check, timeout=30.0)

    except asyncio.TimeoutError:
        await ctx.send("Ci hai messo troppo tempo, per favore riprova!")

    seconds = ("s", "sec", "secs", 'second', "seconds")
    minutes = ("m", "min", "mins", "minute", "minutes")
    hours = ("h", "hour", "hours")
    days = ("d", "day", "days")
    weeks = ("w", "week", "weeks")
    rawsince = since.content

    try:
        temp = re.compile("([0-9]+)([a-zA-Z]+)")
        if not temp.match(since.content):
            return await ctx.send("Non hai specificato un'unità di tempo, riprova.")
        res = temp.match(since.content).groups()
        time = int(res[0])
        since = res[1]

    except ValueError:
        return await ctx.send("Non hai specificato un'unità di tempo, riprov")
    if since.lower() in seconds:
        timewait = time
    elif since.lower() in minutes:
        timewait = time * 60
    elif since.lower() in hours:
        timewait = time * 3600
    elif since.lower() in days:
        timewait = time * 86400
    elif since.lower() in weeks:
        timewait = time * 604800
    else:

        return await ctx.send("Non hai specificato un'unità di tempo, riprova.")

    await ctx.send("Quale vorresti fosse il premio?")
    try:
        msg4 = await bot.wait_for('message', check=check, timeout=30.0)

    except asyncio.TimeoutError:
        await ctx.send("Ci hai messo troppo tempo, per favore riprova.")

    logembed = discord.Embed(title="Giveaway Logged",
                             description=f"**Prize:** ``{msg4.content}``\n**Winners:** ``{winerscount}``\n**Channel:** {giveawaychannel.mention}\n**Host:** {ctx.author.mention}",
                             color=discord.Color.red())
    logembed.set_thumbnail(url=ctx.author.avatar_url)

    logchannel = ctx.guild.get_channel(609431364445405194)  # Put your channel, you would like to send giveaway logs to.
    await logchannel.send(embed=logembed)

    futuredate = datetime.utcnow() + timedelta(seconds=timewait)
    embed1 = discord.Embed(color=discord.Color(random.randint(0x000000, 0xFFFFFF)),
                           title=f"🎉GIVEAWAY🎉\n`{msg4.content}`", timestamp=futuredate,
                           description=f'React with 🎉 to enter!\nHosted by: {ctx.author.mention}')
#vincyxirt#1098

    embed1.set_footer(text=f"Giveaway will end")
    msg = await giveawaychannel.send(embed=embed1)
    await msg.add_reaction("🎉")
    await asyncio.sleep(timewait)
    message = await giveawaychannel.fetch_message(msg.id)
    for reaction in message.reactions:
        if str(reaction.emoji) == "🎉":
            users = await reaction.users().flatten()
            if len(users) == 1:
                return await msg.edit(embed=discord.Embed(title="Nessuno ha vinto il giveaway."))
    try:
        winners = random.sample([user for user in users if not user.bot], k=winerscount)
    except ValueError:
        return await giveawaychannel.send("not enough participants")
    winnerstosend = "\n".join([winner.mention for winner in winners])

    win = await msg.edit(embed=discord.Embed(title="WINNER",
                                             description=f"Congratulazioni {winnerstosend}, hai vinto **{msg4.content}**!",
                                             color=discord.Color.blue()))


# Reroll command
@bot.command()
@commands.has_permissions(manage_guild=True)
async def reroll(ctx):
    async for message in ctx.channel.history(limit=100, oldest_first=False):
        if message.author.id == bot.user.id and message.embeds:
            reroll = await ctx.fetch_message(message.id)
            users = await reroll.reactions[0].users().flatten()
            users.pop(users.index(bot.user))
            winner = random.choice(users)
            await ctx.send(f"Il nuovo vincitore è {winner.mention}")
            break
    else:
        await ctx.send("Nessun giveaway in corso su questo canale.")


@bot.command()
async def ping(ctx):
    ping = bot.latency
    await ctx.send(f"The bot's ping is: ``{round(ping * 1000)}ms``!")


#Ticket command





#fine ban unban

# Eventi
@bot.event
async def on_ready():
    print(Fore.RED + 'Logged in as')
    print(Fore.GREEN + bot.user.name)
    print(Style.RESET_ALL)
    bot.add_view(MyView())
    bot.add_view(delete())
    members = 0
    for guild in bot.guilds:
        members += guild.member_count - 1

    await bot.change_presence(activity = discord.Activity(
        type = discord.ActivityType.watching,

        #Bot status
        name = f'{members} members' 

    ))
    print('Ready to support ✅')


@bot.event
async def on_message(message):
    bad_words = ["fuck", "arschloch", "https://discord.gg", "http://disord.gg", "discord.gg", "fick", "arsch", "Arschgesicht", "arschgesicht", "Arschloch", "Asshole", "asshole", "Fotze", "fotze", "Miststück", "miststück", "Bitch", "bitch", "Schlampe", "schlampe", "Sheisse", "sheisse", "Shit", "shit", "Fick", "huren", "Verpiss", "verpiss", "masturbiert", "Idiot", "idiot", "depp", "Depp", "Dumm", "dumm", "jude", "Bastard", "bastard", "Wichser", "wichser", "wixxer", "Wixxer", "Hurensohn" "Wixer", "Pisser", "Arschgesicht", "huso", "hure", "Hure", "verreck" "Verreck", "fehlgeburt", "Fehlgeburt", "ficken", "adhs", "ADHS", "Btch", "faggot", "fck", "f4ck", "nigga", "Nutted", "flaschengeburt", "penis", "pusse", "pusse", "pussy", "pussys", "nigger", "kacke", "fuucker"]
    for word in bad_words:
        if message.content.count(word) > 0:
            await message.channel.purge(limit=1)
            await message.channel.send(f"Stai usando parole non consentite, perfavore smettila! {message.author.mention}")


bot.run(token)
