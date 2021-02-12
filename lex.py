import requests

def send_to_telegram(chat,message,message_id):
        headers = {
    "Origin": "http://scriptlab.net",
    "Referer": "http://scriptlab.net/telegram/bots/gpt2robot/",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

        url     = "http://scriptlab.net/telegram/bots/gpt2robot/answer.php?chat="+str(chat)+"&message_id="+str(message_id)+"&text="+message
        requests.get(url,headers = headers)