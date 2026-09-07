from settings.set_loging import write_log
import time
import os

# Status mapping
# SYN: SA (0x12) -> open, RA (0x14) -> closed, no response -> filtered
# UDP: response -> open|filtered, port-unreachable -> closed, no response -> open|filtered (usually)

def is_root():
    return os.geteuid() == 0

def syn_scan(ip, port, timeout=1.0):
    """TCP SYN Scan (Half-open)"""
    try:
        from scapy.all import IP, TCP, sr1
    except ImportError:
        from settings import set_themes as clr
        from settings.set_lang import get_string
        return {"port": port, "status": "error", "reason": get_string('scapy_missing'), "time": "0"}

    if not is_root():
        return {"port": port, "status": "error", "reason": "root required", "time": "0"}
    
    start_time = time.time()
    packet = IP(dst=ip)/TCP(dport=port, flags="S")
    resp = sr1(packet, timeout=timeout, verbose=0)
    son_time = time.time() - start_time
    
    result = {"port": port, "status": "filtered", "time": f"{son_time:.10f}"}
    
    if resp is None:
        result["status"] = "filtered"
    elif resp.haslayer(TCP):
        if resp.getlayer(TCP).flags == 0x12: # SYN-ACK
            # Send RST to close the half-open connection
            sr1(IP(dst=ip)/TCP(dport=port, flags="R"), timeout=timeout, verbose=0)
            result["status"] = "open"
        elif resp.getlayer(TCP).flags == 0x14: # RST-ACK
            result["status"] = "closed"
    elif resp.haslayer(ICMP):
        if int(resp.getlayer(ICMP).type) == 3 and int(resp.getlayer(ICMP).code) in [1, 2, 3, 9, 10, 13]:
            result["status"] = "filtered"
            
    return result

def udp_scan(ip, port, timeout=1.0):
    """UDP Scan"""
    try:
        from scapy.all import IP, UDP, sr1, ICMP
    except ImportError:
        from settings import set_themes as clr
        from settings.set_lang import get_string
        return {"port": port, "status": "error", "reason": get_string('scapy_missing'), "time": "0"}

    if not is_root():
        return {"port": port, "status": "error", "reason": "root required", "time": "0"}
        
    start_time = time.time()
    packet = IP(dst=ip)/UDP(dport=port)
    resp = sr1(packet, timeout=timeout, verbose=0)
    son_time = time.time() - start_time
    
    result = {"port": port, "status": "open|filtered", "time": f"{son_time:.10f}"}
    
    if resp is None:
        result["status"] = "open|filtered"
    elif resp.haslayer(UDP):
        result["status"] = "open"
    elif resp.haslayer(ICMP):
        if int(resp.getlayer(ICMP).type) == 3:
            if int(resp.getlayer(ICMP).code) == 3: # Port unreachable
                result["status"] = "closed"
            elif int(resp.getlayer(ICMP).code) in [1, 2, 9, 10, 13]: # Filtered
                result["status"] = "filtered"
                
    return result

def stealth_scan(ip, port, scan_type="FIN", timeout=1.0):
    """NULL, FIN, or XMAS Scan"""
    try:
        from scapy.all import IP, TCP, sr1, ICMP
    except ImportError:
        from settings import set_themes as clr
        from settings.set_lang import get_string
        return {"port": port, "status": "error", "reason": get_string('scapy_missing'), "time": "0"}

    if not is_root():
        return {"port": port, "status": "error", "reason": "root required", "time": "0"}
        
    flags = ""
    if scan_type.upper() == "NULL":
        flags = ""
    elif scan_type.upper() == "FIN":
        flags = "F"
    elif scan_type.upper() == "XMAS":
        flags = "FPU"
        
    start_time = time.time()
    packet = IP(dst=ip)/TCP(dport=port, flags=flags)
    resp = sr1(packet, timeout=timeout, verbose=0)
    son_time = time.time() - start_time
    
    result = {"port": port, "status": "open|filtered", "time": f"{son_time:.10f}"}
    
    if resp is None:
        result["status"] = "open|filtered"
    elif resp.haslayer(TCP):
        if resp.getlayer(TCP).flags == 0x14: # RST
            result["status"] = "closed"
    elif resp.haslayer(ICMP):
        if int(resp.getlayer(ICMP).type) == 3 and int(resp.getlayer(ICMP).code) in [1, 2, 3, 9, 10, 13]:
            result["status"] = "filtered"
            
    return result
