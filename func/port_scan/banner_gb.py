from settings.set_loging import write_log
write_log("[&] 'banner_gb.py' dosyası çalıştırıldı", level="EXEC")

import socket
import re

# Banner pattern veritabanı: (regex_pattern, servis_adı)
BANNER_PATTERNS = [
    # Web Sunucuları
    (r"HTTP/\d", "HTTP Servisi"),
    (r"Apache", "Apache HTTP Server"),
    (r"nginx", "Nginx Web Server"),
    (r"Microsoft-IIS", "Microsoft IIS"),
    (r"LiteSpeed", "LiteSpeed Web Server"),
    (r"Caddy", "Caddy Web Server"),
    
    # SSH
    (r"SSH-\d", "SSH Servisi"),
    (r"OpenSSH", "OpenSSH"),
    (r"Dropbear", "Dropbear SSH"),
    (r"libssh", "libssh"),
    
    # FTP
    (r"220.*FTP", "FTP Servisi"),
    (r"vsFTPd", "vsFTPd"),
    (r"ProFTPD", "ProFTPD"),
    (r"Pure-FTPd", "Pure-FTPd"),
    (r"FileZilla Server", "FileZilla FTP Server"),
    (r"Microsoft FTP", "Microsoft FTP"),
    
    # Veritabanları
    (r"MariaDB", "MariaDB Veritabanı"),
    (r"mysql", "MySQL Veritabanı"),
    (r"PostgreSQL", "PostgreSQL Veritabanı"),
    (r"MongoDB", "MongoDB Veritabanı"),
    (r"Redis", "Redis Veritabanı"),
    (r"Memcached", "Memcached"),
    (r"CouchDB", "CouchDB"),
    (r"Elasticsearch", "Elasticsearch"),
    
    # Mail
    (r"SMTP", "SMTP Mail Servisi"),
    (r"Postfix", "Postfix Mail Server"),
    (r"Sendmail", "Sendmail"),
    (r"Exim", "Exim Mail Server"),
    (r"Dovecot", "Dovecot IMAP/POP3"),
    (r"IMAP", "IMAP Servisi"),
    (r"POP3", "POP3 Servisi"),
    (r"Courier", "Courier Mail Server"),
    
    # Diğer
    (r"AMQP", "RabbitMQ / AMQP"),
    (r"RabbitMQ", "RabbitMQ"),
    (r"Samba", "Samba Dosya Paylaşımı"),
    (r"SMB", "SMB Servisi"),
    (r"VNC", "VNC Uzak Masaüstü"),
    (r"RFB", "VNC (RFB Protokolü)"),
    (r"RTSP", "RTSP Akış Servisi"),
    (r"SIP", "SIP VoIP Servisi"),
    (r"BitTorrent", "BitTorrent"),
    (r"Squid", "Squid Proxy"),
    (r"HAProxy", "HAProxy Yük Dengeleyici"),
    (r"Varnish", "Varnish Cache"),
    (r"Jetty", "Eclipse Jetty"),
    (r"Tomcat", "Apache Tomcat"),
    (r"WildFly", "WildFly (JBoss)"),
    (r"Express", "Node.js Express"),
    (r"MQTT", "MQTT IoT Protokolü"),
    (r"Telnet", "Telnet Servisi"),
    (r"DNS", "DNS Servisi"),
    (r"LDAP", "LDAP Dizin Servisi"),
    (r"Kerberos", "Kerberos Kimlik Doğrulama"),
    (r"Docker", "Docker API"),
    (r"Kubernetes", "Kubernetes API"),
    (r"Prometheus", "Prometheus Monitoring"),
    (r"Grafana", "Grafana Dashboard"),
    (r"Jenkins", "Jenkins CI/CD"),
    (r"GitLab", "GitLab"),
    (r"Webmin", "Webmin Panel"),
    (r"cPanel", "cPanel Panel"),
    (r"Minecraft", "Minecraft Sunucusu"),
    (r"Valve", "Valve Source Sunucusu"),
    (r"CoAP", "CoAP IoT Protokolü"),
    (r"X-Jenkins", "Jenkins CI/CD"),
    (r"X-Prometheus", "Prometheus Monitoring"),
]

def banner_grabbing(ip, port):
    """Gelişmiş banner grabbing - pattern veritabanı ile servis tespiti"""
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((ip, port))
        
        # Bazı servisler önce banner gönderir (SSH, FTP, SMTP vb.)
        banner = ""
        try:
            banner = s.recv(1024).decode("latin-1", errors="ignore").strip()
        except socket.timeout:
            pass
        
        # Banner boş ise HTTP isteği dene
        if not banner:
            try:
                s.send(b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n")
                banner = s.recv(2048).decode("latin-1", errors="ignore").strip()
            except:
                pass
        
        s.close()
        
        if not banner:
            return "Banner alınamadı (bağlantı başarılı)"
        
        # Pattern eşleştirme
        for pattern, servis_adi in BANNER_PATTERNS:
            if re.search(pattern, banner, re.IGNORECASE):
                # İlk satırı al (özet)
                ilk_satir = banner.split("\n")[0][:120]
                return f"{servis_adi} - {ilk_satir}"
        
        # Bilinmeyen servis - ilk satırı döndür
        ilk_satir = banner.split("\n")[0][:120]
        return f"Bilinmeyen Servis - {ilk_satir}"
        
    except socket.timeout:
        return "Banner alınamadı (zaman aşımı)"
    except ConnectionRefusedError:
        return "Banner alınamadı (bağlantı reddedildi)"
    except socket.error as e:
        return f"Banner alınamadı ({e})"
    except Exception as e:
        return f"Banner alınamadı ({e})"

def versiyon_cikar(banner):
    """Banner'dan versiyon numarasını çıkarmaya çalışır.
    
    Desteklenen formatlar: X.Y.Z, X.Y, X.Y.Zp1, X.Y.Z-betaN vb.
    
    Args:
        banner: Banner string
        
    Returns:
        str: Versiyon numarası veya None
    """
    if not banner:
        return None
    
    # Yaygın versiyon formatları
    patterns = [
        r'(\d+\.\d+\.\d+[-\w]*)',   # X.Y.Z veya X.Y.Z-beta1, X.Y.Zp1
        r'(\d+\.\d+[-\w]*)',         # X.Y veya X.Y-rc1
    ]
    
    for pattern in patterns:
        match = re.search(pattern, banner)
        if match:
            return match.group(1)
    
    return None
