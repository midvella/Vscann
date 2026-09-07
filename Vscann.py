# Permissions checking during boot disabled to prevent permission denied loops when root owns it

from settings import set_themes as clr
from settings.set_loging import write_log
write_log("[&] 'Vscann.py' dosyası çalıştırıldı", level="EXEC")

from os import system
import sys,subprocess,help,os
from datetime import datetime
from func.helper_func import Vbanner
from func import helper_func as hf
from settings import set_lang as lang
from settings.set_lang import get_string
from settings import set_opt
from func.port_scan import pscan_menu as pmenu
from func.ip_scan import ipscan_menu as ip_menu
from func.ip_scan import ag_taraması as agt
from func.port_scan import port_range as pr
from func.port_scan import secili_port as sp
from func.port_scan import standart as std
from func.port_scan import port_taraması as p_tsı
from func.port_scan import all_ports as ap
from func.deauth import deauth_menu as dm

def main_menu():
     write_log("[~] 'main_menu()' fonksiyonu çalıştırıldı", level="FUNC")
     system("cls||clear")
     Vbanner()
     try:
          print(f"""
{clr.am6}======================================================
{clr.am6}                  ███ {get_string('main_menu_title')} ███
{clr.am7}======================================================

{clr.am6}[1] {get_string('port_scan')}
{clr.am5}[2] {get_string('network_scan')}
{clr.am4}[3] {get_string('deauth_attack')}
{clr.am3}[4] {get_string('settings')}
{clr.am2}[5] {get_string('help')}
{clr.am}------------------------------------------------------
{clr.am2}[0] {get_string('exit')}
""")
          secim = input(f"{clr.am3}[$] {get_string('choice')}: {clr.r}").strip()
          write_log(f"[$] [{secim}] seçeneği seçildi (Ana menu)", level="EXEC")
          if secim == "0":
               hf.cık()
          elif secim == "1":
               pmenu.tarama_menusu()
          elif secim == "2":
               ip_menu.ip_taraması()
          elif secim == "3":
               dm.deauth_menusu()
          elif secim == "4":
               set_opt.ayarlar()
          elif secim == "5":
               help.yardım()
          else:
               print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
               write_log("[!] Geçerli bir değer girin (Ana menu)", level="ERROR")
               hf.cık()

     except KeyboardInterrupt:
          print(f"\n{clr.k}[!] {get_string('process_terminated')}{clr.r}")
          write_log("[!] İşlem sonlandırıldı", level="ERROR")
          hf.cık()
     except Exception as e:
          print(f"{clr.k}[!] {get_string('error')}: {e}{clr.r}")
          write_log(f"[!] Hata: {e} (Ana menu)", level="ERROR")
          hf.cık()

import argparse

