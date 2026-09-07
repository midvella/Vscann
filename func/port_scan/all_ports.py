from settings.set_loging import write_log
write_log("[&] 'all_ports.py' dosyası çalıştırıldı", level="EXEC")

from datetime import datetime as dt
from func import helper_func as hf
from func.port_scan import ping_control as ping
from func.port_scan import port_taraması as p_tsı
from func.port_scan import thread_tarama as t_tara
from func.port_scan import servis_tespit as st
from settings import set_themes as clr
from settings.set_lang import get_string

acık_port=p_tsı.acık_port
port_list=[]

def tum_portlar(hedef_ip=None, timeout=0.5, max_workers=None, scanner_func=None, os_discovery=False, verbose=False):
          write_log("[~] 'tum_portlar()' fonksiyonu çalıştırıldı", level="FUNC")
          if not hedef_ip:
              hedef_ip=input(f"{clr.am4}[$] {get_string('target_ip')}: {clr.r}")
          
          write_log(f"[$] {get_string('target_ip')}: {hedef_ip}", level="EXEC")
          ping.ping_kontrol(hedef_ip)
          
          port_listesi = list(range(0, 65536))
          
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
          print(f"\n{clr.am}{get_string('total_scanned')}:{clr.r} 65535 {clr.am}{get_string('open_port_count')}:{clr.r} {len(acık_liste)}\n{clr.am}{get_string('target_ip')}:{clr.r} {hedef_ip} {clr.am}{get_string('duration')}:{clr.r} {tson_sure}")
          write_log(f"[#] {get_string('total_scanned')}: 65535 | {get_string('open_port_count')}: {len(acık_liste)} | {get_string('target_ip')}: {hedef_ip} | {get_string('duration')}: {tson_sure}", level="RESULT")
          
          if not acık_liste:
                print(f"\n{clr.am}[*] {get_string('open_ports_list')}:{clr.r} ")
                write_log(f"[*] {get_string('open_ports_list')}:", level="RESULT")
                print(f"\t{clr.k}$$------------{get_string('no_open_ports')}------------$${clr.r}") 
                write_log(f"$$------------{get_string('no_open_ports')}------------$$", level="RESULT")
          else:
                print(f"\n{clr.am}[*] {get_string('open_ports_list')}:{clr.r} ")
                write_log(f"[*] {get_string('open_ports_list')}: ", level="RESULT")
                print(f"\n\t{clr.s}[~] {get_string('service_detecting')}{clr.r}\n")
                write_log(f"[~] {get_string('service_detecting')}", level="FUNC")
                for port, son_time in acık_liste:
                    sonuc = st.servis_tespit(hedef_ip, port)
                    st.sonuc_yazdir(sonuc, son_time)
          write_log("======================================================", level="EXEC")

