import hashlib
import itertools
import string
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

hash_name = [
    'md5',
    'sha1',
    'sha224',
    'sha256',
    'sha384',
    'sha3_224',
    'sha3_256',
    'sha3_384',
    'sha3_512',
    'sha512'
]

def generate_passwords(min_length, max_length, characaters):
    for length in range(min_length, max_length + 1):
        for pwd in itertools.product(characaters, repeat=length):
            yield ''.join(pwd)

def check_hash(hash_fn, password, target_hash):
    return hash_fn(password.encode()).hexidigest() == target_hash

def crack_hash(hash, wordlist=None, hash_type='md5', min_length=0, max_length=0, characaters=string.ascii_letters + string.digits, max_workres)
    hash_fn = getattr(hashlib, hash_type, None)
    if hash_fn is None or hash_type not in hash_name:
        raise ValueError(f'[!] Invalid hash type: {hash_type} supported are {hash_name}')

    if worlist:
        with open(wordlist, 'r') as f:
            lines = f.readlines()
            total_lines = len(lines)
            print(f"[*] Cracking hash {hash} using {hash_type} with a list of {total_lines} passwords.")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(check_hash, hash_fn, line.strip(), hash): line for line in lines}
                for future in tqdm(futures, total=total_lines, desc="Cracking hash")
                    if future.result()
                        return futures[future].strip()

    elif min_length > 0 and max_length > 0:
        total_combinations = sum(len(characaters) ** length for length in range(min_length, max_length + 1))
        print(f'[*] Cracking hash {hash} using {hash_type} with generated passwords of lengths from {min_length} to {max_length}. Total combinations: {total_combinations}.')

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            with tqdm(total=total_combinations, desc='Generating and cracking hash') as pbar:
                for pwd in generate_passwords(min_lengthm, max_length, characaters):
                    future = executor.submit(check_hash, hash_fn, pwd, hash)
                    futures.appped(future)
                    pbar.update(1)
                    if future.result():
                        return pwd

    return None
