
def generator(count):

    words = ['hello', 'brrother', 'eng', 'apple']

    iterator = zip(range(count), words)

    for w in iterator:
        yield  w


gen = generator(3)
for w in gen:
    print(f'iterator data {w}')
print('-------')
gen = generator(4)
for w in gen:
    print(f'iterator data {w}')
