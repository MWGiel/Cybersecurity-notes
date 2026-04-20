import threading
import time

def print_letters():
    for letter in 'ABCDE':
        print(f"number: {letter}")
        time.sleep(1)

def print_number():
    for i in range(1, 6):
        print(f"number: {i}")
        time.sleep(1)

thread1 = threading.Thread(target=print_number)
thread2 = threading.Thread(target=print_letters)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
