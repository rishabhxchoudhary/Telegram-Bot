import telebot
import requests
from bs4 import BeautifulSoup
import praw
import random
import pickle
import convertapi
import tempfile
from io import BytesIO
# from redvid import Downloader
import os
import time

http_proxy  = "http://10.10.1.10:3128"
https_proxy = "https://10.10.1.11:1080"
ftp_proxy   = "ftp://10.10.1.10:3128"

proxyDict = { 
              "http"  : http_proxy, 
              "https" : https_proxy, 
              "ftp"   : ftp_proxy
            }

API_KEY = "5215172336:AAExMMURMmx-VoOiqj68thVmLJTFrb67gZc"
bot = telebot.TeleBot(API_KEY)
reddit=praw.Reddit(client_id='66VIObVPndtbig',client_secret='nIfN5ibuzs-giWCNCZ3s1dtZoj6YYw',username='RK26072003',password='PYTHON123',user_agent='RK')
convertapi.api_secret = '66kpFfFS194MEvNN'
# reddit_downloader = Downloader(max_q=True)
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
    try:
        if "redgif" in url or "gfycat" in url:
            r = requests.get(url)
            soup = BeautifulSoup(r.content,"html.parser")
            l = soup.find_all(property="og:video")
            url = l[-1]["content"]
            # print(url)
        if "imgur" in url:
            url = url.replace("gifv","mp4")
            # print(url)

    except: bot.send_message(chat_id=message.chat.id,text="Error")
    bot.send_chat_action(chat_id=message.chat.id,action='typing')
    bot.send_message(chat_id=message.chat.id,text=name)
    # try:
    if "mp4" in url:
        bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
        bot.send_video(chat_id=message.chat.id,video=url)
    elif "v.redd" in url:
        # reddit_downloader.url = url
        # name=reddit_downloader.download()
        url = url+".json"
        print("URL :",url)
        r = requests.get(url,headers={"User-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"})
        data = r.json()[0]
        video_url = data["data"]['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
        print("Video URL : ",video_url)
        audio_url = "https://v.redd.it/"+video_url.split("/")[3]+"/DASH_audio.mp4"
        with open("video.mp4","wb") as f:
            g = requests.get(video_url,stream=True)
            f.write(g.content)
        with open("audio.mp3","wb") as f:
            g = requests.get(audio_url,stream=True)
            f.write(g.content)
        os.system("ffmpeg -i video.mp4 -i audio.mp3 -c copy output.mp4")
        bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
        bot.send_video(chat_id=message.chat.id, video=open("output.mp4", 'rb'), supports_streaming=True)
        os.remove("video.mp4")
        os.remove("audio.mp3")
        os.remove("output.mp4")
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
        if "redgif" in url or "gfycat" in url:
            r = requests.get(url)
            soup = BeautifulSoup(r.content,"html.parser")
            l = soup.find_all(property="og:video")
            try:
                url = l[-1]["content"]
            except: pass
            # print(url)
        if "imgur" in url:
            url = url.replace("gifv","mp4")
            # print(url)
        bot.send_chat_action(chat_id=message.chat.id,action='typing')
        bot.send_message(chat_id=message.chat.id,text=name)
        try:
            if "mp4" in url:
                bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
                bot.send_video(chat_id=message.chat.id,video=url)

            elif "v.redd" in url:
                # reddit_downloader.url = url
                # name=reddit_downloader.download()
                url = url+".json"
                print(url)
                r = requests.get(url,headers={"User-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"})
                data = r.json()[0]
                video_url = data["data"]['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
                print(video_url)
                audio_url = "https://v.redd.it/"+video_url.split("/")[3]+"/DASH_audio.mp4"
                with open("video.mp4","wb") as f:
                    g = requests.get(video_url,stream=True)
                    f.write(g.content)
                with open("audio.mp3","wb") as f:
                    g = requests.get(audio_url,stream=True)
                    f.write(g.content)
                os.system("ffmpeg -i video.mp4 -i audio.mp3 -c copy output.mp4")
                bot.send_chat_action(chat_id=message.chat.id,action='upload_video')
                bot.send_video(chat_id=message.chat.id, video=open("output.mp4", 'rb'), supports_streaming=True)
                os.remove("video.mp4")
                os.remove("audio.mp3")
                os.remove("output.mp4")
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
