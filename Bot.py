import telebot
import requests
from bs4 import BeautifulSoup
import praw
import random
import pickle
import convertapi
import tempfile
from io import BytesIO
from redvid import Downloader
import os
import time

API_KEY = ""
bot = telebot.TeleBot(API_KEY)
reddit=praw.Reddit(client_id='',client_secret='',username='',password='',user_agent='')
convertapi.api_secret = '66kpFfFS194MEvNN'
reddit_downloader = Downloader(max_q=True)
with open("subs.bin","rb") as f:
    subs = pickle.load(f) 
print("Bot is ready.")
RUN=True

@bot.message_handler(commands=['start'])
def start(message):
    o='''
    Commands :
    /search subreddit : Search Subreddit
    /meme subreddit : random memes from subreddit
    /memeall subreddit : All memes from a subreddit
    /stop : Stop memeall command
    /convert : converts files to pdf
    /clear :  clear bot's cache if slow
    '''
    bot.send_chat_action(chat_id=message.chat.id,action='typing')
    bot.send_message(chat_id=message.chat.id,text=o)

    
@bot.message_handler(commands=['search'])
def search(message):
    print(message.chat.first_name," :",message.text)
    subred = message.text.replace("/search ","").strip()
    subred=subred.lower()
    url='https://www.reddit.com/search/?q='+str(subred)
    result=requests.get(url, headers={'User-Agent': 'Bored programmer\'s bot'})
    src=result.content
    soup=BeautifulSoup(src,'html.parser')
    links=soup.find_all('a')
    subs=[]
    for i in links:
        if 'r/' in i.text:
            for j in i:
                if len(j.split())==1 and ('http' not in j):
                    subs.append(str(j))
    o=""
    for i in range(len(subs)):
        o=o+str(i+1)+") "+subs[i]+'\n'
    bot.send_message(chat_id=message.chat.id,text=o)
    

@bot.message_handler(commands=['meme'])
def send_memes(message):
    print(message.chat.first_name," :",message.text)
    subred = message.text.replace("/meme ","").strip()
    subred=subred.lower()
    if subred=="":
        subred="memes"
    if subred in subs:
        if len(subs[subred])==0:
            subreddit=reddit.subreddit(subred)
            top=subreddit.top(limit=9999)
            for i in top:
                subs[subred].append(i)
    else:
        subs[subred]=[]
        subreddit=reddit.subreddit(subred)
        top=subreddit.top(limit=9999)
        for i in top:
            subs[subred].append(i)
    random_sub=random.choice(subs[subred])
    subs[subred].remove(random_sub)
    with open("subs.bin","wb") as f:
        f.close()
    with open("subs.bin","wb") as f:
        pickle.dump(subs, f)
        f.close()
    name=random_sub.title
    url=str(random_sub.url)
    print(url)
    if "mp4" in url:
        bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
        bot.send_video(chat_id=message.chat.id,video=url)
    elif "v.redd" in url:
        reddit_downloader.url = url
        name=reddit_downloader.download()
        bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
        bot.send_video(chat_id=message.chat.id, video=open(name, 'rb'), supports_streaming=True)
        os.remove(name)
    elif "gif" in url:
        bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
        bot.send_animation(chat_id=message.chat.id,animation=url)
    else:
        bot.send_chat_action(chat_id=message.chat.id,action='upload_photo')
        bot.send_photo(chat_id = message.chat.id , photo=url)
    # except: 
    #     bot.send_message(chat_id=message.chat.id,text="Some Error Occured. \n"+url)
    
@bot.message_handler(content_types=['document', 'photo'])#func=lambda message: message.caption == '/convert')
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

@bot.message_handler(commands=['memeall'])
def send_all_memes(message):
    global RUN
    print(message.chat.first_name," :",message.text)
    subred = message.text.replace("/memeall ","").strip()
    if subred=="": subred="memes"
    subreddit=reddit.subreddit(subred)
    top=subreddit.top(limit=9999)
    count=0
    RUN=True
    for i in top:
        if not RUN:
            break
        time.sleep(3)
        count+=1
        url=str(i.url)
        name=i.title
        bot.send_chat_action(chat_id=message.chat.id,action='typing')
        bot.send_message(chat_id=message.chat.id,text=name)
        try:
            if "mp4" in url:
                bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
                bot.send_video(chat_id=message.chat.id,video=url)

            elif "v.redd" in url:
                reddit_downloader.url = url
                name=reddit_downloader.download()
                bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
                bot.send_video(chat_id=message.chat.id, video=open(name, 'rb'), supports_streaming=True)
                os.remove(name)

            elif "gif" in url:
                bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
                bot.send_animation(chat_id=message.chat.id,animation=url)
            else:
                bot.send_chat_action(chat_id=message.chat.id,action='upload_photo')
                bot.send_photo(chat_id = message.chat.id , photo=url)
        except: pass
    bot.send_chat_action(chat_id=message.chat.id,action='typing')
    bot.send_message(chat_id=message.chat.id,text="Total :"+str(count))

@bot.message_handler(commands=['stop'])
def stop_all_memes(message):
    global RUN
    print(message.chat.first_name," :",message.text)
    RUN=False

@bot.message_handler(commands=['clear'])
def clear(message):
    print(message.chat.first_name," :",message.text)
    subs={}
    with open("subs.bin","wb") as f:
        f.close()
    with open("subs.bin","wb") as f:
        pickle.dump(subs, f)
        f.close()
    for i in os.listdir():
        if i.endswith(".mp4"):
            os.rmdir(i)
    bot.send_chat_action(chat_id=message.chat.id,action='typing')
    bot.send_message(chat_id=message.chat.id,text="All Cache Files Cleared !")

bot.infinity_polling()
