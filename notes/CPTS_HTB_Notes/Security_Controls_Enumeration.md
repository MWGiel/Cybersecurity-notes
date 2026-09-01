Active Directory Security Controls Enumeration Notes

1. Windows Defender (Microsoft Defender)
- Check status:
  Get-MpComputerStatus
  Look for: RealTimeProtectionEnabled (true = active)
- Can block tools like PoverView - bypass possible via obfuscation or alternative tools

2. AppLocker (Whitelisting)
- Restricts which executables/scripts can run (e.g., block powershell.exe)
- Check effective policy:
  Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
- Example: 64-bit PowerShell blocked, but other paths work (SysWOW64/, PowerShell_ISE.exe)
- Bypass options: use alternative paths, C#, or other scripting languages

3. PowerShell Constrained Language Mode
- Limits PowerShell features (blocks COM, some .NET, classes, workflows)
- Check current mode:
  $ExecutionContext.SessionState.LanguageMode
- If 'ConstrainedLanguage' - avoid advanced PowerShell scripts; use .NET or C#
  4. LAPS (Local Administrator Password Solution)
- Randomizes and rotates local admin passwords on domain-joined hosts
- Tool: LAPToolkit (PowerShell)

 Function                    | Purpose
  ------------------------------| --------------------
  Find-LAPDElegatedGroups      | Lists groups with access to LAPS passwords
  Find-AdmPwdExtendedRights   | Finds users with 'All Extended Rights'
  Get-LAPSComputers            | Displays LAPS passwords (if you have permissions)

 Example usage:
  Find-LAPSDelegatedGroups
  Find-AdmPwdExtendedRights
  Get-LAPSComputers

5. Why This Matters
- Tool selection: if Defender/AppLocker blocks common tools, use alternatives
- Find misconfigurations: LAPS may be misconfigured (e.g., regular users can read passwords)
- Avoid detection: knowing the controls helps you plan quieter attacks

6. Quick Reference
------------------------------------------------------------
  Control          | Check Command                     | Bypass / Notes
  ---------------|----------------------------|-----------------------
  Defender        | 'Get-MpComputerStatus'              | Obfuscation, alternate tools
  AppLocker       | 'Get-AppLockerPolicy -Effective' | Use alternative paths / languages
  Constrained Language | '$ExecutionContext.SessionState.LanguageMode' | Use .NET / C
  LAPS             | 'Find-LAPDElegatedGroups'        | Check for excessive permissions
