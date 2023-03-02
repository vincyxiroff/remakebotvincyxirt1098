import discord
import asyncio
import random
import re
from discord.ext import commands
from datetime import datetime, timedelta
from colorama import Fore, Style
from discord_components import Button, Select, SelectOption, ComponentsBot, interaction
from discord_components.component import ButtonStyle

# per Installare discord_components eseguire pip install --upgrade discord-components

token = ''  

# apposto di ! Mettere il prefisso
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
bot.remove_command('help')

id_category = #inserisci qui l'id della categoria dove il bot creerà i canali ticket
id_channel_ticket_logs = #inserisci qui l'id del canale dove il bot creerà i log dei ticket
id_staff_role = #inserire qui l'id del ruolo staff
embed_color = 0xfcd005 #metti qui un colore esadecimale che conterrà tutti gli embed inviati dal bot



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
@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    await ctx.message.delete()

    #Embed title and description
    embed = discord.Embed(title ='Tickets', description ='Welcome to tickets system.', color=embed_color) 

    #Embed image
    embed.set_image(url='https://i.imgur.com/FoI5ITb.png')

    await ctx.send(
        embed = embed,

        #Embed button
        components = [
            Button(
                custom_id = 'Ticket',
                label = "Crea un ticket",
                style = ButtonStyle.green,
                emoji ='🔧')
        ]
    )


@bot.event
async def on_button_click(interaction):

    canal = interaction.channel
    canal_logs = interaction.guild.get_channel(id_channel_ticket_logs)

    #Select function
    if interaction.component.custom_id == "Ticket":
        await interaction.send(

            components = [
                Select(
                    placeholder = "Come possiamo aiutarti?",
                    options = [
                        SelectOption(label="Question", value="question", description='Se hai una semplice domanda.', emoji='❔'),
                        SelectOption(label="Help", value="help", description='Se hai bisogno di aiuto da noi.', emoji='🔧'),
                        SelectOption(label="Report", value="Buy", description='per comprare qualcosa.', emoji='🛒'),
                    ],
                    custom_id = "menu")])

    #Call staff function
    elif interaction.component.custom_id == 'call_staff':

        embed_llamar_staff = discord.Embed(description=f"🔔 {interaction.author.mention} ha chiamato il personale.", color=embed_color)
        await canal.send(f'<@&{id_staff_role}>', embed=embed_llamar_staff, delete_after= 20)

    #Close ticket function
    elif interaction.component.custom_id == 'close_ticket':

        embed_cerrar_ticket = discord.Embed(description=f"⚠️ Sei sicuro di voler chiudere il ticket?", color=embed_color)
        await canal.send(interaction.author.mention, embed=embed_cerrar_ticket, 
                        components = [[
                        Button(custom_id = 'close_yes', label = "Yes", style = ButtonStyle.green),
                        Button(custom_id = 'close_no', label = "No", style = ButtonStyle.red)]])

    #Ticket logs function
    elif interaction.component.custom_id == 'close_yes':

        await canal.delete()
        embed_logs = discord.Embed(title="Tickets", description=f"", timestamp = datetime.datetime.utcnow(), color=embed_color)
        embed_logs.add_field(name="Ticket", value=f"{canal.name}", inline=True)
        embed_logs.add_field(name="Closed by", value=f"{interaction.author.mention}", inline=False)
        embed_logs.set_thumbnail(url=interaction.author.avatar_url)
        await canal_logs.send(embed=embed_logs)


    elif interaction.component.custom_id == 'close_no':
        await interaction.message.delete()

