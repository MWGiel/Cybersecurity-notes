# Kerberos Double Hop Problem - Short Note

## What is it?
Double Hop Problem - when you connect via WinRM Host A, then try to access Host B, authentication fails.

## Why>
- WinRM sends only a TOS ticket (access to Host A)
- TGT ticket (access to entire domain) is NOT sent
- No password is stored in memory
- Can't authenticate further

## Check if you have it
```
powershell
klist
```
- 1 ticket → PROBLEM
- Many tickets → OK

## Fixes

| Method | Command |
|-------|--------------------------------------------------------------|
| PSCredential | get-DomainUser -spn -Credential $Cred |
| Register-PSSessionConfiguration | Register-PSSessionConfiguration -Name sess -RunAsCredential DGMAIN\user |
| Use RDP instead | mstsc /v:HOST-A |

## When it happens

| Tool | Problem? |
|-------|----------|
| WinRM / evil-winrm | YES |
| RDH / PSExec | NO |

## Summary
Summary : WinRM Doesn't Cache Passwords. Use -Credential or RDP to gof further.
