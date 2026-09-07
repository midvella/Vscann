from settings.set_loging import write_log
write_log("[&] 'get_mac.py' dosyası çalıştırıldı", level="EXEC")

import os
import json
import subprocess
import re

# MAC OUI veritabanını yükle
_mac_db = {}
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db", "mac_oui_db.json")

def _load_mac_db():
    """MAC OUI veritabanını JSON dosyasından yükler"""
    global _mac_db
    if _mac_db:
        return _mac_db
    try:
        with open(_DB_PATH, "r", encoding="utf-8") as f:
            _mac_db = json.load(f)
        write_log(f"[#] MAC OUI DB yüklendi: {len(_mac_db)} kayıt", level="EXEC")
    except FileNotFoundError:
        write_log(f"[!] MAC OUI DB bulunamadı: {_DB_PATH}", level="ERROR")
    except Exception as e:
        write_log(f"[!] MAC OUI DB yükleme hatası: {e}", level="ERROR")
    return _mac_db

def _is_termux():
    """Termux ortamında olup olmadığını kontrol eder"""
    return os.environ.get("TERMUX_VERSION") is not None or os.path.exists("/data/data/com.termux")

def _is_root():
    """Root yetkisi kontrolü (basit)"""
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False

def get_mac_addr():
    """Yerel ağ arayüzlerinin MAC adreslerini döndürür (çoklu fallback)
    
    Deneme sırası:
    1. /sys/class/net/ (standart Linux)
    2. ip link show (Termux + Linux)
    3. ifconfig (eski sistemler)
    4. Termux WiFi API
    5. Root ile ip addr
    """
    write_log("[~] 'get_mac_addr()' fonksiyonu çalıştırıldı", level="FUNC")
    
    # 1. /sys/class/net/ ile MAC okuma (standart Linux)
    result = _get_mac_sysfs()
    if result[0]:
        return result
    
    # 2. ip link show ile MAC okuma
    result = _get_mac_ip_link()
    if result[0]:
        return result
    
    # 3. ifconfig ile MAC okuma
    result = _get_mac_ifconfig()
    if result[0]:
        return result
    
    # 4. Termux WiFi API
    if _is_termux():
        result = _get_mac_termux_wifi()
        if result[0]:
            return result
    
    # 5. Root ile ip addr
    if _is_root():
        result = _get_mac_root()
        if result[0]:
            return result
    
    write_log("[!] MAC adresi hiçbir yöntemle alınamadı", level="ERROR")
    return None, None

def _get_mac_sysfs():
    """/sys/class/net/ üzerinden MAC okuma"""
    try:
        interfaces = os.listdir('/sys/class/net/')
        for iface in interfaces:
            if iface == 'lo':
                continue
            try:
                with open(f'/sys/class/net/{iface}/address', 'r') as f:
                    mac = f.read().strip()
                    if mac and mac != "00:00:00:00:00:00":
                        write_log(f"[#] MAC alındı (sysfs): {iface} -> {mac}", level="EXEC")
                        return iface, mac
            except:
                pass
    except (FileNotFoundError, PermissionError):
        pass
    return None, None

