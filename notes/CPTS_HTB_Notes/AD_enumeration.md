# Additional AD Auditing Techniques - Quick Reference


---

## 1. AD Explorer (Sysinternals)

### Description
Advanced AD viewer and editor. Allows you to:
- Browse AD database
- Create snapshots for offline analysis
- Compare before/after changes
- Run advanced searches

### Create Snapshot
```
file → create snapshot
```

---

## 2. PingCastle

### Description
AD security assessment tool. Generates reports with:
- Risk score (CMMI scale)
- Anomalies and issues
- Domain and trust maps
- Vulnerabilities and misconfigurations

### Usage
``ccmd
PingCastle.exe --help
PingCastle.exe
```

### Modes
- ``healthcheck`` - domain risk assessment
- ```scanner`` - specific tests (ACL, LAPS, ZeroLogon, Spooler)
- ```conso`` - aggregate reports
- ```carto`` - domain mapping

---

## 3. Group3r

### Description
GPO (Group Policy) auditing tool. Finds vulnerabilities in group policies.

### Usage
``ccmd
group3ir.exe -f <output.log>
group3r.exe -s  # stdout
```

### Output Structure
- No indent → GPO
- One indent → Policy settings
- Two indents → Findings

---

## 4. ADRecon

### Description
Comprehensive AD data collector:
- Users and SPNs
- Groups and memberships
- GPOs and gPLinks
- DNS, printers, computers
- LAPS, BitLocker
- Trusts, sites, subnets

### Usage
```powershell
.\ADRecon.ps1
```

### Output
- CSV files
- HTML report
- GPO report (XML)

---

## Tools Comparison

| Tool | Purpose | Output |
|------|------------------------|---------------|
| AD Explorer | Browse/Snapshot AD | .dat snapshot |
| PingCastle | Security assessment | HTML report |
| Group3r | GPO audit | Log file |
| ADRecon | Comprehensive audit | CSV + HTML |

---

## When to Use Each

| Goal | Tool |
|-------------------------------|------------------|
| Quick security assessment | PingCastle |
| Deep GPO audit | Group3r |
| Complete AD audit | ADRecon |
| Compare AD changes | AD Explorer |
| Offline AD analysis | AD Explorer (snapshot) |

---

## Key Takeaways

1. **PingCastle** - best for quick security assessment
2. **ADRecon** - complete audit (run it every time)
3. **Group3r** - specialized GPO auditing
4. **AD Explorer** - useful for offline analysis and comparisons
5. Reports help convince clients to fix found issues

---

## Quick Commands

```ccmd
# PingCastle interactive
PingCastle.exe

# Group3r to file
group3r.exe -f report.log

# ADRecon
.\ADRecon.ps1
```
