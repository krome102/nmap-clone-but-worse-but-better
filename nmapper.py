import socket
import threading
from queue import Queue
import re
import sys
import ssl
import subprocess
import platform
import json

print(r""" ██████   █████ ██████████ █████  █████ ███████████   █████   ████ ███████████      ███████    ██████   ██████ ██████████   █████████   ██████   █████   █████████  ██████████ ███████████  
░░██████ ░░███ ░░███░░░░░█░░███  ░░███ ░░███░░░░░███ ░░███   ███░ ░░███░░░░░███   ███░░░░░███ ░░██████ ██████ ░░███░░░░░█  ███░░░░░███ ░░██████ ░░███   ███░░░░░███░░███░░░░░█░░███░░░░░███ 
 ░███░███ ░███  ░███  █ ░  ░███   ░███  ░███    ░███  ░███  ███    ░███    ░███  ███     ░░███ ░███░█████░███  ░███  █ ░  ░███    ░███  ░███░███ ░███  ███     ░░░  ░███  █ ░  ░███    ░███ 
 ░███░░███░███  ░██████    ░███   ░███  ░██████████   ░███████     ░██████████  ░███      ░███ ░███░░███ ░███  ░██████    ░███████████  ░███░░███░███ ░███          ░██████    ░██████████  
 ░███ ░░██████  ░███░░█    ░███   ░███  ░███░░░░░███  ░███░░███    ░███░░░░░███ ░███      ░███ ░███ ░░░  ░███  ░███░░█    ░███░░░░░███  ░███ ░░██████ ░███          ░███░░█    ░███░░░░░███ 
 ░███  ░░█████  ░███ ░   █ ░███   ░███  ░███    ░███  ░███ ░░███   ░███    ░███ ░░███     ███  ░███      ░███  ░███ ░   █ ░███    ░███  ░███  ░░█████ ░░███     ███ ░███ ░   █ ░███    ░███ 
 █████  ░░█████ ██████████ ░░████████   █████   █████ █████ ░░████ █████   █████ ░░░███████░   █████     █████ ██████████ █████   █████ █████  ░░█████ ░░█████████  ██████████ █████   █████
░░░░░    ░░░░░ ░░░░░░░░░░   ░░░░░░░░   ░░░░░   ░░░░░ ░░░░░   ░░░░ ░░░░░   ░░░░░    ░░░░░░░    ░░░░░     ░░░░░ ░░░░░░░░░░ ░░░░░   ░░░░░ ░░░░░    ░░░░░   ░░░░░░░░░  ░░░░░░░░░░ ░░░░░   ░░░░░ 
                                                                                                                                                                                            
                                                                                                                                                                                            
                                                                                                                                                                                            """)

ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
port_range_pattern = re.compile(r'^(\d+)-(\d+)$')

while True:
    ip = input("Victim's IP: ").strip()
    if ip_pattern.search(ip):
        print(f"{ip} — COMPUTAH! SCAN THE NETWORK!\n")
        break
    print("[!] Invalid IP format. Try again.")

while True:
    port_range = input("Enter port range (e.g. 1-1024): ").strip()
    match = port_range_pattern.search(port_range.replace(" ", ""))
    if match:
        port_min = int(match.group(1))
        port_max = int(match.group(2))
        break
    print("[!] Invalid range. Use format like '1-1000'.")

open_ports = []
print_lock = threading.Lock()
port_queue = Queue()

for port in range(port_min, port_max + 1):
    port_queue.put(port)

def scanner():
    while not port_queue.empty():
        port = port_queue.get()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                s.connect((ip, port))
                with print_lock:
                    open_ports.append(port)
                    print(f"[+] Port {port} is OPEN")
        except:
            pass
        finally:
            port_queue.task_done()

num_threads = 200
print(f"[*] Scanning {port_min}-{port_max} on {ip} with {num_threads} threads...\n")

threads = []
for _ in range(num_threads):
    t = threading.Thread(target=scanner, daemon=True)
    t.start()
    threads.append(t)

port_queue.join()

print("\n" + "=" * 40)
print(f"SCAN COMPLETE — {ip}")
print("=" * 40)
if open_ports:
    open_ports.sort()
    for port in open_ports:
        print(f"  Port {port} is OPEN")
else:
    print("  No open ports found in range.")
print("=" * 40)

# alien hentai tentacles probing

