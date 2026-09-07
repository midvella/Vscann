from settings.set_loging import write_log
from settings import set_loging as log_f
from settings import set_themes as clr
from settings import set_lang as lang
from settings import set_scan_opt as scan_opt
from settings.set_lang import get_string
from func import helper_func as hf
from os import system
from func.helper_func import Vbanner

def AYAR_SECİM(secim):
      write_log("[~] 'AYAR_SECİM()' fonksiyonu çalıştırıldı", level="FUNC")
      ayarlarss = {
      "1":lang.dil_control,
      "2":clr.tema_control,
      "3":log_f.loginfo_menu,
      "4":scan_opt.scan_settings_menu
      }

      if secim == "0":
          return "main"
      func = ayarlarss.get(secim)
      if func:
          func()
          return "main"
      else:
          print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
          write_log("[!] Geçerli bir değer girin (Ayar menu)\n", level="ERROR")
          hf.cık()

def ayarlar():
    write_log("[~] 'ayarlar()' fonksiyonu çalıştırıldı", level="FUNC")
    while True:
        system("cls||clear")
        Vbanner()
        
        set_secim = input(f"""
{clr.am6}======================================================
{clr.am6}                  ███ {get_string('settings_title')} ███
{clr.am7}======================================================

{clr.am6}[1] {get_string('lang_settings')} [{clr.s}{lang.get_lang().upper()}{clr.r}]
{clr.am5}[2] {get_string('theme')} [{clr.s}{clr.config["theme"]}{clr.r}]
{clr.am4}[3] {get_string('log_settings')}
{clr.am3}[4] {get_string('scan_settings')} [{clr.s}{scan_opt.get_scan_opts()['threads']}{clr.r}]
{clr.am2}------------------------------------------------------{clr.r}
{clr.am2}[0] {get_string('back')}{clr.r}

{clr.am3}[$] {get_string('choice')}: {clr.r}""")
        write_log(f"[$] [{set_secim}] seçeneği seçildi (Ayarlar)", level="EXEC")
        if set_secim == "0":
            break
        AYAR_SECİM(set_secim)
