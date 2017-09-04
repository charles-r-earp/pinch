from fractions import Fraction
from bitarray import bitarray, bits2bytes

def encode(seq, p):
    low = Fraction()
    high = Fraction(1)
    bits = bitarray()
    for code in seq:
        low, high = encode_step(code, p, low, high)
    x = low
    print('x: {}'.format(x))
    bits += to_bits(x)
    print(bits)
    return bits
    
def encode_step(code, p, low, high):
    r = high - low 
    low += r*sum(p[:code])
    high = low + r*p[code]
    return low, high

def decode(bits, p, length, precision=16):
    x = from_bits(bits, precision)
    bits = bits[precision:]
    low = Fraction()
    high = Fraction(1)
    seq = []
    for _ in range(length):
        code, x, low, high = decode_step(x, p, low, high)
        seq += [code]
    return seq

def decode_step(x, p, low, high):
    r = high - low
    cp = Fraction()
    for code in range(len(p)):
        if x >= low + cp and x < low + cp + r*p[code]:
            break
        cp += r*p[code]
    low += r*sum(p[:code])
    high = low + r*p[code]
    return code, x, low, high

def to_bits(f, n=16):
    f_out = f
    bits = bitarray()
    while f_out != 0:
        if f_out.denominator // 2 > 0 and f_out.denominator % 2 == 0:
            f_out = Fraction(f_out.numerator, f_out.denominator // 2)
        else:
            f_out = Fraction(f_out.numerator * 2, f_out.denominator)
        bits += [f_out.numerator // f_out.denominator]
        f_out -= int(f_out)
    
    #assert from_bits(bits) > f, '{} > {}'.format(float(from_bits(bits)), float(f))
    return bits

def from_bits(bits, precision=16):
    k = 2
    f = Fraction(0)
    for bit in bits:
        f += Fraction(bit,k)
        k *= 2
    return f

def main():
    seq = [0, 1, 1, 2] 
    p = [Fraction(1, 4), Fraction(2, 4), Fraction(1, 4)]
    bits = encode(seq, p)
    seq_out = decode(bits, p, len(seq))
    print('{} : {} => {} => {}'.format(seq, p, bits, seq_out))
    assert seq == seq_out
    print('compressed {} bytes to {} bytes'.format(len(seq), bits2bytes(bits.length())))
    
if __name__ == '__main__':
    #bits = to_bits(Fraction(1, 10), 10)
    #print(bits)
    main()