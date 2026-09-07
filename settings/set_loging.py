import json,os,sys
from datetime import datetime
from os import system

CONFIG_PATH = "config.json"
DEFAULT_LOG_LEVELS = {
    "FUNC": False,
    "EXEC": False,
    "ERROR": False,
    "RESULT": False
}
LOG_FILE = "scann_log.txt"

def load_config():
    """Config dosyasını yükle, yoksa varsayılanla oluştur."""
    from settings import config_manager as cm
    data = cm.load()
    if "log_levels" not in data:
        data["log_levels"] = DEFAULT_LOG_LEVELS
        cm.save(data)
    return data
    
def save_config(new_data: dict):
    """Config içeriğini koruyarak sadece verilen verileri günceller."""
    from settings import config_manager as cm
    cm.save(new_data)
def get_log_levels():
    """Log seviyelerinin mevcut durumunu döndürür."""
    config = load_config()
    return config.get("log_levels", DEFAULT_LOG_LEVELS)

def set_log_level(level: str, value: bool):
    """Belirli bir log seviyesini True/False olarak kaydeder."""
    levels = get_log_levels()
    if level == "ALL":
        for l in levels:
            levels[l] = value
    elif level in levels:
        levels[level] = value
    save_config({"log_levels": levels})

def loginfo_menu():
    from settings.set_lang import get_string
    from settings import set_themes as clr
    while True:
        system("cls||clear")
        levels = get_log_levels()
        
        def get_status_text(val):
            return f"{clr.y}{get_string('on')}{clr.r}" if val else f"{clr.k}{get_string('off')}{clr.r}"

        print(f"""
{clr.am6}======================================================
{clr.am6}               ███ {get_string('log_settings')} ███
{clr.am7}======================================================

{clr.am6}[1] {get_string('log_level_func')}: {get_status_text(levels['FUNC'])}
{clr.am5}[2] {get_string('log_level_exec')}: {get_status_text(levels['EXEC'])}
{clr.am4}[3] {get_string('log_level_error')}: {get_status_text(levels['ERROR'])}
{clr.am3}[4] {get_string('log_level_result')}: {get_status_text(levels['RESULT'])}
{clr.am2}[5] {get_string('log_level_all')} ({get_string('open')})
{clr.am1}[6] {get_string('log_level_all')} ({get_string('close')})
{clr.am}------------------------------------------------------
{clr.am2}[0] {get_string('back')}

{clr.am3}[$] {get_string('choice')}: {clr.r}""", end="")
        
        secim = input().strip()
        
        if secim == "0":
            break
        elif secim == "1":
            set_log_level("FUNC", not levels["FUNC"])
        elif secim == "2":
            set_log_level("EXEC", not levels["EXEC"])
        elif secim == "3":
            set_log_level("ERROR", not levels["ERROR"])
        elif secim == "4":
            set_log_level("RESULT", not levels["RESULT"])
        elif secim == "5":
            set_log_level("ALL", True)
        elif secim == "6":
            set_log_level("ALL", False)
        else:
            print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
            input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")

def write_log(message: str, level: str = "EXEC"):
    level = level.upper()
    try:
        levels = get_log_levels()
        if not levels.get(level, False):
            return
    except Exception:
        pass
    
    from datetime import datetime
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{time_now}] [{level}] - {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