PROBES = {
    21:    b"",                                    # FTP   -> server greets
    22:    b"",                                    # SSH   -> server greets
    23:    b"",                                    # Telnet
    25:    b"",                                    # SMTP  -> greet
    79:    b"",                                    # Finger
    80:    b"HEAD / HTTP/1.0\r\nHost: x\r\n\r\n",  # HTTP
    110:   b"",                                    # POP3  -> greet
    143:   b"",                                    # IMAP  -> greet
    443:   b"",                                    # TLS   -> handshake
    445:   b"",                                    # SMB
    993:   b"",                                    # IMAPS
    995:   b"",                                    # POP3S
    3306:  b"",                                    # MySQL -> greet
    5432:  b"",                                    # PostgreSQL
    6379:  b"INFO server\r\n",                     # Redis
    8080:  b"HEAD / HTTP/1.0\r\nHost: x\r\n\r\n",
    8443:  b"",
    27017: b"",                                    # MongoDB
}
GENERIC_PROBE = b"\r\n"
TLS_PORTS = {443, 465, 636, 993, 995, 8443, 9443}

# banner sigs
# {n} in the format string is substituted with the n-th capture group. not that youd care

SIGNATURES = [
    ("ssh",    re.compile(rb"SSH-([\d.]+)-([^\r\n]+)"),                         "SSH {2} (proto {1})"),
    ("smtp",   re.compile(rb"^220[ -]([^\r\n]+)", re.I),                        "{1}"),
    ("ftp",    re.compile(rb"^220[ -]([^\r\n]+)", re.I),                        "{1}"),
    ("http",   re.compile(rb"Server:\s*([^\r\n]+)", re.I),                      "{1}"),
    ("http",   re.compile(rb"^HTTP/([\d.]+)"),                                  "HTTP/{1}"),
    ("redis",  re.compile(rb"redis_version:([\d.]+)"),                          "Redis {1}"),
    ("mysql",  re.compile(rb"([\d]+\.[\d]+\.[\d]+)[^\r\n\x00]*?(MariaDB[^\r\n\x00]*)", re.I), "MySQL {1} {2}"),
    ("mysql",  re.compile(rb"([\d]+\.[\d]+\.[\d]+)[^\r\n\x00]*MySQL", re.I),    "MySQL {1}"),
    ("mysql",  re.compile(rb"mysql_native_password", re.I),                     "MySQL (version hidden)"),
    ("pgsql",  re.compile(rb"(PostgreSQL|invalid length of startup packet)", re.I), "PostgreSQL"),
    ("mongo",  re.compile(rb"ismaster|MongoDB", re.I),                          "MongoDB"),
    ("tls",    re.compile(rb"(TLSv[\d.]+)"),                                    "{1}"),
    ("telnet", re.compile(rb"login:|Password:", re.I),                          "Telnet service"),
    ("vnc",    re.compile(rb"RFB ([\d.]+)"),                                    "VNC {1}"),
]

# scanners hints more about the os than girls will ever hint at you

OS_BANNER_HINTS = [
    (re.compile(r"ubuntu", re.I),                   "Ubuntu Linux"),
    (re.compile(r"debian", re.I),                   "Debian Linux"),
    (re.compile(r"centos|red ?hat", re.I),          "CentOS / RHEL Linux"),
    (re.compile(r"freebsd", re.I),                  "FreeBSD"),
    (re.compile(r"microsoft|iis|win32|windows", re.I), "Windows"),
    (re.compile(r"cisco|ios-", re.I),               "Cisco IOS"),
]


# banner grab

def _read_all(sock, limit=4096, timeout=2.5):
    data = b""
    sock.settimeout(timeout)
    while len(data) < limit:
        try:
            chunk = sock.recv(1024)
        except (socket.timeout, ssl.SSLError):
            break
        except OSError:
            break
        if not chunk:
            break
        data += chunk
    return data


def grab_banner(host, port, timeout=2.5):
    """Connect to a port, optionally send a probe, return (banner, tls_info)."""
    probe = PROBES.get(port, GENERIC_PROBE)
    tls_info = None
    raw = b""

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        if port in TLS_PORTS:
            try:
                ctx = ssl._create_unverified_context()
                sock = ctx.wrap_socket(sock, server_hostname=host)
                tls_info = sock.version() or ""
                try:
                    cert = sock.getpeercert()
                    if cert:
                        subj = dict(x[0] for x in cert.get("subject", []))
                        tls_info += " | CN=" + subj.get("commonName", "?")
                except Exception:
                    pass
                raw = _read_all(sock, timeout=timeout)
                sock.close()
                return (tls_info.encode(), tls_info)
            except Exception:
                pass  # not actually tls js plain

        if probe:
            sock.sendall(probe)
        raw = _read_all(sock, timeout=timeout)
        sock.close()
    except Exception:
        return (b"", None)

    return (raw, tls_info)


