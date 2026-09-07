from settings.set_loging import write_log
write_log("[&] 'get_service_name.py' dosyası çalıştırıldı", level="EXEC")

import socket
import json
import os

# Lokal servis veritabanını yükle
_servis_db = {}
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db", "servis_db.json")

def _load_servis_db():
    """Servis veritabanını JSON dosyasından yükler"""
    global _servis_db
    if _servis_db:
        return _servis_db
    try:
        with open(_DB_PATH, "r", encoding="utf-8") as f:
            _servis_db = json.load(f)
        write_log(f"[#] Servis DB yüklendi: {len(_servis_db)} kayıt", level="EXEC")
    except FileNotFoundError:
        write_log(f"[!] Servis DB bulunamadı: {_DB_PATH}", level="ERROR")
    except Exception as e:
        write_log(f"[!] Servis DB yükleme hatası: {e}", level="ERROR")
    return _servis_db

def get_service_name(port):
    """Port numarasından servis adını döndürür (lokal DB + socket fallback)"""
    db = _load_servis_db()
    port_str = str(port)
    
    if port_str in db:
        bilgi = db[port_str]
        return bilgi["servis"]
    
    # Fallback: socket modülü
    try:
        return socket.getservbyport(port)
    except:
        return "Bilinmeyen servis"

def get_service_detail(port):
    """Port numarasından detaylı servis bilgisi döndürür
    
    Returns:
        dict: {"servis": str, "protokol": str, "aciklama": str} veya None
    """
    db = _load_servis_db()
    port_str = str(port)
    
    if port_str in db:
        return db[port_str]
    
    # Fallback: socket ile sadece isim
    try:
        isim = socket.getservbyport(port)
        return {"servis": isim, "protokol": "tcp", "aciklama": "Sistem veritabanından"}
    except:
        return None

def get_service_info_str(port):
    """Port için okunabilir servis bilgisi stringi döndürür"""
    detay = get_service_detail(port)
    if detay:
        return f"{detay['servis']} ({detay['protokol']}) - {detay['aciklama']}"
    return "Bilinmeyen servis"