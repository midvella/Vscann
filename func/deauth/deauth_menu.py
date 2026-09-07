from settings.set_loging import write_log
write_log("[&] 'deauth_menu.py' dosyası çalıştırıldı", level="EXEC")

import time
import threading
from os import system
from settings import set_themes as clr
from settings.set_lang import get_string
from func.helper_func import Vbanner
from func import helper_func as hf
from func.deauth import deauth_attack as da

def _print_requirements(reqs):
    """Gereksinim durumunu yazdırır"""
    ok = f"{clr.y}✓{clr.r}"
    fail = f"{clr.k}✗{clr.r}"
    
    print(f"\n{clr.am6}{'='*56}")
    print(f"{clr.am6}         ███ {get_string('deauth_requirements')} ███")
    print(f"{clr.am7}{'='*56}{clr.r}\n")
    
    print(f"  {ok if reqs['root'] else fail} Root {get_string('deauth_access')}")
    print(f"  {ok if reqs['scapy'] else fail} Scapy {get_string('deauth_module')}")
    
    if reqs['wifi']:
        print(f"  {ok} WiFi: {', '.join(reqs['wifi'])}")
    else:
        print(f"  {fail} WiFi {get_string('deauth_interface')}")
    
    print()
    return reqs['ready']

def _select_interface(wifi_list):
    """WiFi arayüzü seçimi"""
    if len(wifi_list) == 1:
        return wifi_list[0]
    
    print(f"\n{clr.am6}[*] {get_string('deauth_select_iface')}:{clr.r}\n")
    for i, iface in enumerate(wifi_list, 1):
        mode = da.get_interface_mode(iface)
        print(f"  {clr.am}{i}. {iface} ({mode}){clr.r}")
    
    try:
        choice = int(input(f"\n{clr.am3}[$] {get_string('choice')}: {clr.r}").strip())
        if 1 <= choice <= len(wifi_list):
            return wifi_list[choice - 1]
    except (ValueError, IndexError):
        pass
    
    return wifi_list[0]

def _display_ap_list(ap_list):
    """AP listesini tablo olarak yazdırır"""
    print(f"\n{clr.am6}{'='*70}")
    print(f"  {'No':<4} {'BSSID':<20} {'SSID':<20} {'CH':<5} {'Sinyal':<10}")
    print(f"{clr.am7}{'='*70}{clr.r}")
    
    for i, ap in enumerate(ap_list, 1):
        print(f"  {clr.y}{i:<4}{clr.r} {ap['bssid']:<20} {ap['ssid']:<20} {ap['channel']:<5} {ap['signal']:<10}")
    
    print(f"{clr.am}{'─'*70}{clr.r}")

def _display_client_list(client_list):
    """İstemci listesini yazdırır"""
    print(f"\n{clr.am6}{'='*50}")
    print(f"  {'No':<4} {'MAC Adresi':<25} {'BSSID':<20}")
    print(f"{clr.am7}{'='*50}{clr.r}")
    
    for i, client in enumerate(client_list, 1):
        print(f"  {clr.y}{i:<4}{clr.r} {client['mac']:<25} {client['bssid']:<20}")
    
    print(f"{clr.am}{'─'*50}{clr.r}")

