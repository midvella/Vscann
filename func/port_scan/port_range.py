from settings.set_loging import write_log
write_log("[&] 'port_range.py' dosyası çalıştırıldı")
from datetime import datetime as dt

from func.port_scan import ping_control as ping
from func import helper_func as hf
from func.port_scan import port_taraması as p_tsı
from func.port_scan import thread_tarama as t_tara
from func.port_scan import servis_tespit as st
from settings import set_themes as clr
from settings.set_lang import get_string

acık_port=p_tsı.acık_port
port_list=[]

def port_range(hedef_ip=None, baslangıc_port=None, bitis_port=None, timeout=0.5, max_workers=None, scanner_func=None, os_discovery=False, verbose=False):
        write_log("[~] 'port_range()' fonksiyonu çalıştırıldı", level="FUNC")
        
        if not hedef_ip:
            hedef_ip=input(f"{clr.am}[$] {get_string('target_ip')}: {clr.r}") 
        
        write_log(f"[$] {get_string('target_ip')}: {hedef_ip}", level="EXEC")
        ping.ping_kontrol(hedef_ip)
        
        if baslangıc_port is None:
            try:
                baslangıc_port=int(input(f"{clr.am}[$] {get_string('start_port')}:{clr.r} "))
            except:
                print(f"{clr.k}[!] {get_string('invalid_port')}{clr.r}")
                write_log(f"[!] {get_string('invalid_port')}\n", level="ERROR")
                return
        
        write_log(f"[$] {get_string('start_port')}: {baslangıc_port}", level="EXEC")
        hf.bas_port_kontrol(baslangıc_port)
        
        if bitis_port is None:
            try:
                bitis_port=int(input(f"{clr.am}[$] {get_string('end_port')}: {clr.r}"))
            except:
                print(f"{clr.k}[!] {get_string('invalid_port')}{clr.r}")
                write_log(f"[!] {get_string('invalid_port')}", level="ERROR")
                return
                
        write_log(f"[$] {get_string('end_port')}: {bitis_port}", level="EXEC")
        hf.bit_port_kontrol(bitis_port)
        
        if baslangıc_port > bitis_port:
            port_listesi = list(range(bitis_port, baslangıc_port+1))
            toplam = baslangıc_port - bitis_port + 1
            aralik_str = f"{bitis_port}-{baslangıc_port}"
        else:
            port_listesi = list(range(baslangıc_port, bitis_port+1))
            toplam = bitis_port - baslangıc_port + 1
            aralik_str = f"{baslangıc_port}-{bitis_port}"
        
        # OS Discovery
        if os_discovery:
            from func.port_scan import os_discovery as osd
            osd.print_os_info(hedef_ip)

        # Clear global list
        p_tsı.acık_port.clear()
        
        tsure = dt.now()
        results = t_tara.thread_port_tarama(hedef_ip, port_listesi, timeout=timeout, max_workers=max_workers, scanner_func=scanner_func or p_tsı.port_taraması)
        tson_sure = dt.now() - tsure
        
        from func import output_handler as oh
        if verbose:
            print(f"\n{clr.s}[#] Tüm Port Sonuçları:{clr.r}")
            for r in results:
                oh.print_verbose_result(r)

        acık_liste = sorted(p_tsı.acık_port, key=lambda x: x[0])
        
        print(f"\n\t{clr.y}$$--------------{get_string('scan_completed')}--------------$${clr.r}") 
        write_log(f"[#] $$--------------{get_string('scan_completed')}--------------$$", level="RESULT")
        print(f"\n{clr.am}{get_string('total_scanned')}:{clr.r} {toplam} {clr.am}{get_string('open_port_count')}:{clr.r} {len(acık_liste)}\n{clr.am}{get_string('port_range_label')}:{clr.r} {aralik_str}\n{clr.am}{get_string('target_ip')}:{clr.r} {hedef_ip} {clr.am}{get_string('duration')}:{clr.r} {tson_sure}")
        write_log(f"{get_string('total_scanned')}: {toplam} | {get_string('open_port_count')}: {len(acık_liste)} | {get_string('port_range_label')}: {aralik_str} | {get_string('target_ip')}: {hedef_ip} | {get_string('duration')}: {tson_sure}", level="RESULT")
        
        if not acık_liste:
            print(f"\n{clr.am}[*] {get_string('open_ports_list')}:{clr.r} ")
            write_log(f"[*] {get_string('open_ports_list')}:", level="RESULT") 
            print(f"\t{clr.k}$$------------{get_string('no_open_ports')}------------$${clr.r}") 
            write_log(f"\t$$------------{get_string('no_open_ports')}------------$$", level="RESULT")
        else:
            print(f"\n{clr.am}[*] {get_string('open_ports_list')}:{clr.r} ")
            write_log(f"[*] {get_string('open_ports_list')}:", level="RESULT")
            print(f"\n\t{clr.s}[~] {get_string('service_detecting')}{clr.r}\n")
            write_log(f"[~] {get_string('service_detecting')}", level="FUNC")
            for port, son_time in acık_liste:
                sonuc = st.servis_tespit(hedef_ip, port)
                st.sonuc_yazdir(sonuc, son_time)
        write_log("======================================================", level="EXEC")

