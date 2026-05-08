# Importujemy potrzebne biblioteki
import scapy.all as scapy  # Do tworzenia i wysyłania pakietów ARP
import socket               # Do odpytywania DNS o nazwy hostów
import threading            # Do równoległego skanowania wielu IP
from queue import Queue     # Do bezpiecznego zbierania wyników z wątków
import ipaddress            # Do obsługi adresów IP i maski CIDR

def scan(ip, result_queue):
    """
    Skanuje pojedynczy adres IP przy użyciu ARP.
    
    Argumenty:
    - ip: adres IP do skanowania (string)
    - result_queue: kolejka do której trafią wyniki (dla wątków)
    """
    
    # Tworzymy zapytanie ARP: "Kto ma ten adres IP?"
    # pdst = destination IP (cel)
    arp_request = scapy.ARP(pdst=ip)
    
    # Tworzymy ramkę Ethernet z adresem broadcast
    # dst="ff:ff:ff:ff:ff:ff" oznacza "wszyscy w sieci"
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    
    # Łączymy warstwę Ethernet z zapytaniem ARP w jeden pakiet
    packet = broadcast / arp_request
    
    # Wysyłamy pakiet i odbieramy odpowiedzi:
    # - srp() = send and receive packet (wyślij i odbierz na warstwie Ethernet)
    # - timeout=1: czekamy 1 sekundę na odpowiedź
    # - verbose=False: nie pokazuj komunikatów
    # - [0]: bierzemy tylko odpowiedzi (pierwszy element krotki)
    answer = scapy.srp(packet, timeout=1, verbose=False)[0]
    
    # Lista na znalezione urządzenia
    clients = []
    
    # Dla każdej odpowiedzi od urządzenia w sieci
    for client in answer:
        # Pobieramy dane z odpowiedzi:
        # - psrc: IP źródłowe (odpowiadającego urządzenia)
        # - hwsrc: MAC źródłowy (fizyczny adres karty sieciowej)
        client_info = {'IP': client[1].psrc, 'MAC': client[1].hwsrc}
        
        # Próbujemy znaleźć nazwę hosta dla tego IP (np. "komputer-piotr")
        try:
            # gethostbyaddr() odwraca DNS: IP -> nazwa hosta
            # [0] bierze pierwszą (główną) nazwę
            hostname = socket.gethostbyaddr(client_info['IP'])[0]
            client_info['Hostname'] = hostname
        except socket.herror:
            # Jeśli nie udało się znaleźć nazwy (błąd DNS)
            client_info['Hostname'] = 'Unknown'
        
        # Dodajemy urządzenie do listy
        clients.append(client_info)
    
    # Wrzucamy wyniki do kolejki (bezpieczne dla wątków)
    result_queue.put(clients)

def print_result(result):
    """
    Wyświetla wyniki skanowania w ładnej tabeli.
    
    Argument:
    - result: lista słowników z danymi urządzeń
    """
    
    # Nagłówki tabeli z odpowiednim odstępem
    print('IP' + " " * 20 + 'MAC' + " " * 20 + 'Hostname')
    print('-' * 80)
    
    # Dla każdego znalezionego urządzenia
    for client in result:
        # Wyświetlamy IP, MAC i nazwę hosta z tabulatorami między kolumnami
        print(client['IP'] + '\t\t' + client['MAC'] + '\t\t' + client['Hostname'])

def main(cidr):
    """
    Główna funkcja programu: zarządza skanowaniem całej sieci.
    
    Argument:
    - cidr: zakres sieci w notacji CIDR (np. "192.168.1.0/24")
    """
    
    # Kolejka do zbierania wyników z wielu wątków (thread-safe)
    results_queue = Queue()
    
    # Lista przechowująca wszystkie utworzone wątki
    threads = []
    
    # Parsujemy zakres sieci z notacji CIDR (np. "192.168.1.0/24")
    # strict=False pozwala na niepełne maski
    network = ipaddress.ip_network(cidr, strict=False)
    
    # Dla każdego adresu IP w zakresie (hosts() pomija adres sieci i broadcast)
    for ip in network.hosts():
        # Tworzymy nowy wątek, który uruchomi funkcję scan() z tym IP
        # args to krotka argumentów dla funkcji scan
        thread = threading.Thread(target=scan, args=(str(ip), results_queue))
        
        # Uruchamiamy wątek
        thread.start()
        
        # Dodajemy wątek do listy (żeby później na niego poczekać)
        threads.append(thread)
    
    # Czekamy na zakończenie WSZYSTKICH wątków
    # join() blokuje program aż wątek zakończy działanie
    for thread in threads:
        thread.join()
    
    # Zbieramy wszystkie wyniki z kolejki
    all_clients = []
    
    # Dopóki w kolejce są jakieś wyniki...
    while not results_queue.empty():
        # Pobieramy wyniki z kolejki (get() wyciąga i usuwa)
        # extend() dodaje elementy listy do all_clients
        all_clients.extend(results_queue.get())
    
    # Wyświetlamy wyniki w ładnej tabeli
    print_result(all_clients)

# Sprawdzamy czy program został uruchomiony bezpośrednio (a nie zaimportowany)
if __name__ == '__main__':
    # Pytamy użytkownika o zakres sieci do skanowania
    # Przykład: 192.168.1.0/24  lub  10.0.0.0/24
    cidr = input("Enter network ip address (np. 192.168.1.0/24): ")
    
    # Uruchamiamy główną funkcję
    main(cidr)
