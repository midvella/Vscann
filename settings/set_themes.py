import json
from os import system
import os

CONFIG_PATH = "config.json"
DEFAULT_THEME = "mavi"

temalar = {
    "mavi": {
        "am1": "\033[38;5;87m", "am2": "\033[38;5;81m", "am3": "\033[38;5;75m",
        "am4": "\033[38;5;69m", "am5": "\033[38;5;63m", "am6": "\033[38;5;27m", "am7": "\033[38;5;21m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "yesil": {
        "am1": "\033[38;5;46m", "am2": "\033[38;5;40m", "am3": "\033[38;5;34m",
        "am4": "\033[38;5;28m", "am5": "\033[38;5;70m", "am6": "\033[38;5;76m", "am7": "\033[38;5;82m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "mor": {
        "am1": "\033[38;5;141m", "am2": "\033[38;5;135m", "am3": "\033[38;5;129m",
        "am4": "\033[38;5;93m", "am5": "\033[38;5;99m", "am6": "\033[38;5;105m", "am7": "\033[38;5;111m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "beyaz": {
        "am1": "\033[38;5;255m", "am2": "\033[38;5;252m", "am3": "\033[38;5;250m",
        "am4": "\033[38;5;247m", "am5": "\033[38;5;244m", "am6": "\033[38;5;240m", "am7": "\033[38;5;237m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "kırmızı": {
        "am1": "\033[38;5;196m", "am2": "\033[38;5;160m", "am3": "\033[38;5;124m",
        "am4": "\033[38;5;88m", "am5": "\033[38;5;203m", "am6": "\033[38;5;210m", "am7": "\033[38;5;9m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "sarı": {
        "am1": "\033[38;5;226m", "am2": "\033[38;5;220m", "am3": "\033[38;5;214m",
        "am4": "\033[38;5;178m", "am5": "\033[38;5;229m", "am6": "\033[38;5;230m", "am7": "\033[38;5;185m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "turuncu": {
        "am1": "\033[38;5;208m", "am2": "\033[38;5;202m", "am3": "\033[38;5;166m",
        "am4": "\033[38;5;130m", "am5": "\033[38;5;215m", "am6": "\033[38;5;223m", "am7": "\033[38;5;172m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "pembe": {
        "am1": "\033[38;5;213m", "am2": "\033[38;5;207m", "am3": "\033[38;5;201m",
        "am4": "\033[38;5;199m", "am5": "\033[38;5;205m", "am6": "\033[38;5;211m", "am7": "\033[38;5;218m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "camgobegi": {
        "am1": "\033[38;5;51m", "am2": "\033[38;5;50m", "am3": "\033[38;5;49m",
        "am4": "\033[38;5;43m", "am5": "\033[38;5;44m", "am6": "\033[38;5;45m", "am7": "\033[38;5;80m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "lacivert": {
        "am1": "\033[38;5;19m", "am2": "\033[38;5;18m", "am3": "\033[38;5;17m",
        "am4": "\033[38;5;20m", "am5": "\033[38;5;25m", "am6": "\033[38;5;26m", "am7": "\033[38;5;61m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "neon_yesil": {
        "am1": "\033[38;5;118m", "am2": "\033[38;5;119m", "am3": "\033[38;5;120m",
        "am4": "\033[38;5;156m", "am5": "\033[38;5;155m", "am6": "\033[38;5;154m", "am7": "\033[38;5;82m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "altin": {
        "am1": "\033[38;5;220m", "am2": "\033[38;5;178m", "am3": "\033[38;5;136m",
        "am4": "\033[38;5;172m", "am5": "\033[38;5;214m", "am6": "\033[38;5;221m", "am7": "\033[38;5;179m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "gumus": {
        "am1": "\033[38;5;188m", "am2": "\033[38;5;187m", "am3": "\033[38;5;145m",
        "am4": "\033[38;5;144m", "am5": "\033[38;5;249m", "am6": "\033[38;5;250m", "am7": "\033[38;5;251m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "buz_mavisi": {
        "am1": "\033[38;5;159m", "am2": "\033[38;5;153m", "am3": "\033[38;5;117m",
        "am4": "\033[38;5;111m", "am5": "\033[38;5;152m", "am6": "\033[38;5;146m", "am7": "\033[38;5;189m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "lavanta": {
        "am1": "\033[38;5;183m", "am2": "\033[38;5;177m", "am3": "\033[38;5;171m",
        "am4": "\033[38;5;134m", "am5": "\033[38;5;140m", "am6": "\033[38;5;146m", "am7": "\033[38;5;189m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "mercan": {
        "am1": "\033[38;5;209m", "am2": "\033[38;5;203m", "am3": "\033[38;5;197m",
        "am4": "\033[38;5;174m", "am5": "\033[38;5;210m", "am6": "\033[38;5;216m", "am7": "\033[38;5;217m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "zumrut": {
        "am1": "\033[38;5;48m", "am2": "\033[38;5;42m", "am3": "\033[38;5;36m",
        "am4": "\033[38;5;30m", "am5": "\033[38;5;35m", "am6": "\033[38;5;41m", "am7": "\033[38;5;47m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "gece": {
        "am1": "\033[38;5;60m", "am2": "\033[38;5;61m", "am3": "\033[38;5;62m",
        "am4": "\033[38;5;56m", "am5": "\033[38;5;57m", "am6": "\033[38;5;93m", "am7": "\033[38;5;54m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "gokkusagi": {
        "am1": "\033[38;5;196m", "am2": "\033[38;5;208m", "am3": "\033[38;5;226m",
        "am4": "\033[38;5;46m", "am5": "\033[38;5;21m", "am6": "\033[38;5;93m", "am7": "\033[38;5;201m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    },
    "retro": {
        "am1": "\033[38;5;179m", "am2": "\033[38;5;173m", "am3": "\033[38;5;137m",
        "am4": "\033[38;5;101m", "am5": "\033[38;5;143m", "am6": "\033[38;5;180m", "am7": "\033[38;5;216m",
        "k": "\033[31m", "s": "\033[93m", "y": "\033[1;32m", "r": "\033[0m"
    }
}

def load_config():
    from settings import config_manager as cm
    from settings.set_loging import write_log
    write_log("[~] 'load_config()' fonksiyonu çalıştırıldı [set_themes.py]", level="FUNC")
    """Config dosyasını oku, yoksa oluştur"""
    data = cm.load()
    if "theme" not in data:
        data["theme"] = DEFAULT_THEME
        cm.save({"theme": DEFAULT_THEME})
        write_log("[#] 'config.json' dosyası oluşturuldu", level="EXEC")
        write_log("[#] 'theme': 'DEFAULT_THEME' olarak atandı", level="EXEC")
    return data


def save_config(new_data: dict):
    from settings import config_manager as cm
    from settings.set_loging import write_log
    write_log("[~] 'save_config()' fonksiyonu çalıştırıldı [set_themes.py]", level="FUNC")
    """Config'teki mevcut veriyi koruyarak güncelle"""
    cm.save(new_data)

def tema_degis(secim):
    from settings.set_loging import write_log
    from settings.set_lang import get_string
    write_log("[~] 'tema_degis()' fonksiyonu çalıştırıldı", level="FUNC")
    secilen_numaralar = {
        "1": "mavi", "2": "turuncu", "3": "sarı",
        "4": "yesil", "5": "mor", "6": "kırmızı", "7": "beyaz",
        "8": "pembe", "9": "camgobegi", "10": "lacivert",
        "11": "neon_yesil", "12": "altin", "13": "gumus",
        "14": "buz_mavisi", "15": "lavanta", "16": "mercan",
        "17": "zumrut", "18": "gece", "19": "gokkusagi", "20": "retro"
    }
    secilen = secilen_numaralar.get(secim, DEFAULT_THEME)
    save_config({"theme": secilen})
    apply_theme(secilen) 
    print(f"{s}[~] {secilen.upper()} {get_string('theme_selected')}{r}")
    write_log(f"[~] {secilen.upper()} {get_string('theme_selected')}\n", level="EXEC")
    return temalar[secilen]

def apply_theme(tema_name):
    """Global tema değişkenlerini günceller."""
    global am1, am, am2, am3, am4, am5, am6, am7, k, s, y, r
    tema = temalar.get(tema_name, temalar[DEFAULT_THEME])
    am1 = tema["am1"]
    am  = am1
    am2 = tema["am2"]
    am3 = tema["am3"]
    am4 = tema["am4"]
    am5 = tema["am5"]
    am6 = tema["am6"]
    am7 = tema["am7"]
    k = tema["k"]
    s = tema["s"]
    y = tema["y"]
    r = tema["r"]
    config["theme"] = tema_name

config = load_config()
# İlk başta global değişkenleri tanımla
am1 = am = am2 = am3 = am4 = am5 = am6 = am7 = k = s = y = r = ""
apply_theme(config["theme"])

def tema_control():
    from settings.set_loging import write_log
    from settings.set_lang import get_string
    write_log("[~] 'tema_control()' fonksiyonu çalıştırıldı", level="FUNC")
    tema_secimi = input(f"""
{am6}═══════════════════ {get_string('themes_title')} ═══════════════════

{am5}  ┌─ {get_string('classic')} ──────────────────────────────────┐
{am4}  │ [1]  Mavi ({get_string('off')})    [2]  Turuncu     │
{am3}  │ [3]  Sarı                [4]  Yeşil        │
{am2}  │ [5]  Mor                 [6]  Kırmızı      │
{am}  │ [7]  Beyaz               [8]  Pembe        │
{am5}  └────────────────────────────────────────────┘

{am5}  ┌─ {get_string('cool_tones')} ─────────────────────────────┐
{am4}  │ [9]  Cam Göbeği          [10] Lacivert      │
{am3}  │ [14] Buz Mavisi          [15] Lavanta       │
{am5}  └─────────────────────────────────────────────┘

{am5}  ┌─ {get_string('warm_tones')} ─────────────────────────────┐
{am4}  │ [11] Neon Yeşil           [12] Altın        │
{am3}  │ [16] Mercan               [17] Zümrüt       │
{am5}  └─────────────────────────────────────────────┘

{am5}  ┌─ {get_string('special')} ──────────────────────────────────────┐
{am4}  │ [13] Gümüş               [18] Gece          │
{am3}  │ [19] Gökkuşağı           [20] Retro         │
{am5}  └─────────────────────────────────────────────┘

{am6}═══════════════════════════════════════════════

{am5}[$] {get_string('choice')}: {r}""")
    tema_degis(tema_secimi)
    input(f"\n{s}{get_string('press_any_key')}{r}")
