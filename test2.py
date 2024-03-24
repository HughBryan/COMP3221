import time
import socket
import sys
import threading

def func1(array):
    time.sleep(2)
    array.remove(6)

def func2(array):
    for num in array:
        print(num)
        time.sleep(1)

array = [1,2,3,4,5,6]

t1 = threading.Thread(target=func1, args=(array,))
t2 = threading.Thread(target=func2, args=(array,))
t1.start()
t2.start()
t1.join()
t2.join()
print(array)