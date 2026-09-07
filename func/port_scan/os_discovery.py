import os
from settings.set_lang import get_string

def is_root():
    return os.geteuid() == 0

def estimate_os(ip, timeout=2.0):
    """
    Estimates the target OS using TCP/IP fingerprinting basics.
    Focuses on TTL and Window Size.
    """
    try:
        from scapy.all import IP, TCP, sr1
    except ImportError:
        from settings import set_themes as clr
        return f"Error: {get_string('scapy_missing')}"

    if not is_root():
        return "Unknown (Root required for OS discovery)"
        
    try:
        # Send a SYN packet to an likely open port (or just any port and see the RST)
        packet = IP(dst=ip)/TCP(dport=80, flags="S")
        resp = sr1(packet, timeout=timeout, verbose=0)
        
        if resp is None:
            return "Unknown (No response)"
            
        ttl = resp.getlayer(IP).ttl
        window = 0
        if resp.haslayer(TCP):
            window = resp.getlayer(TCP).window
            
        # Basic signatures
        if ttl <= 64:
            if window <= 5840:
                return "Linux (Kernel 2.4/2.6)"
            return "Linux / Unix / Android"
        elif ttl <= 128:
            return "Windows"
        elif ttl <= 255:
            return "Cisco / Network Device / Solaris"
            
        return f"Unknown (TTL: {ttl}, Window: {window})"
        
    except Exception as e:
        return f"Error: {e}"

def print_os_info(ip):
    os_name = estimate_os(ip)
    from settings import set_themes as clr
    print(f"\n{clr.s}[#] {get_string('os_guess')}:{clr.r} {os_name}")
