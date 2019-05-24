import psutil


for i in range(0, 10000000):
	print(psutil.cpu_percent())
	print('memory % used:', psutil.virtual_memory()[2])


print(psutil.cpu_percent())
print(psutil.virtual_memory())  # physical memory usage
print('memory % used:', psutil.virtual_memory()[2])