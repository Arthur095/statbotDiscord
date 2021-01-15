# bot_functions.py 

###########################
#########Imports###########
###########################

import discord, re, csv, os, random, logging, asyncio
from discord.ext import commands
from dotenv import load_dotenv
import numpy as np  
import matplotlib.pyplot as plt 

###########################
#########Functions#########
###########################
#Fonction de tri chronologique utilisable avec "sorted(list, key=sorting)" pour une liste de tuples sous la forme (date, valeur)
def sorting(L):
    splitup = L[0].split('-')
    return splitup[0], splitup[1], splitup[2]
    
# Affichage des données pour le camembert.
def pie_chart(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.1f}%\n(~{:d})".format(pct, absolute)

# Retourne la string d'une couleur aléatoire d'après une liste définie de couleurs.
def get_random_color():
    colors = ["blue", "green", "red", "cyan", "magenta", "yellow", "black"]
    num = random.randint(0, len(colors)-1)
    return colors[num]
    
# Créer un graphe d'après le résultat des réactions du sondage.
async def get_channel_poll(question, reactions, channel_name):
    dico = {"✅":"Oui", "❌":"Non", "1⃣":"1", "2⃣":"2", "3⃣":"3", "4⃣":"4", "5⃣":"5"}
    
    choice = []
    count = []
     
    for reaction in reactions :
        choice.append(dico.get(reaction.emoji))
        count.append((reaction.count)-1)  
        
    choice = np.array(choice)
    count = np.array(count)
        
    total_votes = 0
    for vote in count :
        total_votes += vote
    
    # Plotting
    fig, ax = plt.subplots()
    ax.axis('equal')  # Cercle
    sch, texts, autotexts = ax.pie(count, labels=choice, autopct=lambda pct: pie_chart(pct, count),  shadow=True, startangle=90)
    ax.legend(sch, choice, title="Choices", loc="upper right", bbox_to_anchor=(1.1, 1))
    plt.setp(autotexts, size=8, weight="bold")
    if total_votes < 2 :
        plt.title(f"Poll results : {question}\nTotal : {total_votes} vote", ha='center')
    else:
        plt.title(f"Poll results : {question}\nTotal : {total_votes} votes", ha='center')
        
    plt.savefig(f"graph/{channel_name}_poll.png")
    
    # Fermeture du plot.
    plt.close()
    
# Créer un graphe représentant le nombre moyen de token par utilisateur.
async def get_channel_token(guild, channels, users) :
    user_dico = {}
    user_tokens = {}
    
    #Lecture du csv et indexage (nombre de tokens et nombre de message pour chaque utilisateur).
    for user in users :
        for channel in channels :
            if channel.topic != channel.name:
                with open(f"guilds/{guild.name}/{channel.name}.csv", 'r') as file :
                    reader = csv.DictReader(file, delimiter=';', quotechar='"')
                    for row in reader :
                        if row['id'] == str(user.id) :
                            if row['message'][0:17] != "https://tenor.com":
                                user_dico[user.name] = user_dico.get(user.name, 0) + 1
                                user_tokens[user.name] = user_tokens.get(user.name, 0) + len(row['message'].split())
                        
    #Conversion en array Numpy après calcul de la moyenne.
    name = np.array(list(user_dico.keys()))
    average = np.array([t/m for t,m in zip(user_tokens.values(), user_dico.values())])
    
    #Calcul du total de messages et tokens
    total_messages = 0
    for item in user_dico.values() :
        total_messages += item
    total_tokens = 0
    for item in user_tokens.values() :
        total_tokens += item
        
    #Plotting
    if len(channels) == 1 and len(users) == 1 :
        plt.title(f"Average tokens per message : {user.name}- Channel : {channel.name}\nTotal : {total_messages} messages and {total_tokens} tokens", ha='center')
    elif len(channels) > 1 and len(users) == 1 :
        plt.title(f"Average tokens per message : {user.name} - All Channels\nTotal : {total_messages} messages and {total_tokens} tokens", ha='center') 
    elif len(channels) == 1 and len(users) == len(guild.members) :
        plt.title(f"Average tokens per message : Everyone - Channel : {channel.name}\nTotal : {total_messages} messages and {total_tokens} tokens", ha='center')
    elif len(channels) > 1 and len(users) == len(guild.members) :
        plt.title(f"Average tokens per message : Everyone - All Channels\nTotal : {total_messages} messages and {total_tokens} tokens", ha='center')
    elif len(channels) == 1 and len(users) < len(guild.members) and len(users) > 1 :
        plt.title(f"Average tokens per message : See mentions - Channel : {channel.name}\nTotal : {total_messages} messages and {total_tokens} tokens", ha='center')
    elif len(channels) > 1 and len(users) < len(guild.members) and len(users) > 1 :
        plt.title(f"Average tokens per message : See mentions - Channel : All channels\nTotal : {total_messages} messages and {total_tokens} tokens", ha='center')
        
    if len(users) == 1 :
        plt.xticks(fontsize=15, rotation=0)
    elif len(users) > 1 and len(users) < 5 :
        plt.xticks(fontsize=10, rotation=0)
    elif len(users) > 4 :
        plt.xticks(fontsize=5, rotation=-75)
        
    plt.bar(name, average, color=get_random_color())
    
    # Sauvegarde et fermeture du plot.
    plt.savefig('graph/MPD.png')
    plt.close()
    
    
