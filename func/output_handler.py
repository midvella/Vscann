import json
from settings import set_themes as clr

def format_json(results, target_info=None):
    """Formats scan results as a JSON string."""
    data = {
        "target": target_info or {},
        "results": results
    }
    return json.dumps(data, indent=4, ensure_ascii=False)

def print_verbose_result(res):
    """Prints a detailed result line for a port."""
    port = res["port"]
    status = res["status"]
    time_val = res["time"]
    
    color = clr.s
    if status == "open":
        color = clr.y
    elif status == "closed":
        color = clr.k
    elif status == "filtered":
        color = clr.am
    elif status == "error":
        color = clr.k
        
    print(f"\t{color}[*] Port: {port:<6} | Durum: {status:<15} | Süre: {time_val}{clr.r}")

def save_json_output(filename, json_data):
    """Saves JSON data to a file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_data)
        return True
    except Exception as e:
        print(f"{clr.k}[!] JSON dosyası kaydedilemedi: {e}{clr.r}")
        return False
