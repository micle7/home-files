import base64, requests, struct, sys

def check_dns(doh_url, domain):
    # Исправляем URL сервера
    if not doh_url.startswith('http'): 
        doh_url = f'https://{doh_url}'
    if '/dns-query' not in doh_url and 'dns.google' not in doh_url:
        doh_url = doh_url.rstrip('/') + '/dns-query'

    # Сборка DNS пакета
    query = struct.pack('!HHHHHH', 0, 0x0100, 1, 0, 0, 0)
    for part in domain.split('.'):
        query += struct.pack('!B', len(part)) + part.encode()
    query += struct.pack('!BHH', 0, 1, 1)
    
    dns_b64 = base64.urlsafe_b64encode(query).decode().rstrip('=')
    
    try:
        r = requests.get(f"{doh_url}?dns={dns_b64}", 
                         headers={'Accept': 'application/dns-message', 'User-Agent': 'Mozilla/5.0'},
                         timeout=5)
        
        if r.status_code == 200:
            # Вытаскиваем IP из последних 4 байт ответа
            ip = ".".join(map(str, r.content[-4:]))
            print(f"[{doh_url}] {domain} -> {ip}")
        else:
            print(f"Ошибка {doh_url}: HTTP {r.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python3 dnstest.py <адрес_doh> <сайт>")
        print("Пример: python3 dnstest.py kot.homes ntc.party")
    else:
        check_dns(sys.argv[1], sys.argv[2])
