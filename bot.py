# bot.py
###########################
#########Imports###########
###########################
import discord, re, csv, os, random, logging, asyncio
from discord.ext import commands
from dotenv import load_dotenv
import numpy as np  
import matplotlib.pyplot as plt 
from bot_functions import *

###########################
#########Setup#############
###########################
# Récupération du token depuis le fichier .env .
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Mise en place du bot.
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

###########################
#########Logging###########
###########################
# Mise en place du logger pour avoir une trace des évènements et erreurs.
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

###########################
#########Events############
###########################
# On met à jours les stats de TOUS les serveurs du bot au démarrage. (Cela peut prendre plusieurs minutes en fonction du nombre de serveurs et de messages).
@bot.event
async def on_ready():
    print("Bot is connected and ready to process.")
    while True:
        await get_server_stats(bot.guilds)
        print("Done exporting messages.")
        await asyncio.sleep(43200) #unit=sec.

###########################
#########Commands##########
###########################

# Commande principale (!stats)
@bot.group(name="stats", invoke_without_command=True) 
async def stats(ctx):
    await ctx.send("Utilisation : !stats <global|help>? <message|gif|q&a|token|vs*> <one|everyone|+|role*|vs*> <@mention>*")

# Nouveau sous-groupe message. Messages par date.
@stats.group(name="message", invoke_without_command=True)
async def stats_message(ctx):
    await stats(ctx)
   
# Sous-groupe message. Stats pour le channel contextuel des personnes mentionnées.   
@stats_message.command(name="one")
async def message_one(ctx, arg1):
    if arg1[0:3] == "<@!" :   
        for user in ctx.message.mentions:
            if not user.bot:
                await get_channel_message_stats(ctx.guild, [ctx.message.channel], [user])
                await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
            else :
                await ctx.send("Les statistiques des bots ne sont pas enregistrées.")
    else :
        await stats(ctx)

# Sous-groupe message. Stats pour le channel contextuel de tous le monde.
@stats_message.command(name="everyone")
async def message_everyone(ctx):
    await get_channel_message_stats(ctx.guild, [ctx.message.channel], ctx.guild.members)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))

# Sous-groupe message. Stats cumulées pour le channel contextuel des personnes mentionnées.
@stats_message.command(name="+")
async def message_plus(ctx, arg1):
    if arg1[0:3] == "<@!" : 
        await get_channel_message_stats(ctx.guild, [ctx.message.channel], ctx.message.mentions)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)

# Sous-groupe message. Stats du nombre de messages par rôle pour le channel contextuel.
@stats_message.command(name="role")
async def message_role(ctx):
    await get_channel_message_stats_roles(ctx.guild, [ctx.message.channel])
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    
# Sous-groupe message. Stats en camembert des messages des personnes en mentions pour le channel contextuels.
@stats_message.command(name="vs")
async def message_vs(ctx):
    if len(ctx.message.mentions) > 1 :
        await get_channel_item_vs_item(ctx.guild, [ctx.message.channel], users=ctx.message.mentions)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)
    
# Nouveau sous-groupe gif. Gifs par date.
@stats.group(name="gif", invoke_without_command=True)
async def stats_gif(ctx):
    await stats(ctx)
    
# Sous-groupe gif. Stats pour le channel contextuel des personnes mentionnées.   
@stats_gif.command(name="one")
async def gif_one(ctx, arg1):
    if arg1[0:3] == "<@!" :   
        for user in ctx.message.mentions:
            if not user.bot:
                await get_channel_message_stats(ctx.guild, [ctx.message.channel], [user], True)
                await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
            else :
                await ctx.send("Les statistiques des bots ne sont pas enregistrées.")
    else :
        await stats(ctx)

# Sous-groupe gif. Stats pour le channel contextuel de tous le monde.
@stats_gif.command(name="everyone")
async def gif_everyone(ctx):
    await get_channel_message_stats(ctx.guild, [ctx.message.channel], ctx.guild.members, True)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))

# Sous-groupe gif. Stats cumulées pour le channel contextuel des personnes mentionnées.
@stats_gif.command(name="+")
async def gif_plus(ctx, arg1):
    if arg1[0:3] == "<@!" : 
        await get_channel_message_stats(ctx.guild, [ctx.message.channel], ctx.message.mentions, True)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)

