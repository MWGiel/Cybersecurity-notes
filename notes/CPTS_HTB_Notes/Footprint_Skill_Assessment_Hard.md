This writeup details the steps taken to gain access to a target machine and retrieve credentials for user "HTB".

---

#### Network Reconnaissance

The initial Nmap scan revealed an open SNMP port (161/UDP) on the target. This was the first entry point.

```bash
Nmap 7.95 scan result:
10.129.202.20 port 161/udp open SNMP
```

---

#### SNMP Enumeration

A scan of the SNMP service using the default community string "backup" yielded significant information including:

```bash
snmpwalk -v1 -c backup 10.129.202.20
```

Important discoveries included:

- System: Linux NIXHARD 5.4.0-90-generic
- Admin email: tech@inlanefreight.htb
- Hostname: NIXHARD
- Skript: /opt/tom-recovery.sh
- User credentials: tom:NMds732Js2761
- Password change errors for user "tom"

---

#### Obtaining the Private SSH Key

With the credentials tom:NMds732Js2761, access to the POP3 mailbox was gained:

```bash
telnet 10.129.202.20 110
USER tom
PASS NMds732Js2761
```

Within the mailbox, a message with the subject "KEY" contained an OPENSSH private key for user "tom".

The key was saved to a file with proper permissions and used to authenticate via SSH:

```bash
chmod 600 tom_private_key
ssh -i tom_private_key tom@10.129.202.20
```

---

#### System Internal Reconnaissance

Upon successful SSH authentication, the following information was gathered:

```bash
whoami              # tom
id                    # uid=1002(tom) gid=1002(tom) groups=1002(tom),119(mysql)
ls /home            # cry0l1t3, tom, ubuntu
```

The user "tom" was member of the "mysql" group, which was a critical observation.

---

#### MySQLAccess

The password "NMds732Js2761" was used to authenticate to the mysql database:

```bash
mysql -u tom -p
Show databases;
Use users;
Show tables;
Select * from users;
```

The "users" database contained a table with multiple entries, including the target user":

````ruby
id | username | password
-----+------------------+----------------------------------
150 | HTB       | cr3n4o7rzse7rzhnkchssncif7ds
```

---
#### Lessons Learned

- SNMP is often overlooked but can contain sensitive information
- Services like POP3 can be gateways to other services (e.g., SSH)
- Local MySQL access can be gained through reused credentials
- Databases often store passwords in plain text for virtual users

---

This writeup demonstrates a chain of attack starting from SNMP enumeration and leading to full system access through credential reuse.
