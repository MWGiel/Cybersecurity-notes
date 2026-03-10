LDAP (Lightweight Directory Access Protocol) is a protocol used to access and manage directory information. A directory is a hierarchical data store that contains information about network resources such as users, groups, computers, printers, and other devices.
## LDAP is 
commonly used for providing a central location for accessing and managing directory services. Directory services are collections of information about the organisation, its users, and assets–like usernames and passwords. LDAP enables organisations to store, manage, and secure this information in a standardised way. Here are some common use cases:
## LDAP works 
by using a client-server architecture. A client sends an LDAP request to a server, which searches the directory service and returns a response to the client. LDAP is a protocol that is simpler and more efficient than X.500, on which it is based. It uses a client-server model, where clients send requests to servers using LDAP messages encoded in ASN.1 (Abstract Syntax Notation One) and transmitted over TCP/IP (Transmission Control Protocol/Internet Protocol). The servers process the requests and send back responses using the same format. LDAP supports various requests, such as bind, unbind, search, compare, add, delete, modify, etc.
## ldapsearch
For example, ldapsearch is a command-line utility used to search for information stored in a directory using the LDAP protocol. It is commonly used to query and retrieve data from an LDAP directory service.
````bash
$ ldapsearch -H ldap://ldap.example.com:389 -D "cn=admin,dc=example,dc=com" -w secret123 -b "ou=people,dc=example,dc=com" "(mail=john.doe@example.com)"
````
- Connect to the server ldap.example.com on port 389.
- Bind (authenticate) as cn=admin,dc=example,dc=com with password secret123.
- Search under the base DN ou=people,dc=example,dc=com.
- Use the filter (mail=john.doeexample) to find entries that have this email address.
## LDAP Injection
LDAP injection is an attack that exploits web applications that use LDAP (Lightweight Directory Access Protocol) for authentication or storing user information. The attacker can inject malicious code or characters into LDAP queries to alter the application's behaviour, bypass security measures, and access sensitive data stored in the LDAP directory.
- LDAP injection attacks are similar to SQL injection attacks but target the LDAP directory service instead of a database.
# Injection
As OpenLDAP runs on the server, it is safe to assume that the web application running on port 80 uses LDAP for authentication.

Attempting to log in using a wildcard character (*) in the username and password fields grants access to the system, effectively bypassing any authentication measures that had been implemented. This is a significant security issue as it allows anyone with knowledge of the vulnerability to gain unauthorised access to the system and potentially sensitive data.