def deauth_menusu():
    """Ana Deauth menüsü"""
    write_log("[~] 'deauth_menusu()' fonksiyonu çalıştırıldı", level="FUNC")
    
    system("cls||clear")
    Vbanner()
    
    print(f"\n{clr.k}[!] {get_string('deauth_warning')}{clr.r}")
    print(f"{clr.k}[!] {get_string('deauth_legal')}{clr.r}\n")
    
    # Gereksinim kontrolü
    reqs = da.check_requirements()
    ready = _print_requirements(reqs)
    
    if not ready:
        if not reqs['root']:
            print(f"{clr.k}[!] {get_string('deauth_need_root')}{clr.r}")
        if not reqs['scapy']:
            print(f"{clr.k}[!] {get_string('scapy_missing')}{clr.r}")
        if not reqs['wifi']:
            print(f"{clr.k}[!] {get_string('deauth_no_wifi')}{clr.r}")
        
        input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
        return
    
    # Arayüz seçimi
    iface = _select_interface(reqs['wifi'])
    monitor_iface = iface
    
    while True:
        system("cls||clear")
        Vbanner()
        
        mode = da.get_interface_mode(monitor_iface)
        
        print(f"""
{clr.am6}======================================================
{clr.am6}          ███ {get_string('deauth_menu_title')} ███
{clr.am7}======================================================

{clr.am6}[*] {get_string('deauth_interface')}: {clr.s}{monitor_iface} ({mode}){clr.r}

{clr.am6}[1] {get_string('deauth_toggle_monitor')}
{clr.am5}[2] {get_string('deauth_scan_ap')}
{clr.am4}[3] {get_string('deauth_scan_clients')}
{clr.am3}[4] {get_string('deauth_targeted')}
{clr.am2}[5] {get_string('deauth_broadcast')}
{clr.am}------------------------------------------------------
{clr.am2}[0] {get_string('back')}
""")
        secim = input(f"{clr.am3}[$] {get_string('choice')}: {clr.r}").strip()
        write_log(f"[$] [{secim}] seçeneği seçildi (Deauth menüsü)", level="EXEC")
        
        if secim == "0":
            # Monitor modu kapat (açıksa)
            if mode == "monitor":
                print(f"\n{clr.s}[~] {get_string('deauth_disabling_monitor')}..{clr.r}")
                success, managed = da.disable_monitor_mode(monitor_iface)
                if success:
                    print(f"{clr.y}[+] {get_string('deauth_monitor_disabled')}: {managed}{clr.r}")
                    monitor_iface = managed
            return
        
        elif secim == "1":
            # Monitor mod toggle
            if mode == "monitor":
                print(f"\n{clr.s}[~] {get_string('deauth_disabling_monitor')}..{clr.r}")
                success, managed = da.disable_monitor_mode(monitor_iface)
                if success:
                    print(f"{clr.y}[+] {get_string('deauth_monitor_disabled')}: {managed}{clr.r}")
                    monitor_iface = managed
                else:
                    print(f"{clr.k}[!] {get_string('deauth_monitor_fail')}{clr.r}")
            else:
                print(f"\n{clr.s}[~] {get_string('deauth_enabling_monitor')}..{clr.r}")
                success, mon = da.enable_monitor_mode(monitor_iface)
                if success:
                    print(f"{clr.y}[+] {get_string('deauth_monitor_enabled')}: {mon}{clr.r}")
                    monitor_iface = mon
                else:
                    print(f"{clr.k}[!] {get_string('deauth_monitor_fail')}{clr.r}")
            
            input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
        
        elif secim == "2":
            # AP Taraması
            if mode != "monitor":
                print(f"\n{clr.k}[!] {get_string('deauth_need_monitor')}{clr.r}")
                input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
                continue
            
            try:
                sure = input(f"{clr.am3}[$] {get_string('deauth_scan_duration')} (10): {clr.r}").strip()
                sure = int(sure) if sure else 10
            except ValueError:
                sure = 10
            
            print(f"\n{clr.s}[~] {get_string('deauth_scanning_ap')} ({sure}s)..{clr.r}\n")
            ap_list = da.scan_access_points(monitor_iface, duration=sure)
            
            if ap_list:
                _display_ap_list(ap_list)
                print(f"\n{clr.y}[+] {len(ap_list)} AP {get_string('deauth_found')}{clr.r}")
            else:
                print(f"{clr.k}[!] {get_string('deauth_no_ap')}{clr.r}")
            
            input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
        
        elif secim == "3":
            # İstemci Taraması
            if mode != "monitor":
                print(f"\n{clr.k}[!] {get_string('deauth_need_monitor')}{clr.r}")
                input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
                continue
            
            bssid = input(f"{clr.am3}[$] {get_string('deauth_target_bssid')}: {clr.r}").strip()
            if not bssid:
                print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
                input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
                continue
            
            # Kanal ayarla
            kanal = input(f"{clr.am3}[$] {get_string('deauth_channel')} (auto): {clr.r}").strip()
            if kanal:
                try:
                    da.set_channel(monitor_iface, int(kanal))
                except ValueError:
                    pass
            
            try:
                sure = input(f"{clr.am3}[$] {get_string('deauth_scan_duration')} (15): {clr.r}").strip()
                sure = int(sure) if sure else 15
            except ValueError:
                sure = 15
            
            print(f"\n{clr.s}[~] {get_string('deauth_scanning_clients')} ({sure}s)..{clr.r}\n")
            clients = da.scan_clients(monitor_iface, bssid, duration=sure)
            
            if clients:
                _display_client_list(clients)
                print(f"\n{clr.y}[+] {len(clients)} {get_string('deauth_clients_found')}{clr.r}")
            else:
                print(f"{clr.k}[!] {get_string('deauth_no_clients')}{clr.r}")
            
            input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
        
        elif secim == "4":
            # Hedefli Deauth
            if mode != "monitor":
                print(f"\n{clr.k}[!] {get_string('deauth_need_monitor')}{clr.r}")
                input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
                continue
            
            gateway = input(f"{clr.am3}[$] {get_string('deauth_gateway_mac')}: {clr.r}").strip()
            target = input(f"{clr.am3}[$] {get_string('deauth_target_mac')}: {clr.r}").strip()
            
            if not gateway or not target:
                print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
                input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
                continue
            
            # Kanal ayarla
            kanal = input(f"{clr.am3}[$] {get_string('deauth_channel')} (auto): {clr.r}").strip()
            if kanal:
                try:
                    da.set_channel(monitor_iface, int(kanal))
                except ValueError:
                    pass
            
            try:
                paket = input(f"{clr.am3}[$] {get_string('deauth_packet_count')} (0=∞): {clr.r}").strip()
                paket = int(paket) if paket else 0
            except ValueError:
                paket = 0
            
            try:
                aralik = input(f"{clr.am3}[$] {get_string('deauth_interval')} (0.1): {clr.r}").strip()
                aralik = float(aralik) if aralik else 0.1
            except ValueError:
                aralik = 0.1
            
            print(f"\n{clr.k}[!] {get_string('deauth_starting')}..{clr.r}")
            print(f"{clr.am}[*] {get_string('deauth_target_mac')}: {target}{clr.r}")
            print(f"{clr.am}[*] {get_string('deauth_gateway_mac')}: {gateway}{clr.r}")
            print(f"{clr.am}[*] {get_string('deauth_packet_count')}: {'∞' if paket == 0 else paket}{clr.r}")
            print(f"\n{clr.s}[~] {get_string('deauth_stop_info')}{clr.r}\n")
            
            def progress(count):
                print(f"\r{clr.y}[+] {get_string('deauth_packets_sent')}: {count}{clr.r}", end="", flush=True)
            
            try:
                if paket == 0:
                    # Sonsuz mod — thread ile çalıştır
                    t = da.start_attack_thread(
                        da.deauth_attack,
                        iface=monitor_iface,
                        target_mac=target,
                        gateway_mac=gateway,
                        count=0,
                        interval=aralik,
                        callback=progress
                    )
                    input()  # Enter'a basana kadar devam
                    da.stop_attack()
                    t.join(timeout=3)
                else:
                    sent = da.deauth_attack(
                        iface=monitor_iface,
                        target_mac=target,
                        gateway_mac=gateway,
                        count=paket,
                        interval=aralik,
                        callback=progress
                    )
            except KeyboardInterrupt:
                da.stop_attack()
            
            print(f"\n\n{clr.y}[+] {get_string('deauth_completed')}{clr.r}")
            input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
        
        elif secim == "5":
            # Broadcast Deauth
            if mode != "monitor":
                print(f"\n{clr.k}[!] {get_string('deauth_need_monitor')}{clr.r}")
                input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
                continue
            
            gateway = input(f"{clr.am3}[$] {get_string('deauth_gateway_mac')}: {clr.r}").strip()
            
            if not gateway:
                print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
                input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
                continue
            
            # Kanal ayarla
            kanal = input(f"{clr.am3}[$] {get_string('deauth_channel')} (auto): {clr.r}").strip()
            if kanal:
                try:
                    da.set_channel(monitor_iface, int(kanal))
                except ValueError:
                    pass
            
            try:
                paket = input(f"{clr.am3}[$] {get_string('deauth_packet_count')} (0=∞): {clr.r}").strip()
                paket = int(paket) if paket else 0
            except ValueError:
                paket = 0
            
            try:
                aralik = input(f"{clr.am3}[$] {get_string('deauth_interval')} (0.1): {clr.r}").strip()
                aralik = float(aralik) if aralik else 0.1
            except ValueError:
                aralik = 0.1
            
            print(f"\n{clr.k}[!] {get_string('deauth_broadcast_warning')}{clr.r}")
            print(f"{clr.am}[*] {get_string('deauth_gateway_mac')}: {gateway}{clr.r}")
            print(f"{clr.am}[*] {get_string('deauth_packet_count')}: {'∞' if paket == 0 else paket}{clr.r}")
            print(f"\n{clr.s}[~] {get_string('deauth_stop_info')}{clr.r}\n")
            
            def progress_bc(count):
                print(f"\r{clr.y}[+] {get_string('deauth_packets_sent')}: {count}{clr.r}", end="", flush=True)
            
            try:
                if paket == 0:
                    t = da.start_attack_thread(
                        da.broadcast_deauth,
                        iface=monitor_iface,
                        gateway_mac=gateway,
                        count=0,
                        interval=aralik,
                        callback=progress_bc
                    )
                    input()
                    da.stop_attack()
                    t.join(timeout=3)
                else:
                    sent = da.broadcast_deauth(
                        iface=monitor_iface,
                        gateway_mac=gateway,
                        count=paket,
                        interval=aralik,
                        callback=progress_bc
                    )
            except KeyboardInterrupt:
                da.stop_attack()
            
            print(f"\n\n{clr.y}[+] {get_string('deauth_completed')}{clr.r}")
            input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
        
        else:
            print(f"{clr.k}[!] {get_string('invalid_choice')}{clr.r}")
            time.sleep(1)
