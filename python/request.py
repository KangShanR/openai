import requests
# find the prime numbers

for i in range(2, 10):
    for n in range(2, i):
        if(i % n ==0):
            print(i, 'equals', n, '*', i//n)
            break
        else:
            print(n)
    else:
        print(i, 'is a prime number')

