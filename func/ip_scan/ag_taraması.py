from settings.set_loging import write_log
write_log("[&] 'ag_taraması.py' dosyası çalıştırıldı", level="EXEC")

import ipaddress
from func.ip_scan import get_local_ip as get_ip
from func.ip_scan import arp_tarama as arp
from func.ip_scan import thread_ip_tarama as t_ip
from func.ip_scan import get_mac
from settings import set_themes as clr
from settings.set_lang import get_string
from func import helper_func as hf
from datetime import datetime as dt

def ag_taraması(target_ip=None):
    write_log("[~] 'ag_taraması()' fonksiyonu çalıştırıldı", level="FUNC")
    if target_ip:
        try:
            net = ipaddress.ip_network(target_ip, strict=False)
        except ValueError:
            print(f"{clr.k}[!] Geçersiz IP/Ağ adresi: {target_ip}{clr.r}")
            write_log(f"[!] Geçersiz IP/Ağ adresi: {target_ip}", level="ERROR")
            return
    else:
        local_ip = get_ip.get_local_ip()
        net = ipaddress.ip_network(local_ip + "/24", strict=False)
    
    ag_adresi = str(net)
    
    print(f"{clr.s}[#] {get_string('network_scan_title')} {clr.r}\n")
    write_log(f"[#] {get_string('network_scan_title')}", level="EXEC")
    
    tsure = dt.now()
    
    # Root kontrolü: root ise ARP, değilse thread ping
    if arp.root_mu():
        print(f"{clr.y}[+] {get_string('root_detected_arp')}{clr.r}\n")
        write_log(f"[+] {get_string('root_detected_arp')}", level="EXEC")
        
        aktif_cihazlar = arp.arp_tara(ag_adresi)
        tson_sure = dt.now() - tsure
        
        print(f"\n\t{clr.y}$$--------------{get_string('scan_completed')}--------------$${clr.r}") 
        write_log(f"[#] $$--------------{get_string('scan_completed')}--------------$$", level="RESULT")
        
        if not aktif_cihazlar:
            print(f"\n{clr.am}{get_string('active_devices')}: {clr.r}")
            write_log(f"\n{get_string('active_devices')}: ", level="RESULT")
            print(f"\t{clr.k}$$------------{get_string('no_active_devices')}------------$${clr.r}")
            write_log(f"\t$$------------{get_string('no_active_devices')}------------$$", level="RESULT")
        else:
            print(f"\n{clr.am}{get_string('active_device_count')}:{clr.r} {len(aktif_cihazlar)} {clr.am}{get_string('duration')}:{clr.r} {tson_sure}\n")
            write_log(f"{get_string('active_device_count')}: {len(aktif_cihazlar)} | {get_string('duration')}: {tson_sure}", level="RESULT")
            print(f"{clr.am}{get_string('active_devices')}: {clr.r}")
            write_log(f"\n{get_string('active_devices')}: ", level="RESULT")
            for ip, mac in aktif_cihazlar:
                vendor = get_mac.mac_to_vendor(mac)
                print(f"\t{clr.y}[+] {ip} - MAC: {mac} ({vendor}){clr.r}")
                write_log(f"\t[+] {ip} - MAC: {mac} ({vendor})", level="RESULT")
    else:
        print(f"{clr.s}[#] {get_string('no_root_ping')}{clr.r}\n")
        write_log(f"[#] {get_string('no_root_ping')}", level="EXEC")
        
        ip_listesi = [str(ip) for ip in net.hosts()]
        aktif_ip = t_ip.thread_ping_tarama(ip_listesi)
        tson_sure = dt.now() - tsure
        
        print(f"\n\t{clr.y}$$--------------{get_string('scan_completed')}--------------$${clr.r}") 
        write_log(f"[#] $$--------------{get_string('scan_completed')}--------------$$", level="RESULT")
        
        if not aktif_ip:
            print(f"\n{clr.am}{get_string('active_devices')}: {clr.r}")
            write_log(f"\n{get_string('active_devices')}: ", level="RESULT")
            print(f"\t{clr.k}$$------------{get_string('no_active_devices')}------------$${clr.r}")
            write_log(f"\t$$------------{get_string('no_active_devices')}------------$$", level="RESULT")
        else:
            print(f"\n{clr.am}{get_string('active_device_count')}:{clr.r} {len(aktif_ip)} {clr.am}{get_string('duration')}:{clr.r} {tson_sure}\n")
            write_log(f"{get_string('active_device_count')}: {len(aktif_ip)} | {get_string('duration')}: {tson_sure}", level="RESULT")
            print(f"{clr.am}{get_string('active_devices')}: {clr.r}")
            write_log(f"\n{get_string('active_devices')}: ", level="RESULT")
            for ip, son_sure in aktif_ip:
                # MAC adresi çekmeye çalış
                mac_str = get_mac.try_get_remote_mac(ip)
                if mac_str:
                    vendor = get_mac.mac_to_vendor(mac_str)
                    print(f"\t{clr.y}[+] {ip} - MAC: {mac_str} ({vendor}) - {get_string('duration')}: {son_sure}s{clr.r}")
                    write_log(f"\t[+] {ip} - MAC: {mac_str} ({vendor}) - {get_string('duration')}: {son_sure}s", level="RESULT")
                else:
                    print(f"\t{clr.y}[+] {ip} - {get_string('duration')}: {son_sure}s{clr.r}")
                    write_log(f"\t[+] {ip} - {get_string('duration')}: {son_sure}s", level="RESULT")
    
    write_log("======================================================", level="EXEC")
    return
