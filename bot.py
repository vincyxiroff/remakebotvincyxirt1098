import io
import discord
import yaml
import chat_exporter
from discord import Button, ActionRow, ButtonStyle, app_commands
from discord.ext import commands
from discord.utils import get
from utils import remove_command_message, check_permissions
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
config = yaml.safe_load(open("ticketsConfig.yml", 'r', encoding="utf-8"))



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

class Tickets(commands.Cog):
    """Class containing all methods for this module"""
    def __init__(self, bot):
        self.bot = bot
        db.check_create_table("tickets", "id INT AUTO_INCREMENT PRIMARY KEY, ticket_channel_id VARCHAR(64),"
                                         " ticket_category VARCHAR(255), creator_id VARCHAR(64),"
                                         " is_closed BOOLEAN, creation_date DATE")
        print('Tickets module ready!')

    @commands.hybrid_command(name="ticketsgen", with_app_command=True,
                             description="Creates new embed used for ticket creation")
    async def ticketsgen(self, ctx):
        """Handles the -ticketsgen command and creation of new ticket generator."""
        role_identificator = config.get("ticket-creation-admin-role")
        if await check_permissions(ctx.author, role_identificator):
            await self.create_generator(ctx)
            await remove_command_message(ctx.message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        """Full button handling, for ticket creation, closing etc."""
        channel = interaction.channel
        custom_id = interaction.data.get("custom_id")
        if custom_id is None:
            return
        # --- Button is for closing ticket ---
        # Without confirmation
        if custom_id == "tickets_close_ticket":
            if config.get("require-close-confirmation") is True:
                await self.confirm_close_ticket(interaction)
            else:
                await self.close_ticket(channel, False)
            return
        # With confirmation
        if custom_id == "tickets_confirm_close_ticket":
            await self.close_ticket(channel, False)
            return

        # --- Button is for creating new ticket ---
        for category in config.get("categories"):
            if custom_id == "tickets_" + category:
                category_conf = config.get("categories").get(category)
                user = interaction.user
                guild = interaction.guild
                # Check that user has role required to create the ticket in this category
                role_identificator = category_conf.get("required-role")
                if role_identificator is not None:
                    if isinstance(role_identificator, int):
                        required_role = discord.utils.get(guild.roles, id=role_identificator)
                    else:
                        required_role = discord.utils.get(guild.roles, name=role_identificator)
                    if required_role not in user.roles:
                        # Send embed with info about missing role
                        embed_conf = config.get("missing-role-embed")
                        embed_desc = embed_conf.get("embed-description").replace("{role}", required_role.mention)
                        dembed = discord.Embed(title=embed_conf.get("embed-title"),
                                               description=embed_desc,
                                               color=embed_conf.get("embed-colour"))
                        dembed.set_footer(text=embed_conf.get("embed-footer"))
                        await interaction.response.send_message(ephemeral=True, embed=dembed)
                        return  # Do not create ticket and exit

                if db.get_count("tickets", f"creator_id={str(user.id)} AND is_closed=0") < config.get(
                        "maximum-tickets-per-user"):
                    # User can create ticket
                    # Create the ticket channel
                    role_identificator = category_conf.get("admin-role")
                    if isinstance(role_identificator, int):
                        admin_role = discord.utils.get(guild.roles, id=role_identificator)
                    else:
                        admin_role = discord.utils.get(guild.roles, name=role_identificator)
                    if not admin_role:  # If admin role is not set up
                        error = "Error occurred while trying to get **admin-role** for ticket category." \
                                " Please, check your configuration and try again."
                        print(error)
                        await self.send_error_message(interaction.channel, error)
                        return
                    cat = discord.utils.get(guild.categories, name=config.get("ticket-channel-category"))
                    if not cat:  # If category doesn't exist
                        error = "Error occurred while trying to get **category** for ticket channel." \
                                " Please, check your configuration and try again."
                        print(error)
                        await self.send_error_message(interaction.channel, error)
                        return
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True),
                        user: discord.PermissionOverwrite(read_messages=True),
                        admin_role: discord.PermissionOverwrite(read_messages=True)
                    }
                    channel_name = config.get("ticket-channel-name-format")
                    channel_name = channel_name.replace("{ticket_count}", str(db.get_next_auto_increment("tickets")))
                    channel_name = channel_name.replace("{creator}", user.name)
                    channel_name = channel_name.replace("{category_name}", category_conf.get("name"))
                    channel = await guild.create_text_channel(channel_name,
                                                              category=cat, overwrites=overwrites)
                    db.insert("tickets", "ticket_channel_id, ticket_category, creator_id, is_closed, creation_date",
                              "'" + str(channel.id) + "', '" + str(category) + "', '" + str(user.id) + "', 0, NOW()")
                    # Create management embed in the ticket
                    embed_conf = config.get("ticket-management-embed")
                    embed_desc = embed_conf.get("embed-description").replace("{instructions}",
                                                                             category_conf.get("instructions"))
                    membed = discord.Embed(title=embed_conf.get("embed-title").replace("{channel-name}", channel.name),
                                           description=embed_desc,
                                           colour=embed_conf.get("embed-colour"))
                    membed.set_footer(text=embed_conf.get("embed-footer"))
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(label=embed_conf.get("close-button"), custom_id="tickets_close_ticket", style=ButtonStyle.gray))
                    await channel.send(embed=membed, view=view)
                    # Ping admins in the ticket channel
                    if config.get("ping-admin-role-on-creation"):
                        msg = await channel.send(f"{admin_role.mention}")
                        await msg.delete()
                    # Send embed to generator that the ticket has been created and where
                    embed_conf = config.get("ticket-created-embed")
                    dembed = discord.Embed(title=embed_conf.get("embed-title"),
                                           description=embed_conf.get("embed-description").replace("{channel}",
                                                                                                   channel.mention),
                                           colour=embed_conf.get("embed-colour"))
                    dembed.set_footer(text=embed_conf.get("embed-footer"))
                    await interaction.response.send_message(embed=dembed, ephemeral=True)
                    print(f"Ticket created for {user.name}")

                else:
                    # User has too many tickets
                    embed_conf = config.get("too-many-tickets-embed")
                    embed = discord.Embed(title=embed_conf.get("embed-title"),
                                          description=embed_conf.get("embed-description"),
                                          colour=embed_conf.get("embed-colour"))
                    embed.set_footer(text=embed_conf.get("embed-footer"))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    print(f"Can't create ticket for {interaction.user.name}, user has too many tickets")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Checks if there should be admins mentioned in case there is a user response in a ticket"""
        if not config.get("ping-admin-role-on-user-response"):
            return
        if db.check_contains("tickets", "ticket_channel_id", str(message.channel.id))\
                and db.check_contains("tickets", "creator_id", str(message.author.id)):
            category = db.get_value_general("tickets", "ticket_category",
                                            f"ticket_channel_id={str(message.channel.id)} AND creator_id={str(message.author.id)}")
            role_identificator = config.get("categories").get(category).get("admin-role")
            if isinstance(role_identificator, int):
                admin_role = discord.utils.get(message.guild.roles, id=role_identificator)
            else:
                admin_role = discord.utils.get(message.guild.roles, name=role_identificator)
            msg = await message.channel.send(f"{admin_role.mention}")
            await msg.delete()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Check for unexpected ticket channel deletion"""
        if db.check_contains("tickets", "ticket_channel_id", str(channel.id)):
            if not db.get_value_general("tickets", "is_closed", f"ticket_channel_id={channel.id}"):
                await self.close_ticket(channel, True)
                print("Ticket force-closed, channel was deleted!")

    @commands.hybrid_command(description="Closes the ticket")
    async def close(self, ctx):
        """-close command handling for closing a ticket"""
        channel = ctx.message.channel
        if db.check_contains("tickets", "ticket_channel_id", str(channel.id)):
            if not db.get_value_general("tickets", "is_closed", f"ticket_channel_id={channel.id}"):
                await self.close_ticket(channel, False)

    @staticmethod
    async def confirm_close_ticket(interaction):
        """Handles creation of confirmation for ticket closing"""
        embed_conf = config.get("confirm-close-embed")
        embed = discord.Embed(title=embed_conf.get("embed-title"),
                              description=embed_conf.get("embed-description"),
                              color=embed_conf.get("embed-colour"))
        embed.set_footer(text=embed_conf.get("embed-footer"))
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=embed_conf.get("confirm-button"), custom_id="tickets_confirm_close_ticket", style=ButtonStyle.gray))
        await interaction.response.send_message(embed=embed,
                                  ephemeral=True,
                                  view=view)

    async def close_ticket(self, channel, force_closed):
        """Handles ticket closing"""
        ticket_id = db.get_id("tickets", "ticket_channel_id=" + str(channel.id))
        db.update_data("tickets", "is_closed", "1", f"id={str(ticket_id)}")
        if not force_closed:
            if config.get("send-transcription"):
                await self.create_transcript(ticket_id, channel)
            await channel.delete()
        print(f"Ticket {str(ticket_id)} closed.")

    async def create_transcript(self, ticket_id, channel):
        """Create and sends transcript."""
        try:
            transcript = await chat_exporter.export(channel)
            if transcript is None:
                return
        except Exception as e:
            print("Error occured while trying to create ticket transcript:")
            print(e)
            return
        ticket_creator = await self.bot.fetch_user(db.get_value_general("tickets", "creator_id", f"id={ticket_id}"))
        if ticket_creator:
            try:
                await ticket_creator.send(content=str(config.get("transcript-description")),
                                          file=discord.File(io.BytesIO(transcript.encode()),
                                                            filename=f"{channel.name}.html", ))
            except Exception:
                print(f"Failed to send ticket transcript to ticket creator. ({channel.name})")
        ticket_log_channel = get(self.bot.get_all_channels(), id=config.get("transcript-channel"))
        if ticket_log_channel:
            await ticket_log_channel.send(
                file=discord.File(io.BytesIO(transcript.encode()), filename=f"{channel.name}.html"))

    async def create_generator(self, ctx):
        """Creates new ticket generator in specific channel."""
        econfig = config.get("ticket-creator-embed")
        embed = discord.Embed(title=econfig.get("embed-title"),
                              description=econfig.get("embed-description"),
                              colour=econfig.get("embed-colour"))
        embed.set_footer(text=econfig.get("embed-footer"))

        view = discord.ui.View()
        for category in config.get("categories"):
            button_conf = config.get("categories").get(category)
            b_emoji = button_conf.get("emoji")
            if b_emoji == '':
                view.add_item(discord.ui.Button(label=button_conf.get("name"), custom_id="tickets_" + category, style=ButtonStyle.gray))
            else:
                view.add_item(discord.ui.Button(label=button_conf.get("name"), emoji=b_emoji, custom_id="tickets_" + category, style=ButtonStyle.gray))
        await ctx.reply(embed=embed, view=view)
        print("Ticket generator created!")

    @staticmethod
    async def send_error_message(channel, error_message):
        """Sends an error message to specified channel."""
        embed = discord.Embed(title="Bot ERROR", description=error_message, colour=0xff0000)
        await channel.send(embed=embed)


