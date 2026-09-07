import json, os
from settings.set_loging import write_log
from os import system

CONFIG_PATH = "config.json"
DEFAULT_SCAN_OPTS = {
    "threads": 300,
    "verbose": False,
    "os_discovery": False
}

def load_config():
    from settings import config_manager as cm
    data = cm.load()
    
    # Check if scan_opts exists, if not, add defaults
    updated = False
    for key, value in DEFAULT_SCAN_OPTS.items():
        if key not in data:
            data[key] = value
            updated = True
    
    if updated:
        cm.save(data)
    return data

def save_config(new_data: dict):
    from settings import config_manager as cm
    cm.save(new_data)

def get_scan_opts():
    config = load_config()
    return {k: config.get(k, DEFAULT_SCAN_OPTS[k]) for k in DEFAULT_SCAN_OPTS}

def set_scan_opt(key, value):
    save_config({key: value})

def scan_settings_menu():
    from settings.set_lang import get_string
    from settings import set_themes as clr
    while True:
        system("cls||clear")
        opts = get_scan_opts()
        
        def get_bool_text(val):
            return f"{clr.y}{get_string('on')}{clr.r}" if val else f"{clr.k}{get_string('off')}{clr.r}"

        print(f"""
{clr.am6}======================================================
{clr.am6}               ███ {get_string('scan_settings')} ███
{clr.am7}======================================================

{clr.am6}[1] {get_string('threads')}: {clr.s}{opts['threads']}{clr.r}
{clr.am5}[2] {get_string('verbose_output')}: {get_bool_text(opts['verbose'])}
{clr.am4}[3] {get_string('os_discovery_label')}: {get_bool_text(opts['os_discovery'])}
{clr.am}------------------------------------------------------
{clr.am2}[0] {get_string('back')}

{clr.am3}[$] {get_string('choice')}: {clr.r}""", end="")
        
        secim = input().strip()
        
        if secim == "0":
            break
        elif secim == "1":
            try:
                new_threads = int(input(f"{get_string('threads')} [1-1000]: "))
                if 1 <= new_threads <= 1000:
                    set_scan_opt("threads", new_threads)
                else:
                    print(f"{clr.k}[!] {get_string('invalid_number')}{clr.r}")
                    input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
            except:
                print(f"{clr.k}[!] {get_string('invalid_number')}{clr.r}")
                input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
        elif secim == "2":
            set_scan_opt("verbose", not opts["verbose"])
        elif secim == "3":
            set_scan_opt("os_discovery", not opts["os_discovery"])
        else:
            print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
            input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
