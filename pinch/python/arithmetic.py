
from bitarray import bitarray, bits2bytes

class BinaryCoder(object):
    
    def __init__(self, precision=16):
        self.precision = precision
        self.reset()
    
    def reset(self):
        self.low = 0
        self.max = (1 << self.precision) - 1
        self.msb_mask = 1 << (self.precision - 1)
        self.p = 0.5
        self.high = self.max
        
    def encode(self, bits_in):
        bits_out = bitarray()
        for bit_in in bits_in:
            bits_out += self.update(bit_in)
            while (self.low & self.msb_mask) == (self.high & self.msb_mask):
                bits_out += [self.high & self.msb_mask]
                self.high <<= 1
                self.high |= 1
                self.low <<= 1
        return bits_out
    
    def decode(self, bits_in):
        bits_out = bitarray()
        for bit_in in bits_in:
            bits_out += self.update(bit_in)
            while (self.low & self.msb_mask) == (self.high & self.msb_mask):
                bits_out += [self.high & self.msb_mask]
                self.high <<= 1
                self.high |= 1
                self.low <<= 1
        return bits_out
            
    def update(self, bit):
        r = self.high - self.low
        mid = int(self.p * r)
        if bit:
            self.low = mid + 1
        else:
            self.high = mid     
            
def main():
    bits_in = bitarray('011')
    coder = BinaryCoder()
    cipher_bits = coder.encode(bits_in)
    bits_out = coder.decode(cipher_bits)
    
if __name__ == '__main__':
    main()
    