# Créer un graphe catégorisé au format png du nombre de questions et de réponses.
async def get_channel_question_answer(guild, channels, users):
    user_dico = {}
    
    # Lecture du csv et indexage.
    for user in users :
        for channel in channels :
            with open(f"guilds/{guild.name}/{channel.name}.csv", 'r') as file :
                reader = csv.DictReader(file, delimiter=';', quotechar='"')
                for row in reader :
                    if row['id'] == str(user.id) :
                        if "?" in list(row['message']) :
                            user_dico["Questions"] = user_dico.get("Questions",0)+1
                        elif row['reponse'] == "True" :
                            user_dico["Answers"] = user_dico.get("Answers",0)+1
                    
    # Conversion en array numpy.
    sent = np.array(list(user_dico.keys()))
    value = np.array(list(user_dico.values()))
    
    # Total de messages questions ou réponses.
    total_messages = 0
    for num in value :
        total_messages += num
    
    #Plotting
    if len(channels) == 1 and len(users) == 1 :
        plt.title(f"Questions and Answers : {user.name} \n Channel : {channel.name} - Total : {total_messages}", ha='center')
    elif len(channels) > 1 and len(users) == 1 :
        plt.title(f"Questions and Answers : {user.name} \n All Channels - Total : {total_messages}", ha='center') 
    elif len(channels) == 1 and len(users) == len(guild.members) :
        plt.title(f"Questions and Answers : Everyone \n Channel : {channel.name} - Total : {total_messages}", ha='center')
    elif len(channels) > 1 and len(users) == len(guild.members) :
        plt.title(f"Questions and Answers : Everyone \n All Channels - Total : {total_messages}", ha='center')
    elif len(channels) == 1 and len(users) < len(guild.members) and len(users) > 1 :
        plt.title(f"Questions and Answers : See mentions \n Channel : {channel.name} - Total : {total_messages}", ha='center')
    elif len(channels) > 1 and len(users) < len(guild.members) and len(users) > 1 :
        plt.title(f"Questions and Answers : See mentions \n Channel : All channels - Total : {total_messages}", ha='center')
    
    plt.bar(sent, value, color=get_random_color())
    
    # Sauvegarde et fermeture du plot.
    plt.savefig('graph/MPD.png')
    plt.close()
                
