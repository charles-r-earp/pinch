import numpy as np

def cdf(s, f):
    return np.sum(f[:s])

def encode(s, f, x=0):
    m = np.sum(f)
    x = m*(x//f[s]) + cdf(s, f) + (x % f[s])
    print('y={} x = {}'.format(cdf(s, f), x))
    return x

def symbol(y, f):
    print('symbol: y={} f={}'.format(y, f))
    for s in range(f.size):
        if cdf(s, f) <= y and y < cdf(s+1, f):
            return s
    return s
    #raise IndexError('y: {} s: {} cf: {} f: {}'.format(y, s, cdf(s+1, f), f))

def decode(x, f):
    print('decode: x={} f={}'.format(x, f))
    m = np.sum(f)
    s = symbol(x % m, f)
    x = f[s]*(x//m) + (x % m) - cdf(s, f)
    print('x = {}'.format(x))
    return s, x


def main():
    seq1 = [0, 1, 1, 1, 1]
    f = np.array([1, 2, 3])
    x1 = 1
    print('encode: x = {}'.format(x1))
    for s in seq1:
        x1 = encode(s, f, x1)
    x2 = int(x1)
    seq2 = []
    print('decode: x = {}'.format(x2))
    while x2 % np.sum(f) != x2:
        s, x2 = decode(x2, f)
        seq2 += [s]
    print('{} => {} => {}'.format(seq1, x1, seq2))
    if seq1 == seq2[::-1]:
        print('success')
    else:
        print('fail')
    
if __name__ == '__main__':
    main()
        