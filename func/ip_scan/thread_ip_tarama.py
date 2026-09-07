from settings.set_loging import write_log
write_log("[&] 'thread_ip_tarama.py' dosyası çalıştırıldı", level="EXEC")

import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from settings import set_themes as clr
from settings.set_lang import get_string
from func import helper_func as hf

# Thread-safe lock for aktif_ip listesi
ip_lock = threading.Lock()

from settings import set_scan_opt as scan_opt
THREAD_SAYISI = scan_opt.get_scan_opts()['threads']

def _tek_ip_ping(ip):
    """Tek bir IP'ye ping atar (thread worker fonksiyonu)
    
    Returns:
        tuple: (ip, sure) eğer aktif ise, None değilse
    """
    try:
        bas_sure = time.time()
        yanit = subprocess.call(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        son_sure = time.time() - bas_sure
        if yanit == 0:
            return (ip, f"{son_sure:.4f}")
    except Exception as e:
        write_log(f"[!] Ping hatası ({ip}): {e}", level="ERROR")
    return None

def thread_ping_tarama(ip_listesi):
    """IP listesini thread pool ile paralel ping tarar
    
    Args:
        ip_listesi: Taranacak IP adresleri listesi (str)
    
    Returns:
        list: (ip, sure) tuple'larından oluşan aktif IP listesi
    """
    write_log(f"[~] 'thread_ping_tarama()' fonksiyonu çalıştırıldı - {len(ip_listesi)} IP", level="FUNC")
    
    aktif_ip = []
    total = len(ip_listesi)
    completed = 0
    
    print(f"{clr.s}[#] {get_string('scan_started')} ({total} IP, {THREAD_SAYISI} thread)..{clr.r}\n")
    write_log(f"[#] Thread ping taraması başlatılıyor ({total} IP, {THREAD_SAYISI} thread)..", level="EXEC")
    
    with ThreadPoolExecutor(max_workers=THREAD_SAYISI) as executor:
        futures = {executor.submit(_tek_ip_ping, ip): ip for ip in ip_listesi}
        for future in as_completed(futures):
            completed += 1
            if hf.get_key():
                hf.show_progress(completed, total)
            try:
                sonuc = future.result()
                if sonuc is not None:
                    with ip_lock:
                        aktif_ip.append(sonuc)
                    write_log(f"[+] Aktif IP: {sonuc[0]} - Süre: {sonuc[1]}s", level="RESULT")
            except Exception as e:
                ip = futures[future]
                write_log(f"[!] Thread hatası ({ip}): {e}", level="ERROR")
    print() # New line after progress
    
    # IP adresine göre sırala
    import ipaddress
    aktif_ip.sort(key=lambda x: ipaddress.ip_address(x[0]))
    
    return aktif_ip
