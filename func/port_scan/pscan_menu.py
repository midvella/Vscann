from settings.set_loging import write_log
write_log("[&] 'pscan_menu.py' dosyası çalıştırıldı", level="EXEC")

from func.helper_func import Vbanner
from os import system
from func.port_scan import port_range as p_r
from func.port_scan import ping_control as ping
from func.port_scan import secili_port as secp
from func.port_scan import standart,all_ports
from settings import set_themes as clr
from settings.set_lang import get_string
from func import helper_func as hf

from settings import set_scan_opt as scan_opt
# Load persistent defaults
_persistent_opts = scan_opt.get_scan_opts()

# Global state for interactive advanced settings
GLOBAL_SCAN_CONFIG = {
    "technique": "TCP Connect",
    "threads": _persistent_opts['threads'],
    "timeout": 0.5,
    "scanner": None,
    "os_discovery": _persistent_opts['os_discovery'],
    "verbose": _persistent_opts['verbose']
}

def scan_ayarlari():
    write_log("[~] 'scan_ayarlari()' fonksiyonu çalıştırıldı", level="FUNC")
    from func.port_scan import scapy_scanners as ss
    while True:
        system("cls||clear")
        Vbanner()
        # Refresh from persistent config
        opts = scan_opt.get_scan_opts()
        GLOBAL_SCAN_CONFIG["threads"] = opts["threads"]
        GLOBAL_SCAN_CONFIG["os_discovery"] = opts["os_discovery"]
        GLOBAL_SCAN_CONFIG["verbose"] = opts["verbose"]

        print(f"""
{clr.am6}======================================================
{clr.am6}            ███ {get_string('adv_scan_settings')} ███       
{clr.am7}======================================================

{clr.am6}[1] {get_string('method')}: {clr.s}{GLOBAL_SCAN_CONFIG['technique']}{clr.r}
{clr.am5}[2] {get_string('threads')}: {clr.s}{GLOBAL_SCAN_CONFIG['threads']}{clr.r}
{clr.am4}[3] {get_string('timeout_label')}: {clr.s}{GLOBAL_SCAN_CONFIG['timeout']}{clr.r}
{clr.am3}[4] {get_string('os_discovery_label')}: {clr.s}{get_string('on') if GLOBAL_SCAN_CONFIG['os_discovery'] else get_string('off')}{clr.r}
{clr.am2}[5] {get_string('verbose_output')}: {clr.s}{get_string('on') if GLOBAL_SCAN_CONFIG['verbose'] else get_string('off')}{clr.r}
{clr.am}------------------------------------------------------
{clr.am2}[0] {get_string('back')}
""")
        secim = input(f"{clr.am3}[$] {get_string('choice')}: {clr.r}").strip()
        
        if secim == "0":
            break
        elif secim == "1":
            print(f"\n{clr.am6}[1] TCP Connect ({get_string('off')})\n[2] TCP SYN Scan (Root)\n[3] UDP Scan (Root)\n[4] NULL Scan (Root)\n[5] FIN Scan (Root)\n[6] XMAS Scan (Root){clr.r}")
            y_secim = input(f"\n{clr.am3}[$] {get_string('select_method')}: {clr.r}").strip()
            if y_secim == "1":
                GLOBAL_SCAN_CONFIG["technique"] = "TCP Connect"
                GLOBAL_SCAN_CONFIG["scanner"] = None
            elif y_secim == "2":
                GLOBAL_SCAN_CONFIG["technique"] = "TCP SYN"
                GLOBAL_SCAN_CONFIG["scanner"] = ss.syn_scan
            elif y_secim == "3":
                GLOBAL_SCAN_CONFIG["technique"] = "UDP"
                GLOBAL_SCAN_CONFIG["scanner"] = ss.udp_scan
            elif y_secim == "4":
                GLOBAL_SCAN_CONFIG["technique"] = "NULL"
                GLOBAL_SCAN_CONFIG["scanner"] = lambda i, p, t: ss.stealth_scan(i, p, "NULL", t)
            elif y_secim == "5":
                GLOBAL_SCAN_CONFIG["technique"] = "FIN"
                GLOBAL_SCAN_CONFIG["scanner"] = lambda i, p, t: ss.stealth_scan(i, p, "FIN", t)
            elif y_secim == "6":
                GLOBAL_SCAN_CONFIG["technique"] = "XMAS"
                GLOBAL_SCAN_CONFIG["scanner"] = lambda i, p, t: ss.stealth_scan(i, p, "XMAS", t)
        elif secim == "2":
            try:
                val = input(f"{clr.am3}[$] {get_string('threads')} ({get_string('back')}): {clr.r}").strip()
                if val:
                    new_val = int(val)
                    scan_opt.set_scan_opt("threads", new_val)
                    GLOBAL_SCAN_CONFIG["threads"] = new_val
            except: print(f"{clr.k}[!] {get_string('invalid_number')}{clr.r}"); time.sleep(1)
        elif secim == "3":
            try:
                val = input(f"{clr.am3}[$] Timeout (ms): {clr.r}").strip()
                GLOBAL_SCAN_CONFIG["timeout"] = float(val) if val else 0.5
            except: print(f"{clr.k}[!] {get_string('invalid_number')}{clr.r}"); time.sleep(1)
        elif secim == "4":
            new_val = not GLOBAL_SCAN_CONFIG["os_discovery"]
            scan_opt.set_scan_opt("os_discovery", new_val)
            GLOBAL_SCAN_CONFIG["os_discovery"] = new_val
        elif secim == "5":
            new_val = not GLOBAL_SCAN_CONFIG["verbose"]
            scan_opt.set_scan_opt("verbose", new_val)
            GLOBAL_SCAN_CONFIG["verbose"] = new_val

