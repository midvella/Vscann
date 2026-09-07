from settings.set_loging import write_log
write_log("[&] 'get_local_ip.py' dosyası çalıştırıldı")

import socket
from settings import set_themes as clr
from func import helper_func as hf

def get_local_ip():
    write_log("[~] 'get_local_ip()' fonksiyonu çalıştırıldı")
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8",80))
        print(f"\n{clr.s}[#] IP adresi alınıyor..{clr.r}")
        write_log("[#] IP adresi alınıyor..")
        ip = s.getsockname()[0]
        if ip == "127.0.0.1":
            print(f"{clr.k}[!] Ağ bağlantınızı kontrol edin!{clr.r}")
            write_log("[!] Ağ bağlantınızı kontrol edin!")
            hf.cık()
        print(f"{clr.s}[#] Bilinen IP adresi:{clr.r} [{ip}]")
        write_log(f"[#] Bilinen IP adresi: [{ip}]")
        return ip
    
    except socket.gaierror:
        print(f"{clr.k}[!] DNS çözümlenemedi! Ağ bağlantınızı kontrol edin{clr.r}")
        write_log("[!] DNS çözümlenemedi! Ağ bağlantınızı kontrol edin")
        hf.cık()
        
    except ConnectionError as ce:
        print(f"{clr.k}[!] Bağlantı hatası: {ce}{clr.r}")
        write_log(f"[!] Bağlantı hatası: {ce}")
        hf.cık()
    
    except OSError:
        print(f"{clr.k}[!] Ağ arabirimi bulunamadı! Ağ bağlantınızı kontrol edin{clr.r}")
        write_log("[!] Ağ arabirimi bulunamadı! Ağ bağlantınızı kontrol edin")
        hf.cık()
    
    except Exception as e:
        print(f"{clr.k}[!] Bilinmeyen hata oluştu: {e}{clr.r}")
        write_log(f"[!] Bilinmeyen hata oluştu: {e}")
        hf.cık()
        
    finally:
        s.close()
    return ip
