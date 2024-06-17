import random
num = random.randint(1, 10**6)
num_str = '{:06}'.format(num)
num_str = str(num).zfill(6)
print(num_str)