# Sous-groupe gif. Stats du nombre de gif par rôle pour le channel contextuel.
@stats_gif.command(name="role")
async def gif_role(ctx):
    await get_channel_message_stats_roles(ctx.guild, [ctx.message.channel], True)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    
# Sous-groupe gif. Stats en camembert des gifs des personnes en mentions pour le channel contextuels.
@stats_gif.command(name="vs")
async def gif_vs(ctx):
    if len(ctx.message.mentions) > 1 :
        await get_channel_item_vs_item(ctx.guild, [ctx.message.channel], users=ctx.message.mentions, gif=True)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)

# Groupe stats. Comparaison messages et gifs pour le channel contextuel.
@stats.command(name="vs", invoke_without_command=True)
async def stats_vs(ctx):
    await get_channel_item_vs_item(ctx.guild, [ctx.message.channel], mvg=True)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    
# Nouveau sous-groupe q&a. Questions et réponses.
@stats.group(name="q&a", invoke_without_command=True)
async def stats_qa(ctx):
    await stats(ctx)
    
# Sous-groupe q&a. Questions et réponses par personne pour toutes les personnes mentionnées pour le channel contextuel.
@stats_qa.command(name="one")
async def qa_one(ctx, arg1):
    if arg1[0:3] == "<@!" :   
        for user in ctx.message.mentions:
            if not user.bot:
                await get_channel_question_answer(ctx.guild, [ctx.message.channel], [user])
                await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
            else :
                await ctx.send("Les statistiques des bots ne sont pas enregistrées.")
    else :
        await stats(ctx)

# Sous-groupe q&a. Questions et réponses pour tous le monde pour le channel contextuel.
@stats_qa.command(name="everyone")
async def qa_everyone(ctx):
    await get_channel_question_answer(ctx.guild, [ctx.message.channel], ctx.guild.members)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    
# Sous-groupe q&a. Questions et réponses cumulées pour les personnes mentionnées pour le channel contextuel.
@stats_qa.command(name="+")
async def qa_plus(ctx, arg1):
    if arg1[0:3] == "<@!" : 
        await get_channel_question_answer(ctx.guild, [ctx.message.channel], ctx.message.mentions)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)

# Nouveau sous-groupe token. Moyenne de token par message par utilisateur.
@stats.group(name="token", invoke_without_command=True)
async def stats_token(ctx):
    await stats(ctx)
   
# Sous-groupe token. Stats pour le channel contextuel des personnes mentionnées.   
@stats_token.command(name="one")
async def token_one(ctx, arg1):
    if arg1[0:3] == "<@!" :   
        for user in ctx.message.mentions:
            if not user.bot:
                await get_channel_token(ctx.guild, [ctx.message.channel], [user])
                await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
            else :
                await ctx.send("Les statistiques des bots ne sont pas enregistrées.")
    else :
        await stats(ctx)

# Sous-groupe token. Stats pour le channel contextuel de tous le monde.
@stats_token.command(name="everyone")
async def token_everyone(ctx):
    await get_channel_token(ctx.guild, [ctx.message.channel], ctx.guild.members)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    
# Sous-groupe token. Comparaison de la moyenne de token pour les personnes mentionnées pour le channel contextuel.
@stats_token.command(name="vs")
async def token_vs(ctx, arg1):
    if arg1[0:3] == "<@!" : 
        await get_channel_token(ctx.guild, [ctx.message.channel], ctx.message.mentions)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)
        
