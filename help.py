from settings import set_themes as clr
from settings.set_loging import write_log
from settings.set_lang import get_string
write_log("[&] 'help.py' dosyası çalıştırıldı", level="EXEC")

def yardım():
     write_log("[~] 'yardım()' fonksiyonu çalıştırıldı", level="FUNC")
     print(f"""
{clr.k}[!] {get_string('help_warning')}
[!] {get_string('help_disclaimer')}{clr.r}

{clr.am3}[*] {get_string('cli_usage')}: python3 Vscann.py --help{clr.r}

{clr.am2}[1] {get_string('help_port_desc')} 
     {clr.am3}[-] 0- {get_string('back')}
     {clr.am4}[-] 1- {get_string('port_range_label')}
     {clr.am5}[-] 2- {get_string('selected_ports')}
     {clr.am6}[-] 3- {get_string('standard_scan')} 
     {clr.am7}[-] 4- {get_string('all_ports_scan')}
     {clr.am2}[-] 5- {get_string('adv_scan_settings')}

{clr.am6}[2] {get_string('help_net_desc')}
     {clr.am5}[-] 0- {get_string('back')}
     {clr.am4}[-] 1- {get_string('start')}

{clr.am4}[3] {get_string('deauth_attack')}
     {clr.am3}[-] 1- {get_string('deauth_toggle_monitor')}
     {clr.am4}[-] 2- {get_string('deauth_scan_ap')}
     {clr.am5}[-] 3- {get_string('deauth_scan_clients')}
     {clr.am6}[-] 4- {get_string('deauth_targeted')}
     {clr.am7}[-] 5- {get_string('deauth_broadcast')}

{clr.am5}[4] {get_string('help_set_desc')}
     {clr.am3}[-] 0- {get_string('back')}
     {clr.am2}[-] 1- {get_string('lang_settings')}
     {clr.am}[-] 2- {get_string('theme')}
     {clr.am2}[-] 3- {get_string('log_settings')}
     {clr.am3}[-] 4- {get_string('ram_info')}

{clr.am4}[-] {get_string('help_log_analyze')}
     {clr.am4}[-] {get_string('log_level_error')} = [!]
     {clr.am5}[-] {get_string('log_level_func')} = [~]
     {clr.am6}[-] {get_string('log_level_exec')} = [&]
     {clr.am7}[-] {get_string('log_level_result')} = [#]
     {clr.am6}[-] {get_string('choice')} log = [$]

{clr.am3}[*] {get_string('help_progress_info')}
""")
     input(f"\n{clr.s}{get_string('press_any_key')}{clr.r}")
     return "main"
