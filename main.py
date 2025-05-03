import requests
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning
from telethon.sync import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#########################
api_id = 00000000
api_hash = ''
vk_url = ''
defaultabout = ''
#########################

def get_current_track(vk_url):
    url = f'https://vk.com/{vk_url}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'}

    try:
        response = requests.get(url, headers=headers, verify=False)
        raw_data = response.text
        match = re.search(r'"status_audio":\s*({.*?})(?=,\s*["\'])', raw_data, re.DOTALL)
        if not match:
            return None, None
        json_str = match.group(1).strip()
        try:
            audio_data = json.loads(json_str)
        except json.JSONDecodeError:
            audio_data = json.loads(json_str + '}') 

        artist = audio_data.get('artist', None)
        title = audio_data.get('title', None)

        return artist, title

    except Exception as e:
        print(f"Ошибка при получении трека: {str(e)}")
        return None, None

client = TelegramClient('session', api_id, api_hash)

async def main():
    await client.start()
    user = await client.get_me()
    print(f"Telegram: {user.first_name} (@{user.username})")
    last_status = None

    while True:
        artist, title = get_current_track(vk_url)
        if artist and title and artist != "N/A" and title != "N/A":
            status = f"🎧 Слушает в VK Music: {artist} - {title}"
            print(f"Сейчас играет: {artist} - {title}")
        else:
            status = defaultabout
            print("Сейчас ничего не играет")
        if status != last_status:
            await client(UpdateProfileRequest(about=status))
            print("Статус Telegram обновлён")
            last_status = status
            
        time.sleep(10)

with client:
    client.loop.run_until_complete(main())
