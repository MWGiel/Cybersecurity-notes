import threading
import requests

domain = 'youtube.com'

with open('subdomain.txt') as file:
    subdomains = file.read().splitlines()

discivered_subdomains = []

lock = threading.Lock()

def check_subdomain(subdomain):

    url = f'http://{subdomain}.{domain}'
    try:
        requests.get(url)
    except requests.ConnectionError:
        pass
    else:
        print("[+] Discovered subdomain: ", url)
        with lock:
            discivered_subdomains.append(url)
# Tworzenie i uruchamianie wątków
threads = []
for subdomain in subdomains:
    t = threading.Thread(target=check_subdomain, args=(subdomain,))
    threads.append(t)
    t.start()

# Oczekiwanie na zakończenie wszystkich wątków
for t in threads:
    t.join()

with open("discovered_subdomain.txt", 'w') as f:
    for subdomain in discivered_subdomains:
        print(subdomain, file=f)
