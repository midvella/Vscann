import sys, os, select, termios, tty
from settings import set_themes as clr
from settings.set_loging import write_log
from settings.set_lang import get_string
        
def cık():
      print(f"{clr.s}[#] {get_string('exiting')}{clr.r}")
      write_log("[#] Çıkılıyor.. \n", level="EXEC")
      write_log("#"*30, level="EXEC")
      sys.exit()
      
def bas_port_kontrol(baslangıc_port):
      write_log("[~] 'bas_port_kontrol()' fonksiyonu çalıştırıldı", level="FUNC")
      if baslangıc_port > 65535:
         print(f"{clr.k}[!] {get_string('invalid_port')}{clr.r}")
         write_log("[!] Port girdisi 65535'ten büyük olamaz!", level="ERROR")
         cık()
         
def bit_port_kontrol(bitis_port):
      write_log("[~] 'bit_port_kontrol()' fonksiyonu çalıştırıldı", level="FUNC")
      if bitis_port > 65535:
            print(f"{clr.k}[!] {get_string('invalid_port')}{clr.r}")
            write_log("[!] Port girdisi 65535'ten büyük olamaz!", level="ERROR")
            cık()
                
def Vbanner():
     print(fr"""

{clr.am}@@@  @@@  @@@@@@  @@@@@@@  @@@@@@  @@@  @@@ @@@  @@@
{clr.am2}@@!  @@@ !@@     !@@      @@!  @@@ @@!@!@@@ @@!@!@@@
{clr.am3}@!@  !@!  !@@!!  !@!      @!@!@!@! @!@@!!@! @!@@!!@!
{clr.am4} !: .:!      !:! :!!      !!:  !!! !!:  !!! !!:  !!!
{clr.am5}   ::    ::.: :   :: :: :  :   : : ::    :  ::    :
{clr.am6}            Github: https://github.com/midvella
""")

def get_key():
    """Non-blocking key press detection for Linux"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            return sys.stdin.read(1)
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def show_progress(current, total):
    """Prints progress percentage"""
    if total == 0: return
    per = (current / total) * 100
    print(f"\r{clr.s}[#] {get_string('progress')}: %{per:.2f}{clr.r}", end="", flush=True)

