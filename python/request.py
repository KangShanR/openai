import requests
# find the prime numbers

def prime(p):
    """Print the prime numbers from 2 2 the argument number"""
    for i in range(2, p):
        for n in range(2, i):
            if(i % n ==0):
                print(i, 'equals', n, '*', i//n)
                break
            else:
                print(i, 'can\'t be divided by', n)
        else:
            print(i, 'is a prime number')

prime(100)

# request

# response = request.get('43.136.134.205:8080/all')


