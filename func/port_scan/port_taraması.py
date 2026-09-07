from settings.set_loging import write_log
import time,socket,threading
from settings import set_themes as clr

acık_port = []
port_lock = threading.Lock()

def port_taraması(ip, port, timeout=0.5):
    """
    Standart TCP Connect taraması yapar.
    
    Returns:
        dict: {"port": port, "status": "open"|"closed"|"filtered", "time": str}
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    result = {"port": port, "status": "closed", "time": "0.0000000000"}
    
    try:
        start_time = time.time()
        sonuc = s.connect_ex((ip, port))
        son_time = time.time() - start_time
        result["time"] = f"{son_time:.10f}"
        
        if sonuc == 0:
            result["status"] = "open"
            with port_lock:
                acık_port.append((port, result["time"]))
        elif sonuc == 11 or sonuc == 110: # EAGAIN or ETIMEDOUT
            result["status"] = "filtered"
            
    except socket.timeout:
        result["status"] = "filtered"
    except (ConnectionRefusedError, socket.error):
        result["status"] = "closed"
    except Exception as e:
        write_log(f"[!] Port {port} hatası: {e}", level="ERROR")
    finally:
        s.close()
    
    return result