# Créer un camembert au format png du % de messages et du % de gifs, par utilisateur ou non sur le serveur en paramètre et les channels en paramètre.
async def get_channel_item_vs_item(guild, channels, users="", mvg=False, gif=False, all=False):
    user_dico = {}
    
    # Messages ou gifs
    if gif == True :
        m_or_g = "Gifs"
    else :
        m_or_g = "Messages"
        
    # Lecture du csv et indexage.
    #Pour Messages vs Gifs
    if mvg == True:
        for channel in channels :
            with open(f"guilds/{guild.name}/{channel.name}.csv", 'r') as file :
                reader = csv.DictReader(file, delimiter=';', quotechar='"')
                for row in reader :
                    if row['message'][0:17] == "https://tenor.com":
                        user_dico["gif"] = user_dico.get("gif",0)+1
                    else :
                        user_dico["message"] = user_dico.get("message",0)+1
                        
    else :
        for user in users :
            for channel in channels :
                if channel.topic != channel.name:
                    with open(f"./guilds/{guild.name}/{channel.name}.csv", 'r') as file :
                        reader = csv.DictReader(file, delimiter=';', quotechar='"')
                        for row in reader :
                            if row['id'] == str(user.id) :
                                if gif == True : 
                                    if row['message'][0:17] == "https://tenor.com":
                                        user_dico[row['utilisateur']] = user_dico.get(row['utilisateur'],0)+1
                                elif gif == False and all == False :
                                    if row['message'][0:17] != "https://tenor.com":
                                        user_dico[row['utilisateur']] = user_dico.get(row['utilisateur'],0)+1

    # Conversion en array numpy
    role = np.array(list(user_dico.keys()))
    message = np.array(list(user_dico.values()))
    
    # Calcul du total de messages
    total_messages = 0
    for num in message :
        total_messages += num
    
    # Plotting
    fig, ax = plt.subplots()
    ax.axis('equal')  # Cercle
    sch, texts, autotexts = ax.pie(message, labels=role, autopct=lambda pct: pie_chart(pct, message),  shadow=True, startangle=90)
    ax.legend(sch, role, title="Members", loc="upper right", bbox_to_anchor=(1.1, 1))
    plt.setp(autotexts, size=8, weight="bold")

    
    # Titre selon le nombre de channels.
    if len(channels) == 1 and mvg == True:
        plt.title(f"Messages vs Gifs : {channel.name} \n Total : {total_messages}", ha='center')
    elif len(channels) > 1 and mvg == True : 
        plt.title(f"Messages vs Gifs : All Channels \n Total : {total_messages}", ha='center')
    elif len(channels) == 1 and mvg == False :
        plt.title(f"{m_or_g} vs. : {channel.name} \nSee mentions - Total : {total_messages}", ha='center')
    elif len(channels) > 1 and mvg == False :
        plt.title(f"{m_or_g} vs. : All Channels \n See mentions - Total : {total_messages}", ha='center')
    
    plt.savefig('graph/MPD.png')
    
    # Fermeture du plot.
    plt.close()

# Créer un camembert au format png du % de messages par role sur le serveur en paramètre et les channels en paramètre.
async def get_channel_message_stats_roles(guild, channels, gif=False):
    user_dico = {}
    
    # Messages ou gifs
    if gif == True :
        m_or_g = "Gifs"
    else :
        m_or_g = "Messages"
        
    # Lecture du csv et indexage.
    for channel in channels :
        with open(f"guilds/{guild.name}/{channel.name}.csv", 'r') as file :
            reader = csv.DictReader(file, delimiter=';', quotechar='"')
            for row in reader :
                roles = row['role'].split('|')
                for role in roles :
                    if role != "@everyone" and role != "":
                        if gif == True :
                            if row['message'][0:17] == "https://tenor.com":
                                user_dico[role] = user_dico.get(role,0)+1
                        else :
                            if row['message'][0:17] != "https://tenor.com":
                                user_dico[role] = user_dico.get(role,0)+1

    # Conversion en array numpy
    role = np.array(list(user_dico.keys()))
    message = np.array(list(user_dico.values()))
    
    # Calcul du total de messages
    total_messages = 0
    for num in message :
        total_messages += num
    
    # Plotting
    fig, ax = plt.subplots()
    ax.axis('equal')  # Cercle
    sch, texts, autotexts = ax.pie(message, labels=role, autopct=lambda pct: pie_chart(pct, message),  shadow=True, startangle=90)
    ax.legend(sch, role, title="Roles", loc="upper right", bbox_to_anchor=(1.1, 1))
    plt.setp(autotexts, size=8, weight="bold")

    
    # Titre selon le nombre de channels.
    if len(channels) == 1 :
        plt.title(f"{m_or_g} % by role : {channel.name} \n Total : {total_messages}", ha='center')
    else : 
        plt.title(f"{m_or_g} % by role : All Channels \n Total : {total_messages}", ha='center')
    
    plt.savefig('graph/MPD.png')
    
    # Fermeture du plot.
    plt.close()
    