def _get_mac_ip_link():
    """ip link show komutu ile MAC okuma"""
    try:
        result = subprocess.run(
            ["ip", "link", "show"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            # Format: 2: wlan0: <...>\n    link/ether aa:bb:cc:dd:ee:ff brd ...
            lines = result.stdout.splitlines()
            current_iface = None
            for line in lines:
                # Arayüz satırı
                iface_match = re.match(r'^\d+:\s+(\S+?):', line)
                if iface_match:
                    current_iface = iface_match.group(1)
                    if current_iface == 'lo':
                        current_iface = None
                        continue
                
                # MAC satırı
                if current_iface:
                    mac_match = re.search(r'link/ether\s+([0-9a-fA-F:]{17})', line)
                    if mac_match:
                        mac = mac_match.group(1)
                        if mac != "00:00:00:00:00:00":
                            write_log(f"[#] MAC alındı (ip link): {current_iface} -> {mac}", level="EXEC")
                            return current_iface, mac
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None, None

def _get_mac_ifconfig():
    """ifconfig komutu ile MAC okuma"""
    try:
        result = subprocess.run(
            ["ifconfig"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            current_iface = None
            for line in result.stdout.splitlines():
                # Arayüz satırı
                iface_match = re.match(r'^(\S+?)[\s:]', line)
                if iface_match:
                    iface = iface_match.group(1)
                    if iface != 'lo':
                        current_iface = iface
                    else:
                        current_iface = None
                
                if current_iface:
                    # ether aa:bb:cc:dd:ee:ff veya HWaddr aa:bb:cc:dd:ee:ff
                    mac_match = re.search(r'(?:ether|HWaddr)\s+([0-9a-fA-F:]{17})', line)
                    if mac_match:
                        mac = mac_match.group(1)
                        if mac != "00:00:00:00:00:00":
                            write_log(f"[#] MAC alındı (ifconfig): {current_iface} -> {mac}", level="EXEC")
                            return current_iface, mac
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None, None

def _get_mac_termux_wifi():
    """Termux WiFi API ile MAC okuma"""
    try:
        result = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            try:
                info = json.loads(result.stdout)
                mac = info.get("mac_address", "")
                if mac and mac != "02:00:00:00:00:00" and mac != "00:00:00:00:00:00":
                    write_log(f"[#] MAC alındı (termux-wifi): wlan0 -> {mac}", level="EXEC")
                    return "wlan0", mac
            except json.JSONDecodeError:
                pass
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None, None

def _get_mac_root():
    """Root yetkisi ile ip addr komutu kullanarak MAC okuma"""
    try:
        result = subprocess.run(
            ["ip", "addr"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            current_iface = None
            for line in result.stdout.splitlines():
                iface_match = re.match(r'^\d+:\s+(\S+?):', line)
                if iface_match:
                    current_iface = iface_match.group(1)
                    if current_iface == 'lo':
                        current_iface = None
                
                if current_iface:
                    mac_match = re.search(r'link/ether\s+([0-9a-fA-F:]{17})', line)
                    if mac_match:
                        mac = mac_match.group(1)
                        if mac != "00:00:00:00:00:00":
                            write_log(f"[#] MAC alındı (root ip addr): {current_iface} -> {mac}", level="EXEC")
                            return current_iface, mac
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None, None

def get_all_mac_addrs():
    """Tüm ağ arayüzlerinin MAC adreslerini döndürür (çoklu fallback)
    
    Returns:
        list: [(iface, mac)] listesi
    """
    write_log("[~] 'get_all_mac_addrs()' fonksiyonu çalıştırıldı", level="FUNC")
    sonuclar = []
    
    # 1. sysfs ile dene
    try:
        interfaces = os.listdir('/sys/class/net/')
        for iface in interfaces:
            if iface == 'lo':
                continue
            try:
                with open(f'/sys/class/net/{iface}/address', 'r') as f:
                    mac = f.read().strip()
                    if mac and mac != "00:00:00:00:00:00":
                        sonuclar.append((iface, mac))
            except:
                pass
    except (FileNotFoundError, PermissionError):
        pass
    
    if sonuclar:
        return sonuclar
    
    # 2. ip link show ile dene
    try:
        result = subprocess.run(
            ["ip", "link", "show"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            current_iface = None
            for line in result.stdout.splitlines():
                iface_match = re.match(r'^\d+:\s+(\S+?):', line)
                if iface_match:
                    current_iface = iface_match.group(1)
                    if current_iface == 'lo':
                        current_iface = None
                
                if current_iface:
                    mac_match = re.search(r'link/ether\s+([0-9a-fA-F:]{17})', line)
                    if mac_match:
                        mac = mac_match.group(1)
                        if mac != "00:00:00:00:00:00":
                            sonuclar.append((current_iface, mac))
                            current_iface = None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    if sonuclar:
        return sonuclar
    
    # 3. Termux WiFi
    if _is_termux():
        iface, mac = _get_mac_termux_wifi()
        if iface:
            sonuclar.append((iface, mac))
    
    return sonuclar

def try_get_remote_mac(ip):
    """Uzak bir IP'nin MAC adresini ARP tablosundan çekmeye çalışır
    
    Args:
        ip: Hedef IP adresi
    
    Returns:
        str: MAC adresi veya None
    """
    # 1. ARP tablosundan oku
    try:
        result = subprocess.run(
            ["arp", "-n", ip],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            mac_match = re.search(r'([0-9a-fA-F:]{17})', result.stdout)
            if mac_match:
                mac = mac_match.group(1)
                if mac != "00:00:00:00:00:00" and "(incomplete)" not in result.stdout:
                    return mac
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # 2. ip neigh ile dene
    try:
        result = subprocess.run(
            ["ip", "neigh", "show", ip],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            mac_match = re.search(r'([0-9a-fA-F:]{17})', result.stdout)
            if mac_match:
                return mac_match.group(1)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # 3. cat /proc/net/arp ile dene (Termux uyumlu)
    try:
        with open('/proc/net/arp', 'r') as f:
            for line in f.readlines()[1:]:  # Başlık satırını atla
                parts = line.split()
                if len(parts) >= 4 and parts[0] == ip:
                    mac = parts[3]
                    if mac != "00:00:00:00:00:00":
                        return mac
    except (FileNotFoundError, PermissionError):
        pass
    
    return None

def mac_to_vendor(mac_adresi):
    """MAC adresinden üretici/marka bilgisini döndürür
    
    Args:
        mac_adresi: MAC adresi (herhangi bir formatta: AA:BB:CC:DD:EE:FF veya aa-bb-cc-dd-ee-ff)
    
    Returns:
        str: Üretici adı veya "Bilinmeyen Üretici"
    """
    if not mac_adresi or mac_adresi == "N/A":
        return "Bilinmeyen Üretici"
    
    db = _load_mac_db()
    
    # MAC adresini normalize et (büyük harf, : ayracı)
    mac_temiz = mac_adresi.upper().replace("-", ":").replace(".", ":")
    
    # OUI prefix'i al (ilk 3 oktet: AA:BB:CC)
    parcalar = mac_temiz.split(":")
    if len(parcalar) >= 3:
        oui = ":".join(parcalar[:3])
        
        if oui in db:
            return db[oui]
    
    return "Bilinmeyen Üretici"

def get_mac_info_str(mac_adresi):
    """MAC adresi için okunabilir bilgi stringi döndürür"""
    vendor = mac_to_vendor(mac_adresi)
    return f"{mac_adresi} ({vendor})"

# Modül yüklendiğinde ilk MAC adresini al
iface, mac = get_mac_addr()
