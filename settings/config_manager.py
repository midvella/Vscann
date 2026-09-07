import os
import json

CONFIG_PATH = "config.json"

def get_real_user():
    sudo_uid = os.environ.get('SUDO_UID')
    sudo_gid = os.environ.get('SUDO_GID')
    return sudo_uid, sudo_gid

def enforce_ownership(filepath):
    """Eger program root olarak (sudo ile) calistirildiysa ve bu dosya yaratiliyorsa, asil kullaniciya devret."""
    sudo_uid, sudo_gid = get_real_user()
    if sudo_uid and sudo_gid:
        try:
            os.chown(filepath, int(sudo_uid), int(sudo_gid))
        except:
            pass

def test_permissions():
    """W_OK testi yapar. Yazma izni yoksa uyarir ve gecer."""
    paths_to_check = ['config.json', 'scann_log.txt']
    
    for path in paths_to_check:
        if os.path.exists(path) and not os.access(path, os.W_OK):
            print(f"\n\033[31m[!] UYARI: '{path}' dosyasina yazma erisimi reddedildi (Muhtemelen Root tarafindan olusturulmus).\033[0m")

def load():
    """Config dosyasini doner, eger yoksa bos bir dict doner."""
    if not os.path.exists(CONFIG_PATH):
        # Eger dosya yoksa ve write izni olan bise lazimsa, save({}).
        pass
    else:
        with open(CONFIG_PATH, "r") as f:
            try:
                return json.load(f)
            except Exception:
                pass
    return {}

def save(new_data: dict):
    """Config e yeni data yazar."""
    current = load()
    current.update(new_data)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(current, f, indent=4)
        enforce_ownership(CONFIG_PATH) # Sahipligi devret
    except PermissionError:
        pass