#Créer un graph au format png du nombre de messsage par jour pour l'utilisateur, le channel et le serveur donnés en paramètres. guild=guil, channels=list, user=user.
async def get_channel_message_stats(guild, channels, users, gif=False):
    user_dico = {}
    
    # Messages ou gifs
    if gif == True :
        m_or_g = "Gifs"
    else :
        m_or_g = "Messages"
        
    # Lecture du csv et indexage.
    for user in users :
        for channel in channels :
            if channel.topic != channel.name:
                with open(f"./guilds/{guild.name}/{channel.name}.csv", 'r') as file :
                    reader = csv.DictReader(file, delimiter=';', quotechar='"')
                    for row in reader :
                        if row['id'] == str(user.id) :
                            if gif == True : 
                                if row['message'][0:17] == "https://tenor.com":
                                    user_dico[row['date']] = user_dico.get(row['date'],0)+1
                            else :
                                if row['message'][0:17] != "https://tenor.com":
                                    user_dico[row['date']] = user_dico.get(row['date'],0)+1
        
    # Conversion en array numpy et tri chronologique des dates.
    #data = [(item[0], item[1]) for item in user_dico.items()]
    sorted_date = sorted(user_dico.items(), key=sorting)
    date = np.array([e[0] for e in sorted_date])
    message = np.array([e[1] for e in sorted_date])
    
    total_messages = 0
    for num in message :
        total_messages += num
    
    # Plotting 
    # Titre selon le nombre de channels et d'utilisateurs.
    if len(channels) == 1 and len(users) == 1 :
        plt.title(f"{m_or_g} by date : {user.name} \n Channel : {channel.name} - Total : {total_messages}", ha='center')
    elif len(channels) > 1 and len(users) == 1 :
        plt.title(f"{m_or_g} by date : {user.name} \n All Channels - Total : {total_messages}", ha='center') 
    elif len(channels) == 1 and len(users) == len(guild.members) :
        plt.title(f"{m_or_g} by date : Everyone \n Channel : {channel.name} - Total : {total_messages}", ha='center')
    elif len(channels) > 1 and len(users) == len(guild.members) :
        plt.title(f"{m_or_g} by date : Everyone \n All Channels - Total : {total_messages}", ha='center')
    elif len(channels) == 1 and len(users) < len(guild.members) and len(users) > 1 :
        plt.title(f"{m_or_g} by date : See mentions \n Channel : {channel.name} - Total : {total_messages}", ha='center')
    elif len(channels) > 1 and len(users) < len(guild.members) and len(users) > 1 :
        plt.title(f"{m_or_g} by date : See mentions \n Channel : All channels - Total : {total_messages}", ha='center')
    
       
    plt.xlabel("Date")  
    plt.ylabel(f"{m_or_g}")  
    
    #Arrangement des noms des ticks horizontaux car trop nombreux pour afficher une date.
    ticks = len(date)
    plt.xticks(fontsize=6, rotation= -50)
    
    if ticks > 12 and ticks <20 :
        plt.xticks(np.arange(0, ticks+1, 1.5))
    elif ticks > 20 :
        plt.xticks(np.arange(0, ticks+1, 2))
    elif ticks > 50 :
        plt.xticks(10)
    
    #Génération et sauvegarde du plot sur le disque.
    plt.plot(date, message, color=get_random_color())  
    plt.savefig(f"graph/MPD.png")
    
    #Fermer le plot pour ne pas générer une seconde courbe et remplacer les données.
    plt.close() 
    

#Récupère tous les messages des serveurs données en paramètre avec les infos : data,role,utilisateur,id_utilisateur,contenu du message, réponse oui ou non.
async def get_server_stats(guilds):

    #Pour ne traiter qu'une seule guilde spécifiquement. 
    #guilds = [bot.get_guild(int(os.getenv('GUILD_ID')))]
    
    for guild in guilds:
        # Récupération des roles des utilisateurs.
        role_dict = {}
        for role in guild.roles:
            for member in role.members:
                if not member.bot :
                    role_dict[member.id] = role_dict.get(member.id,[])+[role.name]

        #Création d'un dossier pour la guilde en question:
        if not os.path.exists(os.path.join(f"{os.getcwd()}/guilds", guild.name)):
            os.mkdir(f"{os.getcwd()}/guilds/{guild.name}")
            os.mkdir(f"{os.getcwd()}/graph/{guild.name}")
        
        # Aspiration des messages de chaque channel.
        for channel in guild.text_channels:
        
            if channel.topic != channel.name:
                with open(f"./guilds/{guild.name}/{channel.name}.csv", 'w') as file:
                    file.write("date;role;utilisateur;id;message;reponse\n")
                    
                    async for message in channel.history(limit=None, oldest_first=True):
                    
                        # Réponse ou non.
                        if message.reference != None :
                            is_reply = True
                        else :
                            is_reply = False
                            
                        # Fichiers, images upload depuis son ordinateur ou message crée à partir d'un pin
                        attach = ""
                        for attachment in message.attachments :
                            attach += f"{attachment.url}|"
                            
                        # Bot ou non + clean
                        if not message.author.bot and str(message.clean_content) != "" :
                            if str(message.clean_content)[0] != "!" :
                                mp = re.sub(r"\r?\n", " ", message.clean_content)
                                mp = re.sub(r";", "", mp)
                                
                                if mp == "" and attach != "" :
                                    mp = attach
                                elif mp == "" and attach == "" :
                                    continue
                                
                                file.write(f"{str(message.created_at).split(' ')[0]};{'|'.join(role_dict[message.author.id])};{message.author.display_name};{message.author.id};{mp};{is_reply}\n")
                                            
