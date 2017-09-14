class Model(object):
    
    def name():
        # str used for filename
        return NotImplemented
    
    def build(self):
        # returns dict of net_name:net
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
                self.build()
                while True:
                    self.train(b)
                    info = 'accuracy: {:.2f}% loss: {:.5f} iterations: {}'.format(100*self.accuracy, self.loss, i)
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
                b += ('namespace pinch {\n   namespace model {\n    namespace '+self.name()+'_netdef {\n').encode()
                nets = self.build()
                for name, net in nets.items():
                    b += ('    const std::string '+name+' = "').encode()
                    b += net.Proto().SerializeToString()+'";\n'.encode()
                b += '    };\n  };\n};'.encode()
                f.write(b)
    