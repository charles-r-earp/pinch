from bitarray import bitarray

def main():
    precision = 4
    msb_mask = (1 << (precision - 1)) - 1
    mask_bit_zero = 1 << (precision - 1)
    print('2 : {}'.format(bin(2)))
    print('msb_mask: {} mask_bit_zero: {}'.format(bin(msb_mask), bin(mask_bit_zero)))
    bits = bitarray()
    f = lambda x: x + 2
    x = 0
    y = 0
    for _ in range(10):
        x = f(x)
        y = f(y)
        print('x= {} : {}'.format(x, bin(x)))
        while len(bin(y)[2:]) > precision:
            bits += (bin(y)[2:])[0]
            y &= msb_mask
            y <<= 1
            print('y= {} : {}'.format(y, bin(y)))
        print('y= {} : {}'.format(y, bin(y)))
    bits += bin(y)[2:]
    print(bin(x))
    print(bits)
    
if __name__ == '__main__':
    main()