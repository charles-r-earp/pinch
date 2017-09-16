class Model(object):
    
    def __init__(self):
        self.ints = {}
        self.nets = {}
        self.build()
    
    def name():
        # str used for filename
        return NotImplemented
    
    def train(self, b):
        # sets accuracy
        return NotImplemented
    
    def run(self, argv):
        assert(len(argv) == 3)
        mode = argv[1]
        if(mode == 'train'):
            fname = argv[2]
            with open(fname, 'rb') as f:
                b = f.read()
                i = 1
                from bitarray import bitarray
                bits = bitarray()
                bits.frombytes(b)
                for bit in bits:
                    self.train(bit)
                    info = 'accuracy: {:.2f}% loss: {:.5f} iterations: {}'.format(100*self.accuracy, self.loss, i)
                    print(info, end='\r', flush=True)
                    i += 1
        elif(mode == 'predict'):
            fname = argv[2]
            with open(fname, 'rb') as f:
                b = f.read()
                i = 1
                from bitarray import bitarray
                bits = bitarray()
                bits.frombytes(b)
                for bit in bits:
                    self.predict(bit)
                    info = 'iterations: {}'.format(i)
                    print(info, end='\r', flush=True)
                    i += 1
        elif(mode == 'save'):
            folder = argv[2]
            import os
            if folder == '.':
                path = self.name()+'.netdef'
            else:
                path = os.path.join(folder, self.name()+'.netdef')
            with open(path, 'wb') as f:
                b = bytes()
                b += '#include <string>\n\n'.encode()
                b += ('namespace pinch {\n  namespace model {\n    namespace '+self.name()+'_netdef {\n').encode()
                for name, val in self.ints.items():
                    b += ('      const int {} = {};\n'.format(name, val)).encode()
                for name, net in self.nets.items():
                    b += ('      const std::string '+name+' = { ').encode()
                    proto_bytes = net.Proto().SerializeToString()
                    for byte in proto_bytes[:-1]:
                        b += ('char({}), '.format(byte)).encode()
                    b += ('char ({})'.format(proto_bytes[-1])).encode()
                    b += '};\n'.encode()
                b += '    };\n  };\n};'.encode()
                f.write(b)
    