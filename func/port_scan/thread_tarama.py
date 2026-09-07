from settings.set_loging import write_log
write_log("[&] 'thread_tarama.py' dosyası çalıştırıldı", level="EXEC")

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from func.port_scan import port_taraması as p_tsı
from settings import set_themes as clr
from settings.set_lang import get_string
from func import helper_func as hf

# Thread-safe lock for acık_port listesi
port_lock = threading.Lock()

def localhost_mu(ip):
    """IP'nin localhost olup olmadığını kontrol eder"""
    write_log(f"[~] 'localhost_mu()' fonksiyonu çalıştırıldı - IP: {ip}", level="FUNC")
    localhost_adresleri = ["127.0.0.1", "localhost", "::1", "0.0.0.0"]
    return ip.strip().lower() in localhost_adresleri

def thread_sayisi_belirle(ip):
    """Localhost ise 300, değilse 100 thread döndürür"""
    write_log(f"[~] 'thread_sayisi_belirle()' fonksiyonu çalıştırıldı - IP: {ip}", level="FUNC")
    if localhost_mu(ip):
        thread_sayisi = 300
    else:
        thread_sayisi = 100
    print(f"{clr.s}[#] {get_string('threads')}: {thread_sayisi}{clr.r}")
    write_log(f"[#] Thread sayısı: {thread_sayisi}", level="EXEC")
    return thread_sayisi

def thread_port_tarama(ip, port_listesi, timeout=0.5, max_workers=None, scanner_func=p_tsı.port_taraması):
    """Verilen port listesini thread pool ile paralel tarar"""
    write_log(f"[~] 'thread_port_tarama()' fonksiyonu çalıştırıldı - IP: {ip}", level="FUNC")
    
    if max_workers is None:
        thread_sayisi = thread_sayisi_belirle(ip)
    else:
        thread_sayisi = max_workers
        print(f"{clr.s}[#] Thread sayısı: {thread_sayisi}{clr.r}")
    
    total = len(port_listesi)
    completed = 0
    results = []
    
    print(f"{clr.s}[#] {get_string('scan_started')} ({total} port, {thread_sayisi} thread)..{clr.r}\n")
    write_log(f"[#] Tarama başlatılıyor ({total} port, {thread_sayisi} thread)..", level="EXEC")
    
    with ThreadPoolExecutor(max_workers=thread_sayisi) as executor:
        futures = {executor.submit(scanner_func, ip, port, timeout): port for port in port_listesi}
        for future in as_completed(futures):
            completed += 1
            if hf.get_key():
                hf.show_progress(completed, total)
            try:
                res = future.result()
                results.append(res)
            except Exception as e:
                port = futures[future]
                write_log(f"[!] Thread hatası - Port {port}: {e}", level="ERROR")
    
    print() # Progress bar bitişi
    return results
