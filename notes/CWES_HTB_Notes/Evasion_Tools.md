## If we are dealing with advanced security tools, we may not be able to use basic, manual obfuscation techniques. In such cases, it may be best to resort to automated obfuscation tools.
- Linux (Bashfuscator)
- Mwegiel@htb[/htb]$ git clone https://github.com/Bashfuscator/Bashfuscator
- Mwegiel@htb[/htb]$ cd Bashfuscator
- Mwegiel@htb[/htb]$ pip3 install setuptools==65
- Mwegiel@htb[/htb]$ python3 setup.py install --user
*Once we have the tool set up, we can start using it from the ./bashfuscator/bin/ directory. There are many flags we can use with the tool to fine-tune our final obfuscated command, as we can see in the -h help menu*
- Windows (DOSfuscation)
- PS C:\htb> git clone https://github.com/danielbohannon/Invoke-DOSfuscation.git
- PS C:\htb> cd Invoke-DOSfuscation
- PS C:\htb> Import-Module .\Invoke-DOSfuscation.psd1
- PS C:\htb> Invoke-DOSfuscation
- Invoke-DOSfuscation> help
*We can even use tutorial to see an example of how the tool works. Once we are set, we can start using the tool*