@bot.event
async def on_select_option(interaction):
    if interaction.component.custom_id == "menu":

        guild = interaction.guild
        category = discord.utils.get(interaction.guild.categories, id = id_category)
        rol_staff = discord.utils.get(interaction.guild.roles, id = id_staff_role)

        #Select option | Question
        if interaction.values[0] == 'question':

            #Creating ticket channel | Question
            channel = await guild.create_text_channel(name=f'❔┃{interaction.author.name}-ticket', category=category)
            
            #Ticket channel permissions | Question
            await channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                            send_messages=False,
                            read_messages=False)
            await channel.set_permissions(interaction.author, 
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True)
            await channel.set_permissions(rol_staff,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True,
                                                manage_messages=True)
                                                

            await interaction.send(f'> Il {channel.mention} canale è stato creato per risolvere le tue domande.', delete_after= 3)

            #Inside the ticket | Question
            #Embed inside the ticket | Question
            embed_question = discord.Embed(title=f'Question - ¡Ciao {interaction.author.name}!', description='In questo ticket abbiamo una risposta alla tua domanda.\n\nSe non riesci a farti aiutare da qualcuno, premi il pulsante `🔔 Chiama lo staff`..', color=embed_color)
            embed_question.set_thumbnail(url=interaction.author.avatar_url)


            await channel.send(interaction.author.mention, embed=embed_question,
            
            #Embed buttons inside the ticket | Question
             components = [[
                    Button(custom_id = 'close_ticket', label = "Chiudi il ticket", style = ButtonStyle.red, emoji ='🔐'),
                    Button(custom_id = 'call_staff', label = "Chiama lo staff", style = ButtonStyle.blue, emoji ='🔔')]])


        #Select option | Help
        elif interaction.values[0] == 'help':

            #Creating ticket channel | Help
            channel = await guild.create_text_channel(name=f'🔧┃{interaction.author.name}-ticket', category=category)
            
            #Ticket channel permissions | Help
            await channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                            send_messages=False,
                            read_messages=False)
            await channel.set_permissions(interaction.author, 
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True)
            await channel.set_permissions(rol_staff,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True,
                                                manage_messages=True)


            await interaction.send(f'> il {channel.mention} canale è stato creato per aiutarti.', delete_after= 3)

            #Inside the ticket | Help
            #Embed inside the ticket | Help
            embed_question = discord.Embed(title=f'Help - ¡Ciao {interaction.author.name}!', description='In questo ticket possiamo aiutarti con tutto ciò di cui hai bisogno.\n\nSe non puoi farti aiutare da qualcuno, premi il pulsante `🔔 Chiama lo staff`.', color=embed_color)
            embed_question.set_thumbnail(url=interaction.author.avatar_url)


            await channel.send(interaction.author.mention, embed=embed_question, 
            
            #Embed buttons inside the ticket | Help
            components = [[
                    Button(custom_id = 'close_ticket', label = "Chiudi il ticket", style = ButtonStyle.red, emoji ='🔐'),
                    Button(custom_id = 'call_staff', label = "Chiama lo staff", style = ButtonStyle.blue, emoji ='🔔')]])


        #Select option | Report
        elif interaction.values[0] == 'report':

            #Creating ticket channel | Report
            channel = await guild.create_text_channel(name=f'🚫┃{interaction.author.name}-ticket', category=category)

            #Ticket channel permissions | Report
            await channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                            send_messages=False,
                            read_messages=False)
            await channel.set_permissions(interaction.author, 
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True)
            await channel.set_permissions(rol_staff,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True,
                                                manage_messages=True)


            await interaction.send(f'> il {channel.mention} canale è stato creato per acquistare qualcosa.', delete_after= 3)

            #Inside the ticket | Report
            #Embed inside the ticket | Report
            embed_question = discord.Embed(title=f'Buy - ¡Hi {interaction.author.name}!', description='In questo ticket possiamo aiutarti con il tuo acquisto.\n\nIf you cant get someone to help you, press the button `🔔 Chiama lo staff`.', color=embed_color)
            embed_question.set_thumbnail(url=interaction.author.avatar_url)

            await channel.send(interaction.author.mention, embed=embed_question, 
            
            #Embed buttons inside the ticket | Report
            components = [[
                    Button(custom_id = 'close_ticket', label = "Chiudi il ticket", style = ButtonStyle.red, emoji ='🔐'),
                    Button(custom_id = 'call_staff', label = "Chiama lo staff", style = ButtonStyle.blue, emoji ='🔔')]])

#fine ticket

# Eventi
@bot.event
async def on_ready():
    print(Fore.RED + 'Logged in as')
    print(Fore.GREEN + bot.user.name)
    print(Style.RESET_ALL)
    members = 0
    for guild in bot.guilds:
        members += guild.member_count - 1

    await bot.change_presence(activity = discord.Activity(
        type = discord.ActivityType.watching,

        #Bot status
        name = f'{members} members' 

    ))
    print('Ready to support ✅')





bot.run(token)
