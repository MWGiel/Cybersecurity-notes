import dns.resolver
from tqdm import tqdm

print('Welcome in DNS finder,')
target_domain = input("Enter domain: ")
records_type = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SOA']

RESOLVATOR3000X = dns.resolver.Resolver()

print(f'\nChecking domains for: {target_domain}')

for record_type in tqdm(records_type, desc=f'\nProgress:', unit='typ'):
    try:                                   
        answer = RESOLVATOR3000X.resolve(target_domain, record_type)    
        
        print(f'{record_type} for {target_domain}') 
        for data in answer:                
            print(f' {data}')              
    except:                                
        print(f' {record_type}: no records found :(')