# svc/ver identifier

def identify_service(banner, port, tls_info=None):
    """Return (service, version_string) from raw banner bytes."""
    service, version = "unknown", ""

    if tls_info:
        service, version = "tls", tls_info

    for name, pat, fmt in SIGNATURES:
        m = pat.search(banner)
        if not m:
            continue
        # build version string from the capture-group format
        try:
            version = fmt.format(*([""] + [g.decode(errors="replace") if isinstance(g, bytes) else g
                                           for g in m.groups()]))
        except Exception:
            version = ""
        service = name
        break

    if not version:

        # generic "product/version" fallback: nginx/1.18.0, Apache/2.4.41, OpenSSH_8.9

        gm = re.search(rb"([A-Za-z][\w.\-]+)[/_]([\d][\d.\w]*)", banner)
        if gm:
            version = f"{gm.group(1).decode()} {gm.group(2).decode()}"

    if service == "unknown" and version:
        service = "generic"
    return service, version.strip()


# os identifier

def ping_ttl(host):
    """Send one ICMP echo and extract the reply TTL (no root needed)."""
    win = platform.system().lower().startswith("win")
    cmd = ["ping", "-n", "1", "-w", "1000", host] if win \
        else ["ping", "-c", "1", "-W", "1", host]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL,
                                      timeout=5).decode(errors="ignore")
    except Exception:
        return None
    m = re.search(r"ttl[=\s](\d+)", out, re.I)
    return int(m.group(1)) if m else None


def guess_os_from_ttl(ttl):
    if ttl is None:
        return "Unknown (no ICMP reply / host filtered)"
    if ttl > 128:
        return "Network device / Solaris / AIX (initial TTL ~255)"
    if ttl > 64:
        return "Windows (initial TTL ~128)"
    return "Linux / Unix / macOS (initial TTL ~64)"


def os_hints_from_banners(results):
    hits = set()
    for _, _, _, banner, *_ in results:
        text = banner.decode(errors="ignore") if isinstance(banner, bytes) else str(banner)
        for pat, label in OS_BANNER_HINTS:
            if pat.search(text):
                hits.add(label)
    return sorted(hits)


# bermuda scan

def scan_one(host, port, results):
    banner, tls_info = grab_banner(host, port)
    service, version = identify_service(banner, port, tls_info)
    preview = banner[:120].replace(b"\r", b"").replace(b"\n", b" | ")
    with print_lock:
        results.append((port, service, version, banner, preview))


def deep_scan(host, ports):
    print(f"\n[*] Fingerprinting {len(ports)} open service(s) on {host} ...\n")
    results = []
    threads = []
    for p in ports:
        t = threading.Thread(target=scan_one, args=(host, p, results), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    results.sort(key=lambda r: r[0])

    print("=" * 78)
    print(f"{'PORT':<7}{'SERVICE':<10}{'VERSION / DETAILS'}")
    print("-" * 78)
    for port, service, version, banner, preview in results:
        print(f"{port:<7}{service:<10}{version or '(no version in banner)'}")
        if preview:
            print(f"       └─ banner: {preview.decode(errors='replace')}")
    print("=" * 78)

    ttl = ping_ttl(host)
    banner_hints = os_hints_from_banners(results)
    print(f"[*] ICMP TTL              : {ttl if ttl is not None else 'n/a'}")
    print(f"[*] OS guess (TTL)        : {guess_os_from_ttl(ttl)}")
    if banner_hints:
        print(f"[*] OS hints (banners)    : {', '.join(banner_hints)}")
    print("=" * 78)

# saves results

    report = {
        "target": host,
        "icmp_ttl": ttl,
        "os_ttl_guess": guess_os_from_ttl(ttl),
        "os_banner_hints": banner_hints,
        "services": [
            {"port": p, "service": s, "version": v,
             "banner": b.decode(errors="replace")}
            for p, s, v, b, _ in results
        ],
    }
    fname = f"scan_{host.replace('.', '_')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[+] Report saved -> {fname}")
    return report


# runs sprints even

if open_ports:
    deep_scan(ip, sorted(open_ports))
else:
    print("[!] No open ports to fingerprint.")
