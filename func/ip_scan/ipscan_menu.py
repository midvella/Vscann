from settings.set_loging import write_log
write_log("[&] 'ipscan_menu.py' dosyası çalıştırıldı", level="EXEC")

from settings import set_themes as clr
from os import system
from func.helper_func import Vbanner
from func import helper_func as hf
from func.ip_scan import ag_taraması as ag_tara
from settings.set_lang import get_string

def ipscan_menu(secilmis):
    write_log("[~] 'ipscan_menu()' fonksiyonu çalıştırıldı", level="FUNC")
    secim_menusu = {
        "1":ag_tara.ag_taraması
    }
    if secilmis == "0":
        return "main"
    func = secim_menusu.get(secilmis)
    if func:
        func()
        input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
        hf.cık()
    else:
        print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
        write_log(f"[!] {get_string('invalid_choice')} (Ağ tarama menusu)", level="ERROR")
        hf.cık()

def ip_taraması():
    write_log("[~] 'ip_taraması()' fonksiyonu çalıştırıldı", level="FUNC")
    system("cls||clear")
    Vbanner()
    print(f"{clr.s}[#] {get_string('network_scan_title')} {clr.r}\n")
    secim = input(f"""
{clr.am6}======================================================
{clr.am6}             ███ {get_string('network_scan_title')} ███       
{clr.am7}======================================================

{clr.am6}[1] {get_string('start')}
{clr.am5}------------------------------------------------------
{clr.am4}[0] {get_string('back')}

{clr.am3}[$] {get_string('choice')}: {clr.r}""")
    write_log(f"[$] [{secim}] {get_string('choice_selected')} (Ağ tarama menusu)", level="EXEC")
    ipscan_menu(secim)
