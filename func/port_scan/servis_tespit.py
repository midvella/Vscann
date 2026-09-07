from settings.set_loging import write_log
write_log("[&] 'servis_tespit.py' dosyası çalıştırıldı", level="EXEC")

import json
import os
import re
import threading
from func.port_scan.banner_gb import banner_grabbing, versiyon_cikar, BANNER_PATTERNS
from func.port_scan.get_service_name import get_service_detail
from settings import set_themes as clr
from settings.set_lang import get_string

# Veritabanı yolu
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db", "servis_db.json")
_db_lock = threading.Lock()

def _load_db():
    """Servis veritabanını yükler"""
    try:
        with open(_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        write_log(f"[!] Servis DB yükleme hatası: {e}", level="ERROR")
        return {}

def _save_db(db):
    """Servis veritabanını kaydeder"""
    try:
        with open(_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
        write_log(f"[#] Servis DB güncellendi: {len(db)} kayıt", level="EXEC")
    except Exception as e:
        write_log(f"[!] Servis DB kaydetme hatası: {e}", level="ERROR")

def _db_pattern_eslestir(banner, port_bilgisi):
    """Veritabanındaki banner_patterns ile eşleştirme yapar.
    
    Returns:
        (uygulama, versiyon) veya (None, None)
    """
    patterns = port_bilgisi.get("banner_patterns", [])
    if not patterns:
        return None, None
    
    for p in patterns:
        match = re.search(p["pattern"], banner, re.IGNORECASE)
        if match:
            uygulama = p["uygulama"]
            versiyon_grubu = p.get("versiyon_grubu", 0)
            if versiyon_grubu > 0 and match.lastindex and match.lastindex >= versiyon_grubu:
                versiyon = match.group(versiyon_grubu)
            else:
                versiyon = None
            return uygulama, versiyon
    
    return None, None

def _banner_pattern_eslestir(banner):
    """banner_gb.py'deki genel BANNER_PATTERNS ile eşleştirme yapar.
    
    Returns:
        servis_adi veya None
    """
    for pattern, servis_adi in BANNER_PATTERNS:
        if re.search(pattern, banner, re.IGNORECASE):
            return servis_adi
    return None

def _bilinmeyen_servisi_ekle(port, banner):
    """Bilinmeyen servisi veritabanına ekler"""
    port_str = str(port)
    
    with _db_lock:
        db = _load_db()
        if port_str in db:
            return False
        
        # Banner'dan ilk satırı al
        ilk_satir = banner.split("\n")[0][:80] if banner else "Bilinmeyen"
        
        db[port_str] = {
            "servis": f"Port-{port}",
            "protokol": "tcp",
            "aciklama": f"Auto-added - {ilk_satir}",
            "banner_patterns": []
        }
        _save_db(db)
        write_log(f"[+] Yeni servis eklendi: Port {port} - {ilk_satir}", level="EXEC")
    return True

def servis_tespit(ip, port):
    """Port için servis, uygulama ve versiyon tespiti yapar.
    
    Banner grabbing + DB karşılaştırma + otomatik ekleme.
    
    Returns:
        dict: {
            "port": int,
            "servis": str,
            "uygulama": str,
            "versiyon": str,
            "banner": str,
            "kaynak": str  -> "db_pattern" | "banner_pattern" | "db_temel" | "bilinmeyen"
            "db_eklendi": bool
        }
    """
    sonuc = {
        "port": port,
        "servis": get_string('unknown'),
        "uygulama": "",
        "versiyon": "",
        "banner": "",
        "kaynak": "bilinmeyen",
        "db_eklendi": False
    }
    
    # 1. Banner al
    banner = banner_grabbing(ip, port)
    sonuc["banner"] = banner
    
    # 2. DB'den port bilgisini çek
    port_bilgisi = get_service_detail(port)
    
    if port_bilgisi:
        sonuc["servis"] = port_bilgisi["servis"]
        sonuc["kaynak"] = "db_temel"
    
    # 3. Banner alınabildiyse pattern eşleştirme yap
    if banner and not banner.startswith("Banner alınamadı"):
        
        # 3a. DB banner_patterns ile eşleştir
        if port_bilgisi:
            uygulama, versiyon = _db_pattern_eslestir(banner, port_bilgisi)
            if uygulama:
                sonuc["uygulama"] = uygulama
                sonuc["versiyon"] = versiyon or ""
                sonuc["kaynak"] = "db_pattern"
                return sonuc
        
        # 3b. Genel BANNER_PATTERNS ile eşleştir
        genel_servis = _banner_pattern_eslestir(banner)
        if genel_servis:
            sonuc["uygulama"] = genel_servis
            sonuc["kaynak"] = "banner_pattern"
            
            # Genel versiyon çıkarma dene
            v = versiyon_cikar(banner)
            if v:
                sonuc["versiyon"] = v
            return sonuc
        
        # 3c. Banner var ama eşleşme yok -> genel versiyon çıkar
        v = versiyon_cikar(banner)
        if v:
            sonuc["versiyon"] = v
        
        # 4. DB'de yoksa otomatik ekle
        if not port_bilgisi:
            eklendi = _bilinmeyen_servisi_ekle(port, banner)
            sonuc["db_eklendi"] = eklendi
    
    elif not port_bilgisi:
        # Banner alınamadı ve DB'de de yok
        sonuc["servis"] = "Bilinmeyen"
    
    return sonuc

def sonuc_yazdir(sonuc, son_time):
    """Servis tespit sonucunu formatlanmış şekilde yazdırır.
    
    Args:
        sonuc: servis_tespit() dönüş değeri
        son_time: port tarama süresi string
    """
    port = sonuc["port"]
    servis = sonuc["servis"]
    uygulama = sonuc["uygulama"]
    versiyon = sonuc["versiyon"]
    db_eklendi = sonuc["db_eklendi"]
    
    # Uygulama + versiyon birleştir
    if uygulama and versiyon:
        uygulama_str = f"{uygulama} {versiyon}"
    elif uygulama:
        uygulama_str = uygulama
    else:
        uygulama_str = "-"
    
    # Ekleme notu
    ek_not = f" {clr.am3}{get_string('added_to_db')}{clr.r}" if db_eklendi else ""
    
    # Çıktı
    cikti = (
        f"\t\033[32m[-] Port:{clr.r} {port:<6}"
        f"\033[32m| Servis:{clr.r} {servis:<15}"
        f"\033[32m| {get_string('application')}:{clr.r} {uygulama_str:<25}"
        f"\033[32m| {get_string('duration')}:{clr.r} {son_time}"
        f"{ek_not}"
    )
    print(cikti)
    
    log_str = (
        f"\t[-] Port: {port} | Servis: {servis} "
        f"| {get_string('application')}: {uygulama_str} | {get_string('duration')}: {son_time}"
    )
    if db_eklendi:
        log_str += f" {get_string('added_to_db')}"
    write_log(log_str, level="RESULT")
