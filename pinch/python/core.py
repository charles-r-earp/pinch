import numpy as np
import io
from bitarray import bitarray
from utility import OrderedSet, Graph
            
class CoreObject(object):
    
    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

class Model(CoreObject):
    
    characters = OrderedSet(chr(u) for u in range(256))
    
    def __init__(self, word_length=1):
        # how long vocab words will be
        # -1 means no limit
        self.word_length = word_length
    
    def reset(self):
        self.vocab = OrderedSet(Model.characters)
        self.loss = None
    
    def feed(self, word):
        return NotImplemented
    
    def add(self, word):
        # add new words to vocab
        assert len(word) <= self.word_length
        assert word not in self.vocab
        self.vocab.add(word)
        
    def predict(self, context=''):
        return np.ones([len(self.vocab)]) / len(self.vocab)
        
    def generate(self, context='', n=1):
        s = str(context)
        count = 0
        while count < n:
            p = self.predict(s)
            i = np.argmax(p)
            word = self.vocab[i]
            count += len(word)
            s += word
        return s
    
def ContextModel(Model):
    
    def __init__(self, word_length=1, context_length=1):
        Model.__init__(self, word_length)
        # how long the context can be
        # -1 means no limit
        self.context_length = context_length
        
    def reset(self):
        Model.reset(self)
        self.context = ' '
        
    def feed(self, word):
        self.context += word
        self.train(self.context)
    
    def train(self, context=''):
        return NotImplemented
    

class Coder(CoreObject):
    
    EOF = 1
    byteorder = 'little'
    
    def reset(self):
        self.bits = bitarray(endian=Coder.byteorder)
    
    def encode(self, code, p):
        # p is np vector
        b = code.to_bytes(1, Coder.byteorder)
        self.bits.frombytes(b)
    
    def fetch(self, end=False):
        # gets and removes bytes from the buffer
        # if end then finishes the coding op
        if end:
            return self.bits.tobytes()
        else:
            nbytes = self.bits.length() // 8
            nbits = nbytes * 8
            bits = self.bits[:nbits]
            self.bits = self.bits[nbits:]
            return bits.tobytes()
    
    def decode(self, cipher, p):
        b = cipher.read(1)
        if len(b) > 0:
            code = int.from_bytes(b, Coder.byteorder)
        else:
            code = Coder.EOF
        # returns code, ie index of string in p
        return code
        
class Compressor(CoreObject):
    
    def reset(self):
        pass
    
    def encode(self, byte, model):
        return to_write
    
    def decode(self,  model)
    
    def compress(self, plain, model, coder, cipher=io.BytesIO()):
        print(cipher)
        pos = plain.tell()
        cpos = cipher.tell()
        plain.seek(-1, 2)
        length = plain.tell() - pos
        plain.seek(pos)
        model.reset()
        coder.reset()
        b = plain.read(1)
        while len(b) > 0:
            ch = chr(int.from_bytes(b, Coder.byteorder))
            #ch = b.decode()
            p = model.predict()
            code = model.vocab.index(ch)
            coder.encode(code, p)
            model.feed(ch)
            bs = coder.fetch()
            cipher.write(bs)
            b = plain.read(1)
            print('compress {}/{}'.format(plain.tell()-pos, length), end='\r', flush=True)
        coder.encode(Coder.EOF, p)
        cipher.write(coder.fetch(end=True))
        cipher.seek(-1, 2)
        clength = cipher.tell() - cpos
        cipher.seek(cpos)
        print('compress done. {}B'.format(clength))
        return cipher
        
    def decompress(self, cipher, model, coder, plain=io.BytesIO()):
        print(cipher)
        pos = plain.tell()
        cpos = cipher.tell()
        cipher.seek(-1, 2)
        clength = cipher.tell() - cpos
        cipher.seek(cpos)
        model.reset()
        coder.reset()
        code = 0
        while code != Coder.EOF:
            p = model.predict()
            code = coder.decode(cipher, p)
            if code != Coder.EOF:
                ch = model.vocab[code]
                plain.write(ch.encode())
                model.feed(ch)
            print('decompress {}/{}'.format(cipher.tell()-cpos, clength), end='\r', flush=True)
        cipher.seek(cpos)
        length = plain.tell() - pos
        cipher.seek(pos)
        print('decompress done. {}B'.format(plain.tell()-pos, length), end='\r', flush=True)
        return plain
        
    def test(self, plain, model, coder, cipher=io.BytesIO()):
        print('{}: model={} coder={}'.format(self, model, coder))
        cpos = cipher.tell()
        pos = plain.tell()
        #print(plain.read())
        plain.seek(pos)
        self.compress(plain, model, coder, cipher)
        plain.seek(pos)
        cipher.seek(cpos)
        #print(cipher.read())
        cipher.seek(cpos)
        plain2 = self.decompress(cipher, model, coder)
        plain2.seek(pos)
        if plain.read() == plain2.read():
            print('success')
            success = True
        else:
            print('fail')
            print('[...] '+plain2.read()[-100])
            success = False
        plain.seek(pos)
        cipher.seek(cpos)
        plain2.seek(pos)
        return success
    
def main():
    with open('texts/dickens-selection', 'rb') as f:
        Compressor().test(f, Model(), Coder())
    
if __name__ == '__main__':
    main()