## What are ACLs?
**Access Control Lists (ACLs)** define:
- Who has access to resources
- What level of access they have

## Two Types of ACLs:
| Type | Description |
|------|--------------------------|
| **DACL** | Defines which users/groups have access (Allow/Deny) |
| **SACL** | Audit logging - records access attempts |

## ACL Components - ACE (Access Control Entries)
Each ACE contains:
- **SID** of the user/group
- **Type** (Allow, Deny, Audit)
- **Inheritance flags**
- **Access mask** (permissions)

## Why ACLs Matter for Attackers?
- **Invisible** to vulnerability scanners
- Often **unchanged for years*
- Enables **lateral movement** and **privilege escalation**

## Key Abusable Permissions

| Permission | What it Allows | Tool |
|------------|------------------------|--------|
| **ForceChangePassword** | Reset user's password | Set-DomainUserPassword |
| **GenericAll** | Full control over object | Set-DomainUserPassword or Add-DomainGroupMember |
| **GenericWrite** | Modify object attributes | Set-DomainObject |
| **AddSelf** | Add yourself to a group | Add-DomainGroupMember |
| **WriteOwner** | Change object owner | Set-DomainObjectOwner |
| **WriteDACL** | Modify permissions | Add-DomainObjectACL |
| **AddMember** | Add members to group | Add-DomainGroupMember |

## Common Attack Scenarios

### 1. Abuse "Forgot Password" Permissions
- Help Desk has password reset rights
- Compromise such account -> reset admin's password

### 2. Abuse Group Membership Management
- Help Desk can add/remove users from groups
- Add controlled account to privileged group

### 3. Excessive User Rights
- Over-permissioned accounts (e.g., after Exchange install)
- Legacy/accidental configurations

## Tools for Enumeration & Exploitation
- **BloodHound** - ACL visualization
- **PowerView** - enumeration and exploitation
- **GMSAPasswordReader** - read gMSA passwords

## Important Warnings
1. Some attacks are **destructive** (e.g., password resets)
2. Always **consult client** before execution
3. **Document everything** - every change made
4. **Revert changes** after testing

## Attack Use Cases
ACL abuse enables:
- Lateral movement
- Privilege escalation
- Persistence establishment

## Example PowerShell Commands

### Enumerate ACLs with PowerView
powershell

Find-InterestingDomainAcl -ResolveGUIDs

Get-DomainObjectAcl -Identity "username" -ResolveGUIDs

Get-DomainObjectAcl -LDAPFilter "(objectClass=user)" | Where-Object { $_.ActiveDirectoryRights -match "ExtendedRight" }

### Exploit ACL Attacks
powershell

# Force change password
Set-DomainUserPassword -Identity "targetuser" -AccountPassword (Convert-ToSecureString "NewPassword123!" -AsOlainText -Force)

# Add user to group
Add-DomainGroupMember -Identity "Domain Admins" -Members "hacker"

# GenericWrite - set SPN for Kerrobroasting
Set-DomainObject -Identity "targetuser" -Set @{serviceprincipalname="fake/http"}

## Quick Checklist for ACL Abuse
1. Enumerate with BloodHound or PowerView
2. Identify abusable ACEs
3. Verify permissions exist
4. Consult client if destructive
5. Execute attack
6. Document everything
7. Revert changes

## Remember
ACL abuse is an **advanced technique** that requires:
- Patience in enumeration
- Careful documentation
- Client communication for destructive actions
- Clean cleanup after testing
