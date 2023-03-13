import requests
# find the prime numbers

for i in range(2, 10):
    for n in range(2, i):
        if(i % n ==0):
            print(i, 'equals', n, '*', i//n)
            break
        else:
            print(i, 'can\'t be divided by', n)
    else:
        print(i, 'is a prime number')

# request

response = request.get('43.136.134.205:8080/all')