async def setup(bot):
    """Add the module to discord.py cogs"""
    await bot.add_cog(Tickets(bot))

# fine ticket



#fine ban unban

# Eventi
@bot.event
async def on_ready():
    print(Fore.RED + 'Logged in as')
    print(Fore.GREEN + bot.user.name)
    print(Style.RESET_ALL)
    print('Ready to support ✅')


@bot.event
async def on_message(message):
    bad_words = ["fuck", "arschloch", "https://discord.gg", "http://disord.gg", "discord.gg", "fick", "arsch", "Arschgesicht", "arschgesicht", "Arschloch", "Asshole", "asshole", "Fotze", "fotze", "Miststück", "miststück", "Bitch", "bitch", "Schlampe", "schlampe", "Sheisse", "sheisse", "Shit", "shit", "Fick", "huren", "Verpiss", "verpiss", "masturbiert", "Idiot", "idiot", "depp", "Depp", "Dumm", "dumm", "jude", "Bastard", "bastard", "Wichser", "wichser", "wixxer", "Wixxer", "Hurensohn" "Wixer", "Pisser", "Arschgesicht", "huso", "hure", "Hure", "verreck" "Verreck", "fehlgeburt", "Fehlgeburt", "ficken", "adhs", "ADHS", "Btch", "faggot", "fck", "f4ck", "nigga", "Nutted", "flaschengeburt", "penis", "pusse", "pusse", "pussy", "pussys", "nigger", "kacke", "fuucker"]
    for word in bad_words:
        if message.content.count(word) > 0:
            await message.channel.purge(limit=1)
            await message.channel.send(f"Stai usando parole non consentite, perfavore smettila! {message.author.mention}")


bot.run(token)