# Nouveau sous-groupe poll. Permet de lancer un sondage d'après les arguments et renvoie un camembert des résultats.
@stats.command(name="poll")
async def poll(ctx, *args) :
    
    if len(args) == 0 :
        await ctx.send("""Utilisation : !stats poll temps_en_secondes "question" "choix1", "choix2", "choix3" ...""")
        return
    
    if int(args[0]) > 180 :
        await ctx.send("Le temps maximal est de trois minutes.")
        return
        
    try:
        int(args[0])
    except:
        await ctx.send("Utilisation : !stats poll temps question choix1, choix2, choix3...\n Le temps maximum est de trois minutes.")
        return  
    
    if len(args) > 7 :
        await ctx.send("Un maximum de 5 choix sont possibles pour le sondage.")
        return
    elif len(args) < 2 : 
        await ctx.send("Un sondage doit au moins poser une question")
        return
    
    if len(args) == 2 :
        reactions = ["✅", "❌"]
    else :
        reactions = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣"]
        
    deco = [":cat2:", ":rabbit:", ":rabbit2:", ":dog2:", ":penguin:", ":mouse2:", ":fox:", ":wolf:", ":tiger2:", ":horse:", ":monkey:"]
    id = random.randint(0, len(deco)-1)
    
    sondage = f"{deco[id]} Un sondage est ouvert : **{args[1]}** {deco[id]}\n\n"
    
    if len(args) == 2 :
        sondage += f"✅ - OUI\n❌ - NON"
    else :
        for i, arg in enumerate(args[2:]) :
            sondage += f"{reactions[i]} - {arg}\n\n"
    
    put_reaction = await ctx.send(sondage)
    
    if len(args) != 2 :
        cnt = 0
        while cnt < len(args[2:]) :
            await put_reaction.add_reaction(reactions[cnt])
            cnt +=1
    else :
        for reaction in reactions :
            await put_reaction.add_reaction(reaction)
            
    await asyncio.sleep(int(args[0]))
    
    put_reaction = await ctx.fetch_message(put_reaction.id)
    
    await get_channel_poll(args[1], put_reaction.reactions, ctx.channel.name, ctx.guild.name)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/{ctx.channel.name}_poll.png"))
    
#########################################

# Nouveau sous-groupe global.
@stats.group(name="global", invoke_without_command=True)
async def stats_global(ctx):
    await stats(ctx)
    
# Nouveau sous-groupe global_message. 
@stats_global.group(name="message", invoke_without_command=True)
async def global_message(ctx):
    await stats(ctx)

# Sous-groupe global_message. Stats pour tous les channels des personnes mentionnées. 
@global_message.command(name="one")
async def global_message_one(ctx, arg1):
    if arg1[0:3] == "<@!"  :
        for user in ctx.message.mentions:
            if not user.bot:
                await get_channel_message_stats(ctx.guild, ctx.guild.text_channels, [user])
                await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
            else :
                await ctx.send("Les statistiques des bots ne sont pas enregistrées.")
    else :
        await stats(ctx)
 
# Sous-groupe global_message. Stats pour tous channels, de tous le monde.
@global_message.command(name="everyone")
async def global_message_everyone(ctx):
    await get_channel_message_stats(ctx.guild, ctx.guild.text_channels, ctx.guild.members)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))

# Sous-groupe global_message. Stats cumulées pour tous les channels des personnes mentionnées.
@global_message.command(name="+")
async def global_message_plus(ctx, arg1):  
    if arg1[0:3] == "<@!" :
        await get_channel_message_stats(ctx.guild, ctx.guild.text_channels, ctx.message.mentions)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)
        
# Sous-groupe global_message. Stats du nombre de messages par rôle pour tous les channels.
@global_message.command(name="role")
async def global_message_role(ctx):
    await get_channel_message_stats_roles(ctx.guild, ctx.guild.text_channels)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))

# Sous-groupe global_message. Stats en camembert des messages des personnes en mentions pour tous les channels.
@global_message.command(name="vs")
async def message_vs(ctx):
    if len(ctx.message.mentions) > 1 :
        await get_channel_item_vs_item(ctx.guild, ctx.guild.text_channels, users=ctx.message.mentions)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)
    
# Nouveau sous-groupe global_gif. 
@stats_global.group(name="gif", invoke_without_command=True)
async def global_gif(ctx):
    await stats(ctx)

# Sous-groupe global_gif. Stats pour tous les channels des personnes mentionnées. 
@global_gif.command(name="one")
async def global_gif_one(ctx, arg1):
    if arg1[0:3] == "<@!"  :
        for user in ctx.message.mentions:
            if not user.bot:
                await get_channel_message_stats(ctx.guild, ctx.guild.text_channels, [user], True)
                await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
            else :
                await ctx.send("Les statistiques des bots ne sont pas enregistrées.")
    else :
        await stats(ctx)
 
# Sous-groupe global_gif. Stats pour tous channels, de tous le monde.
@global_gif.command(name="everyone")
async def global_gif_everyone(ctx):
    await get_channel_message_stats(ctx.guild, ctx.guild.text_channels, ctx.guild.members, True)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))

# Sous-groupe global_gif. Stats cumulées pour tous les channels des personnes mentionnées.
@global_gif.command(name="+")
async def global_gif_plus(ctx, arg1):  
    if arg1[0:3] == "<@!" :
        await get_channel_message_stats(ctx.guild, ctx.guild.text_channels, ctx.message.mentions, True)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)
        