def main():
    parser = argparse.ArgumentParser(description="Vscann - Network & Port Scanner")
    # Positional Target
    parser.add_argument("pos_target", nargs="?", help="Target IP, hostname, or network")
    
    # Network Scan Group
    group_net = parser.add_argument_group('Network Scan')
    group_net.add_argument("-n", "--network", help="Network address to scan (e.g., 192.168.1.0/24)")
    
    # Port Scan Group
    group_port = parser.add_argument_group('Port Scan')
    group_port.add_argument("-t", "--target", help="Target IP or hostname")
    group_port.add_argument("-p", "--port", help="Target port or range")
    group_port.add_argument("-r", "--range", help="Port range (e.g., 20-80) [Legacy]")
    group_port.add_argument("--ports", help="Selected ports (e.g., 22,80,443) [Legacy]")
    group_port.add_argument("--standard", action="store_true", help="Scan standard ports (1-1024)")
    group_port.add_argument("--all", action="store_true", help="Scan all ports (0-65535)")
    
    # Advanced Scan Group
    group_adv = parser.add_argument_group('Advanced Scan')
    group_adv.add_argument("-T", "--threads", type=int, help="Number of threads")
    group_adv.add_argument("--timeout", type=float, default=0.5, help="Socket timeout in seconds")
    group_adv.add_argument("--udp", action="store_true", help="Perform UDP scan")
    group_adv.add_argument("--syn", action="store_true", help="Perform TCP SYN scan (Root required)")
    group_adv.add_argument("--stealth", choices=["NULL", "FIN", "XMAS"], help="Perform Stealth scan (Root required)")
    group_adv.add_argument("--os", action="store_true", help="Perform OS discovery (Root required)")

    # Deauth Group
    group_deauth = parser.add_argument_group('Deauth Attack')
    group_deauth.add_argument("--deauth", action="store_true", help="Launch Deauth attack menu (Root required)")

    # Config/Settings Group
    group_cfg = parser.add_argument_group('General Settings & Output')
    group_cfg.add_argument("--lang", choices=["tr", "en"], help="Set application language (tr/en)")
    group_cfg.add_argument("--theme", help="Set application theme (1-20)")
    group_cfg.add_argument("--log", help="Set log levels (e.g., 'all', 'none', 'func,error')")
    group_cfg.add_argument("--json", help="Save output to JSON file")
    group_cfg.add_argument("--verbose", action="store_true", help="Show all port results (open/closed/filtered)")

    args = parser.parse_args()

    # Eğer herhangi bir argüman girilmişse CLI modunda çalış
    if len(sys.argv) > 1:
        system("cls||clear")
        
        # Settings
        setting_used = False
        if args.lang:
            lang.DIL_SEC("1" if args.lang == "tr" else "2")
            setting_used = True
        if args.theme:
            from settings import set_themes
            set_themes.tema_degis(args.theme)
            setting_used = True
        if args.log:
            from settings import set_loging
            if args.log.lower() == "all":
                set_loging.set_log_level("ALL", True)
            elif args.log.lower() == "none":
                set_loging.set_log_level("ALL", False)
            else:
                requested = [l.strip().upper() for l in args.log.split(",")]
                for l in ["FUNC", "EXEC", "ERROR", "RESULT"]:
                    set_loging.set_log_level(l, l in requested)
            setting_used = True

        # Deauth CLI handler
        if args.deauth:
            dm.deauth_menusu()
            sys.exit()

        # Target Resolution
        target = args.pos_target or args.target or args.network
        if target:
            if target.lower() == "localhost":
                target = "127.0.0.1"
            
            # Smart Scan Selection
            is_net_scan = args.network is not None or "/" in target
            
            if is_net_scan:
                agt.ag_taraması(target_ip=target)
                sys.exit()
            
            # Port Resolution
            ports = []
            if args.port:
                if "-" in args.port:
                    try:
                        s, e = map(int, args.port.split("-"))
                        ports = list(range(s, e + 1))
                    except: pass
                elif "," in args.port:
                    try: ports = [int(p.strip()) for p in args.port.split(",")]
                    except: pass
                else:
                    try: ports = [int(args.port)]
                    except: pass
            elif args.range:
                try:
                    s, e = map(int, args.range.split("-"))
                    ports = list(range(s, e + 1))
                except: pass
            elif args.ports:
                try: ports = [int(p.strip()) for p in args.ports.split(",")]
                except: pass
            elif args.standard:
                ports = list(range(1, 1025))
            elif args.all:
                ports = list(range(0, 65536))
            else:
                ports = list(range(1, 1025)) # Default

            # Scanner Function Selection
            from func.port_scan import scapy_scanners as ss
            scanner = p_tsı.port_taraması
            if args.udp: scanner = ss.udp_scan
            elif args.syn: scanner = ss.syn_scan
            elif args.stealth: scanner = lambda ip, p, t: ss.stealth_scan(ip, p, args.stealth, t)

            # OS Discovery
            from settings import set_scan_opt as sopt
            persistent_opts = sopt.get_scan_opts()
            
            do_os = args.os or persistent_opts['os_discovery']
            if do_os:
                from func.port_scan import os_discovery as osd
                osd.print_os_info(target)

            # Perform Port Scan
            from func.port_scan import thread_tarama as tt
            threads = args.threads or persistent_opts['threads']
            results = tt.thread_port_tarama(target, ports, timeout=args.timeout, max_workers=threads, scanner_func=scanner)
            
            # Process Results
            from func import output_handler as oh
            from func.port_scan import servis_tespit as st
            
            open_ports = sorted([r for r in results if r["status"] == "open" or "open" in r["status"]], key=lambda x: x["port"])
            
            is_verbose = args.verbose or persistent_opts['verbose']
            if is_verbose:
                print(f"\n{clr.s}[#] Tüm Port Sonuçları:{clr.r}")
                for r in results:
                    oh.print_verbose_result(r)
            
            print(f"\n\t{clr.y}$$--------------{get_string('scan_completed')}--------------$${clr.r}")
            print(f"{clr.am}{get_string('target_ip')}:{clr.r} {target} | {clr.am}{get_string('total_scanned')}:{clr.r} {len(ports)} | {clr.am}{get_string('open_ports')}:{clr.r} {len(open_ports)}")
            
            if open_ports:
                print(f"\n{clr.s}[~] Servis tespiti yapılıyor...{clr.r}\n")
                for r in open_ports:
                    sonuc = st.servis_tespit(target, r["port"])
                    st.sonuc_yazdir(sonuc, r["time"])
            
            # JSON Output
            if args.json:
                json_data = oh.format_json(results, {"ip": target, "scanned_at": str(datetime.now())})
                if oh.save_json_output(args.json, json_data):
                    print(f"\n{clr.y}[+] Çıktı JSON dosyasına kaydedildi: {args.json}{clr.r}")

            sys.exit()
        
        elif setting_used:
            sys.exit()
        else:
            parser.print_help()
            sys.exit()

    # No arguments provided -> Interactive Mode
    state = "main"
    while state != "exit":
        write_log(f"[~] State değiştirildi: {state}", level="FUNC")
        if state == "main":
            state = main_menu() or "main"
        elif state == "port":
            state = pmenu.tarama_menusu() or "main"
        elif state == "ip":
            state = ip_menu.ip_taraması() or "main"
        elif state == "deauth":
            dm.deauth_menusu()
            state = "main"
        elif state == "settings":
            state = set_opt.ayarlar() or "main"
        elif state == "help":
            state = help.yardım() or "main"
        else:
            break
    hf.cık()

if __name__ == "__main__":
    main()
