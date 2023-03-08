# !pip install pyTelegramBotAPI
# !pip install praw
# !pip install requests
# !pip install beautifulsoup4
# !pip install redgifs
# !pip install convertapi

import telebot
import threading,sys
import praw
import requests
from bs4 import BeautifulSoup
import os
import redgifs
import yarl
import convertapi
from io import BytesIO
import tempfile


API_KEY = "5215172336:AAExMMURMmx-VoOiqj68thVmLJTFrb67gZc"
convertapi.api_secret = '66kpFfFS194MEvNN'
telegram_token = "5215172336:AAExMMURMmx-VoOiqj68thVmLJTFrb67gZc"
api = redgifs.API()
api.login()
HEADERS = api.http.headers
get_gif = api.http.get_gif

username = "Fit-Belt1935"
password = "Rishabh@12345"
client_id = "H2f8VSpd-8t5AoQSGZVVoA"
client_secret='c5PexU5V63uQYOGeMQWAz0pqG1FN0w'
user_agent="Reddit bot for bidding"
bot = telebot.TeleBot(telegram_token)
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                     username=username, password=password, user_agent=user_agent)

RUN = True

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
        '/search - Search subreddits',
        '/meme - Get all meme from a subreddit',
        '/stop - stop the running commands',
        '/restart - Re Run the bot script'
    ]
    for cmd in commands:
        help_text += cmd+"\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['restart'])
def restart(message):
    print(message.chat.first_name, " :", message.text)
    bot.reply_to(message, "Restarting...")
    os.execv(sys.argv[0], sys.argv)

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

@bot.message_handler(content_types=['document', 'photo'])
def convert_to_pdf(message):
    if (message.caption == "/convert"):
        print(message.chat.first_name," :",message.caption)
        try:
            bot.send_message(message.chat.id, 'Converting...')
            send_photo_warning = False
            content_type = message.content_type

            documents = getattr(message, content_type)
            if not isinstance(documents, list):
                documents = [documents]

            for doc in documents:
                file_id = doc.file_id
                file_info = bot.get_file(file_id)
                #print(file_info)
                file_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(API_KEY, file_info.file_path)

                file_data = BytesIO(requests.get(file_url).content)
                try:
                    file_name = doc.file_name
                except:
                    file_name = file_info.file_path.replace("/", "_")
                    send_photo_warning = True
                upload_io = convertapi.UploadIO(file_data, filename=file_name)
                converted_result = convertapi.convert('pdf', {'File': upload_io})
                converted_files = converted_result.save_files(tempfile.gettempdir())

                for file in converted_files:
                    bot.send_document(message.chat.id, open(file, 'rb'))

            if send_photo_warning:
                bot.send_message(message.chat.id, 'You sent this file as a photo. If you require better quality, please send it as a document.')
        except:
            bot.send_message(message.chat.id, 'Connection Timeout Error.')


@bot.message_handler(commands=['stop'])
def stop(message):
    print(message.chat.first_name, " :", message.text)
    global RUN
    RUN=False
    bot.send_message(chat_id=message.chat.id, text="Stopped all threads.")

@bot.message_handler(commands=['meme'])
def send_memes(message):
    global RUN
    RUN = True
    print(message.chat.first_name, " :", message.text)
    subred = message.text.replace("/meme ", "").strip()
    subred = subred.lower()
    if subred == "/meme":
        subred = "memes"

    def get_memes(message, subred, limit=10000):
        global RUN
        subreddit = reddit.subreddit(subred)
        top = list(subreddit.top(limit=limit))
        for i in top:
            if not RUN:
                return
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

bot.polling(none_stop=True)
