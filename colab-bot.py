# !pip install pyTelegramBotAPI
# !pip install praw
# !pip install requests
# !pip install beautifulsoup4
# !pip install redgifs

import telebot
import threading
import praw
import random
import requests
from bs4 import BeautifulSoup
import os
import redgifs
import yarl

# Creds
telegram_token = ""
username = ""
password = ""
client_id = ""
client_secret=''
user_agent=""
mongo_uri=""
mongo_dbname=""
mongo_comment_collection=""
mongo_post_collection=""
subreddit_name = ""

api = redgifs.API()
api.login()
HEADERS = api.http.headers
get_gif = api.http.get_gif

bot = telebot.TeleBot(telegram_token)
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                     username=username, password=password, user_agent=user_agent)

def check_url_type(url):
    ext = os.path.splitext(url)[1]
    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
        return 'image'
    elif ext in ['.mp4', '.mov', '.avi']:
        return 'video'
    else:
        return 'website'


@bot.message_handler(commands=['start'])
def start(message):
    help_text = "The following commands are available:\n"
    commands = [
        '/start - Start the bot ',
        '/search - Search subreddits'
    ]
    for cmd in commands:
        help_text += cmd+"\n"
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['search'])
def search(message):
    print(message.chat.first_name, " :", message.text)
    subred = message.text.replace("/search ", "").strip()
    subred = subred.lower()
    url = 'https://www.reddit.com/search/?q='+str(subred)
    result = requests.get(
        url, headers={'User-Agent': 'Bored programmer\'s bot'})
    src = result.content
    soup = BeautifulSoup(src, 'html.parser')
    links = soup.find_all('a')
    subs = []
    for i in links:
        if 'r/' in i.text:
            for j in i:
                if len(j.split()) == 1 and ('http' not in j):
                    subs.append(str(j))
    o = ""
    for i in range(len(subs)):
        o = o+str(i+1)+") "+subs[i]+'\n'
    bot.send_message(chat_id=message.chat.id, text=o)


@bot.message_handler(commands=['meme'])
def send_memes(message):
    print(message.chat.first_name, " :", message.text)
    subred = message.text.replace("/meme ", "").strip()
    subred = subred.lower()
    if subred == "/meme":
        subred = "memes"

    def get_memes(message, subred, limit=1000):
        subreddit = reddit.subreddit(subred)
        top = list(subreddit.top(limit=limit))
        for i in top:
            try:
                random_sub = i
                out = ""
                if random_sub.title:
                    out += random_sub.title+'\n'
                if random_sub.selftext:
                    out += random_sub.selftext+'\n'
                if random_sub.author_flair_text:
                    out += random_sub.author_flair_text+'\n'
                random_sub.url = random_sub.url.replace(".gifv", ".mp4")
                if check_url_type(random_sub.url) == 'image':
                    response = requests.get(random_sub.url)
                    photo = response.content
                    bot.send_photo(message.chat.id, photo, caption=out)

                elif check_url_type(random_sub.url) == 'video':
                    response = requests.get(random_sub.url)
                    video = response.content
                    bot.send_video(message.chat.id, video, caption=out)

                else:
                    if "redgifs" not in random_sub.url:
                        if random_sub.url:
                            out += random_sub.url
                        bot.send_message(chat_id=message.chat.id, text=out)
                    else:
                        yarl_url = yarl.URL(random_sub.url)
                        id = yarl_url.path.strip('/watch/')
                        hd_url = get_gif(id)['gif']['urls']['hd']
                        response = requests.get(hd_url, headers=HEADERS)
                        video = response.content
                        bot.send_video(message.chat.id, video, caption=out)
            except:
                if random_sub.url:
                    out += random_sub.url
                bot.send_message(chat_id=message.chat.id, text=out)
    t = threading.Thread(target=get_memes, args=(message, subred,))
    t.start()
    t.join()


bot.polling()
