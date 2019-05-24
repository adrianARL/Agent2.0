import sys


try:
    iterations = int(sys.argv[1])
except:
    iterations = 10

for i in range(iterations):
    print(i+1)
