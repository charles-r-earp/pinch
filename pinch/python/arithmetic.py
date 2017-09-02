from core import Coder
from bitarray import bitarray
import numpy as np

class ArithmeticCoder(Coder):
    
    def __init__(self, precision=16):
        self.precision = precision
    
    def reset(self):
        Coder.reset(self)
        self._low = 0
        self._cprob = 0
        self._max = (2 << self.precision) - 1
        self._max_prob = (2 << (self.precision - 2)) - 1
        self._high = self._max
        self._underflow_bits = 0
        self._code = -1
        self._nbits = 0
        def mask_bit(x):
            return (1 << (self.precision - (1 + x)))
        self.mask_bit_zero = mask_bit(0)
        self.mask_bit_one = mask_bit(1)
        self.msb_mask = ((1 << (self.precision - 1)) - 1)
    
    def encode(self, code, p):
        count = self.feed(p)
        c = count[code]
        low = np.sum(count[count <= c])
        high = low + c
        cprob = np.sum(count) + 1
        self.update(low, high, cprob)
        msb_mask = ((1 << (self.precision - 1)) - 1)
        bits = bitarray()
        while True:
            if (self._high ^ ~self._low) & self.mask_bit_zero:
                # MSBs match, write them to output file
                bits += [self._high & self.mask_bit_zero != 0]
                # we can write out underflow bits too
                while self._underflow_bits > 0:
                    bits += [self._high & self.mask_bit_zero == 0]
                    self._underflow_bits -= 1
            elif (~self._high & self._low) & self.mask_bit_one:
                #*******************************************************
                # Possible underflow condition: neither MSBs nor second
                # MSBs match.  It must be the case that lower and upper
                # have MSBs of 01 and 10.  Remove 2nd MSB from lower and
                # upper.
                #*******************************************************
                self._underflow_bits += 1
                self._low &= ~(self.mask_bit_zero | self.mask_bit_one)
                self._high |= self.mask_bit_one
                #*******************************************************
                # The shifts below make the rest of the bit removal
                # work.  If you don't believe me try it yourself.
                #*******************************************************
            else:
                break              # nothing left to do
            #***********************************************************
            # Mask off old MSB and shift in new LSB.  Remember that
            # lower has all 0s beyond it's end and upper has all 1s
            # beyond it's end.
            #***********************************************************
            self._low &= self.msb_mask
            self._low <<= 1
            self._high &= self.msb_mask
            self._high <<= 1
            self._high |= 0x0001
        self._nbits += bits.length()
        self.bits += bits

    def decode(self, cipher, p):
        if self.bits.length() < self.precision:
            return Coder.EOF
        self.bits.fromfile(cipher)
        print(self.bits)
        self.bits.reverse()
        if self._code == -1:
            self._code = 0
            for _ in range(self.precision):
                if self.bits.length() > 0:
                    bit = self.bits.pop()
                else:
                    bit = 0
                self._code <<= 1
                self._code |= bit
        print(self.bits)
        print(self._code)
        r = self._high - self._low + 1
        count = self.feed(p)
        cprob = np.sum(count) + 1
        c = ((self._code - self._low + 1) * cprob - 1)//r
        sorted_count = np.sort(count)
        print(sorted_count)
        code = Coder.EOF
        high = 0
        for val in sorted_count:
            high += val
            if c < high:
                code = count.tolist().index(val)
                break
        if code == Coder.EOF:
            return code
        low = high - val
        print(c)
        self.update(low, high, cprob)
        while True:
            if (self._high ^ ~self._low) & self.mask_bit_zero:
                # MSBs match, allow them to be shifted out
                pass
            elif (~self._high & self._low) & self.mask_bit_one:
                #*******************************************************
                # Possible underflow condition: neither MSBs nor second
                # MSBs match.  It must be the case that lower and upper
                # have MSBs of 01 and 10.  Remove 2nd MSB from lower and
                # upper.
                #*******************************************************
                self._low &= ~(self.mask_bit_zero | self.mask_bit_one)
                self._high |= self.mask_bit_one
                self._code ^= self.mask_bit_one
                # the shifts below make the rest of the bit removal work
            else:
                # nothing to shift out
                break
            #***********************************************************
            # Mask off old MSB and shift in new LSB.  Remember that
            # lower has all 0s beyond it's end and upper has all 1s
            # beyond it's end.
            #***********************************************************
            self._low &= self.msb_mask
            self._low <<= 1
            self._high &= self.msb_mask
            self._high <<= 1
            self._high |= 1
            self._code &= self.msb_mask
            self._code <<= 1
            if self.bits.length() > 0:
                bit = self.bits.pop()
                self._code |= bit
        print('Code: {}'.format(code))
        return code
    
    def fetch(self, end=False):
        # gets and removes bytes from the buffer
        # if end then finishes the coding op
        if end:
            bits = bitarray()
            bits += [self._low & self.mask_bit_one]
            # write out any unwritten underflow bits
            self._underflow_bits += 1
            for i in range(self._underflow_bits):
                bits += [not (self._low & self.mask_bit_one)]
            self.bits += bits
        return Coder.fetch(self, end)
    
    def feed(self, p):
        count = (p * self._max).astype(np.int32) + 1
        # add EOF
        total = np.sum(count) + 1
        if total > self._max_prob:
            val = total // self._max_prob + 1
            count[count > val]  //= val
            count[count <= val] = 1
        return count
        indices = np.argsort(count)
        code_map = np.argsort(indices)
        np.sort(count)
        low_high = np.zeros([count.size], dtype=np.int32)
        cprob = 0
        u = 0
        for c in count:
            cprob += c
            low_high[u] = cprob
            u += 1
        print(low_high)
        exit()
        return low_high, code_map, EOF_index
        
    def update(self, low, high, cprob):
        r = self._high - self._low + 1
        self._high = self._low + r * high // cprob - 1
        self._low += r * low // cprob
        
def main():
    from core import Model, Compressor
    with open('texts/dickens-selection', 'rb') as f:
        Compressor().test(f, Model(), ArithmeticCoder())
    
if __name__ == '__main__':
    main()