import socket 
import concurrent.futures
import sys

# ============================================================
# KOLORY DO WYŚWIETLANIA W KONSOLI
# ============================================================
RED = "\033[91m"      # Czerwony kolor - dla otwartych portów
GREEN = "\033[92m"    # Zielony kolor - dla bannerów
RESET = "\033[0m"     # Reset koloru - powrót do domyślnego

# ============================================================
# FUNKCJA: format_port_result(results)
# CEL: Formatowanie i wyświetlanie wyników skanowania portów
# ARGUMENTY:
#   results - lista krotek (port, service, banner, status)
# ZWRACA: sformatowany string z wynikami skanowania
# ============================================================
def format_port_result(results):
    # Sprawdź czy są jakieś wyniki
    if not results:
        return "No open ports found."
    
    # Nagłówek tabeli wyników
    formatted_results = "Port Scan Results:\n"
    formatted_results += "{:<8} {:<15} {:<10}\n".format("Port", "Service", "Status")
    formatted_results += '-' * 35 + "\n"
    
    # Przejdź przez każdy wynik w liście
    for port, service, banner, status in results:
        if status:  # Tylko dla portów otwartych (status = True)
            # Dodaj informację o otwartym porcie (na czerwono)
            formatted_results += f"{RED}{port:<8} {service:<15} {'Open':<10}{RESET}\n"
            # Jeśli jest banner (odpowiedź serwisu), wyświetl go na zielono
            if banner and banner.strip():
                banner_lines = banner.split('\n')
                for line in banner_lines:
                    if line.strip():
                        formatted_results += f"{GREEN}{'':<8}{line.strip()}{RESET}\n"
    
    return formatted_results  

# ============================================================
# FUNKCJA: get_banner(sock)
# CEL: Pobranie banera (powitania) z otwartego portu
# ARGUMENTY:
#   sock - obiekt gniazda (socket) połączonego z portem
# ZWRACA: string z bannerem lub pusty string w przypadku błędu
# ============================================================
def get_banner(sock):
    try:
        sock.settimeout(1)  # Ustaw timeout na 1 sekundę
        banner = sock.recv(1024).decode().strip()  # Odbierz do 1024 bajtów
        return banner
    except:
        return " "  # W razie błędu zwróć pusty string

# ============================================================
# FUNKCJA: scan_port(target_ip, port)
# CEL: Skanowanie pojedynczego portu na podanym hoście
# ARGUMENTY:
#   target_ip - adres IP celu (string)
#   port - numer portu do skanowania (int)
# ZWRACA: krotka (port, service, banner, status)
#   status = True jeśli port otwarty, False jeśli zamknięty
# ============================================================
def scan_port(target_ip, port):
    sock = None  # Inicjalizacja gniazda
    try:
        # Utwórz gniazdo TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout 1 sekunda
        
        # Próbuj połączyć się z portem (connect_ex zwraca 0 gdy sukces)
        result = sock.connect_ex((target_ip, port))
        
        if result == 0:  # Port jest otwarty!
            try:
                # Spróbuj pobrać nazwę usługi dla tego portu
                service = socket.getservbyport(port, 'tcp')
            except:
                service = 'Unknown'  # Jeśli nie znany, oznacz jako 'Unknown'
            
            banner = get_banner(sock)  # Pobierz banner z portu
            return port, service, banner, True  # Zwróć info o otwartym porcie
        else:
            return port, "", "", False  # Port zamknięty
            
    except Exception as e:
        return port, "", "", False  # Błąd - traktuj jako zamknięty
    finally:
        if sock:
            sock.close()  # Zawsze zamknij gniazdo

# ============================================================
# FUNKCJA: port_scan(target_host, start_port, end_port)
# CEL: Główna funkcja skanująca zakres portów z użyciem wielowątkowości
# ARGUMENTY:
#   target_host - adres IP lub nazwa hosta (string)
#   start_port - pierwszy port do skanowania (int)
#   end_port - ostatni port do skanowania (int)
# ZWRACA: brak (wyświetla wyniki bezpośrednio)
# ============================================================
def port_scan(target_host, start_port, end_port):
    # Zamień nazwę hosta na adres IP
    target_ip = socket.gethostbyname(target_host)
    print(f"Starting scan on host: {target_ip}")

    results = []  # Lista do przechowywania wyników
    
    # Utwórz pulę wątków (max 400 jednoczesnych połączeń)
    with concurrent.futures.ThreadPoolExecutor(max_workers=400) as executor:
        # Utwórz słownik zadań: każdy port to osobne zadanie w wątku
        futures = {executor.submit(scan_port, target_ip, port): port 
                   for port in range(start_port, end_port + 1)}
        
        total_ports = end_port - start_port + 1  # Całkowita liczba portów do skanowania
        
        # Przetwarzaj wyniki w miarę ich pojawiania się
        for i, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            port, service, banner, status = future.result()  # Pobierz wynik z wątku
            results.append((port, service, banner, status))  # Dodaj do listy wyników
            
            # Wyświetl pasek postępu
            sys.stdout.write(f"\rProgress: {i}/{total_ports} ports scanned")
            sys.stdout.flush()

    sys.stdout.write("\n")  # Nowa linia po pasku postępu
    print(format_port_result(results))  # Wyświetl sformatowane wyniki

# ============================================================
# SEKCJA GŁÓWNA (entry point)
# CEL: Pobranie danych od użytkownika i uruchomienie skanowania
# ============================================================
if __name__ == '__main__':
    # Pobierz dane od użytkownika
    target_host = input("Enter your target ip: ")
    start_port = int(input("Enter the start port: "))
    end_port = int(input("Enter end port: ")) 

    # Uruchom skanowanie
    port_scan(target_host, start_port, end_port)