import time
from func.port_scan import port_taraması as p_orig

def scan_wrapper(func):
    """Scan fonksiyonlarını yakalayıp global ayarlarla çalıştırır."""
    def wrapper(*args, **kwargs):
        # Eğer parametreler boşsa (interaktif) global ayarları enjekte et
        scanner = GLOBAL_SCAN_CONFIG["scanner"] or p_orig.port_taraması
        kwargs["timeout"] = GLOBAL_SCAN_CONFIG["timeout"]
        kwargs["max_workers"] = GLOBAL_SCAN_CONFIG["threads"]
        kwargs["scanner_func"] = scanner
        kwargs["os_discovery"] = GLOBAL_SCAN_CONFIG["os_discovery"]
        kwargs["verbose"] = GLOBAL_SCAN_CONFIG["verbose"]
        return func(*args, **kwargs)
    return wrapper

def PSCAN_menu(secilmis):
    write_log("[~] 'PSCAN_menu()' fonksiyonu çalıştırıldı", level="FUNC")
    secim_menusu = {
        "1":scan_wrapper(p_r.port_range),
        "2":scan_wrapper(secp.secili_port),
        "3":scan_wrapper(standart.standart),
        "4":scan_wrapper(all_ports.tum_portlar),
        "5":scan_ayarlari
    }
    if secilmis == "0":
        return "main"
    func = secim_menusu.get(secilmis)
    if func:
        func()
        if secilmis != "5":
            input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
            hf.cık()
    else:
        print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
        write_log(f"[!] {get_string('invalid_choice')} (Port tarama menusu)", level="ERROR")

def tarama_menusu():
    write_log("[~] 'tarama_menusu()' fonksiyonu çalıştırıldı", level="FUNC")
    while True:
        system("cls||clear")
        Vbanner()
        secim = input(f"""
{clr.am6}======================================================
{clr.am6}           ███ {get_string('scan_method_title')} ███       
{clr.am7}======================================================

{clr.am6}[1] {get_string('port_range')}
{clr.am5}[2] {get_string('selected_ports')}
{clr.am4}[3] {get_string('standard_scan')}
{clr.am3}[4] {get_string('all_ports_scan')}
{clr.am2}[5] {get_string('adv_scan_settings')} ({clr.s}{GLOBAL_SCAN_CONFIG['technique']}{clr.r})
{clr.am}------------------------------------------------------
{clr.am2}[0] {get_string('back')}

{clr.am3}[$] {get_string('choice')}: {clr.r}""")
        write_log(f"[$] [{secim}] seçeneği seçildi (Tarama yöntemi menusu)", level="EXEC")
        if secim == "0":
            return "main"
        PSCAN_menu(secim)
