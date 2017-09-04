import numpy as np
from bitarray import bitarray
 
def encode(seq, f, k=1, b=4):
    f = np.copy(f)
    m = np.sum(f)
    L = k*m
    bits = bitarray()
    x = L
    y = L
    for s in seq:
        print([x,y])
        assert L <= x and x < b*L, 'L: {} b: {} x: {}'.format(L, b, x)
        x_max = (b * (L // m)) * f[s]
        while x >= x_max:
            r = x % b
            for bit in bitarray(bin(r)[2:]):
                print('bit: {}'.format(int(bit)))
                bits += [bit]
            x //= b
        #print('x: {}'.format(x))
        x = encode_step(x, s, f)
        y = encode_step(y, s, f)
        
        #print('=> {}'.format(x))
    print([x,y])
    print(bits)
    return bits

def decode(bits, f, k=1, b=2):
    f = np.copy(f)
    m = np.sum(f)
    L = k * m
    bits = bitarray(bits)
    print([bits, bitarray(bin(55)[2:])])
    seq = []
    x = L
    y = 25
    done = False
    while not done:
        print([x,y])
        #assert L <= x and x < b*L
        s, x = decode_step(x, f)
        s, y = decode_step(y, f)
        
        seq += [s]
        if len(seq) == 5:
            break
        while x < L:
            if bits.length() > 0:
                bit = bits.pop()
                xin = x
                x = 2 * x + bit
                print('bit: {} x: {} -> {}'.format(int(bit), xin, x))
            else:
                #done = True
                break
    print([x,y])
    return seq[::-1]

def cdf(s, f):
    return np.sum(f[:s])

def encode_step(x, s, f):
    m = np.sum(f)
    x = m*(x//f[s]) + cdf(s, f) + (x % f[s])
    #print('y={} x = {}'.format(cdf(s, f), x))
    return int(x)

def symbol(y, f):
    #print('symbol: y={} f={}'.format(y, f))
    for s in range(f.size):
        if cdf(s, f) <= y and y < cdf(s+1, f):
            return s
    return s

def decode_step(x, f):
    #print('decode: x={} f={}'.format(x, f))
    m = np.sum(f)
    s = symbol(x % m, f)
    x = f[s]*(x//m) + (x % m) - cdf(s, f)
    #print('x = {}'.format(x))
    return s, int(x)

def count(seq, precision=16):
    f = np.zeros([1], dtype=np.int32)
    for s in seq:
        if s > f.size:
            f.resize([s+1])
        f[s] += 1
    m = (2 << precision) - 1
    f *= m // np.sum(f)
    assert np.log2(np.sum(f)).astype(np.int32) % 2 == 0
    return f

def main():
    #text = 'Hello World!'
    #seq = [ord(c) for c in text]
    #f = count(seq)
    seq = [1, 1, 1, 1, 1]
    f = np.array([1, 3], dtype=np.int32)
    bits = encode(seq, f)
    nbytes = bits.length() // 8 + 1
    seq_out = decode(bits, f)
    #text_out = ''.join(chr(s) for s in seq_out)
    print('{} {} => {} => {}'.format(seq, f, bits, seq_out))
    assert seq == seq_out
    print('compressed {} bytes to {} bytes => {:.1f}%'.format(len(seq), nbytes, 100 * nbytes/len(seq)))
    
if __name__ == '__main__':
    main()
        