# Sous-groupe global_gif. Stats du nombre de gifs par rôle pour tous les channels.
@global_gif.command(name="role")
async def global_gif_role(ctx):
    await get_channel_message_stats_roles(ctx.guild, ctx.guild.text_channels, True)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    
# Sous-groupe global_gif. Stats en camembert des gifs des personnes en mentions pour le channel contextuels.
@global_gif.command(name="vs")
async def global_gif_vs(ctx):
    if len(ctx.message.mentions) > 1 :
        await get_channel_item_vs_item(ctx.guild, ctx.guild.text_channels, users=ctx.message.mentions, gif=True)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)
    
# Nouveau sous groupe de stats_global. Comparaison messages et gifs pour tous les channels.
@stats_global.command(name="vs", invoke_without_command=True)
async def stats_global_vs(ctx):
    await get_channel_item_vs_item(ctx.guild, ctx.guild.text_channels, mvg=True)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))

# Nouveau sous-groupe global_q&a. Questions et réponses.
@stats_global.group(name="q&a", invoke_without_command=True)
async def global_qa(ctx):
    await stats(ctx)
    
# Sous-groupe q&a. Questions et réponses par personne pour toutes les personnes mentionnées pour le channel contextuel.
@global_qa.command(name="one")
async def global_qa_one(ctx, arg1):
    if arg1[0:3] == "<@!" :   
        for user in ctx.message.mentions:
            if not user.bot:
                await get_channel_question_answer(ctx.guild, ctx.guild.text_channels, [user])
                await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
            else :
                await ctx.send("Les statistiques des bots ne sont pas enregistrées.")
    else :
        await stats(ctx)

# Sous-groupe q&a. Questions et réponses pour tous le monde pour le channel contextuel.
@global_qa.command(name="everyone")
async def global_qa_everyone(ctx):
    await get_channel_question_answer(ctx.guild, ctx.guild.text_channels, ctx.guild.members)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    
# Sous-groupe q&a. Questions et réponses cumulées pour les personnes mentionnées pour le channel contextuel.
@global_qa.command(name="+")
async def global_qa_plus(ctx, arg1):
    if arg1[0:3] == "<@!" : 
        await get_channel_question_answer(ctx.guild, ctx.guild.text_channels, ctx.message.mentions)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)

# Nouveau sous-groupe global_token. Moyenne de token par message par utilisateur.
@stats_global.group(name="token", invoke_without_command=True)
async def global_token(ctx):
    await stats(ctx)
   
# Sous-groupe global_token. Stats pour tous les channels des personnes mentionnées.   
@global_token.command(name="one")
async def global_token_one(ctx, arg1):
    if arg1[0:3] == "<@!" :   
        for user in ctx.message.mentions:
            if not user.bot:
                await get_channel_token(ctx.guild, ctx.guild.text_channels, [user])
                await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
            else :
                await ctx.send("Les statistiques des bots ne sont pas enregistrées.")
    else :
        await stats(ctx)

# Sous-groupe global_token. Stats pour tous les channels de tous le monde.
@global_token.command(name="everyone")
async def global_token_everyone(ctx):
    await get_channel_token(ctx.guild, ctx.guild.text_channels, ctx.guild.members)
    await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    
# Sous-groupe global_token. Comparaison de la moyenne de token pour les personnes mentionnées pour tous les channels.
@global_token.command(name="vs")
async def global_token_vs(ctx, arg1):
    if arg1[0:3] == "<@!" : 
        await get_channel_token(ctx.guild, ctx.guild.text_channels, ctx.message.mentions)
        await ctx.send(file=discord.File(f"graph/{ctx.guild.name}/MPD.png"))
    else :
        await stats(ctx)

# Groupe stats . Affiche le lien vers l'aide.
@stats.command(name="help")
async def stats_help(ctx):
    await ctx.send("https://github.com/Arthur095/statbotDiscord")

##########################

#Met à jour les statistiques du serveur contextuel.
#@commands.has_any_role("prof", "admin", "test")
@stats.command(name="refresh")
async def stats_refresh(ctx):
    await get_server_stats([ctx.message.guild])
    await ctx.send("Les statistiques ont été mises à jour.")
    
##########################

if __name__ == '__main__':
    bot.run(TOKEN)
