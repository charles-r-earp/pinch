import numpy as np
import io
from utitlity import OrderedSet, Graph
            
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
    
    EOF = -1
    
    def reset(self):
        self.bits = bitarray()
    
    def encode(self, code, p):
        # p is np vector
        self.bits += bitarray.frombytes(chr(code).encode())
        return NotImplemented
    
    def fetch(end=False):
        # gets and removes bytes from the buffer
        # if end then finishes the coding op
        if end:
            return self.bits.tobtyes()
        else:
            nbytes = self.bits.length() // 8
            bits = self.bits[:nbytes]
            self.bits = self.bits[nbytes:]
            return bits.tobytes()
    
    def decode(self, cipher, p):
        ch = None
        for ch in cipher:
            break
        if ch is not None:
            code = ord(ch)
        else:
            code = Coder.EOF
        # returns code, ie index of string in p
        return code
        
class Compressor(CoreObject):
    
    def compress(plain, model, coder, cipher=io.BytesIO()):
        model.reset()
        coder.reset()
        for ch in plain:
            p = model.predict()
            code = model.vocab.index(ch)
            coder.encode(code, p)
            model.feed(ch)
            cipher.write(coder.fetch())
        cipher.write(coder.fetch(end=True))
        return cipher
        
    def decompress(cipher, model, coder, plain=io.BytesIO()):
        model.reset()
        coder.reset()
        code = 0
        while code != Coder.EOF
            p = model.predict()
            code = coder.decode(cipher, p)
            if code != Coder.EOF:
                ch = model.vocab[code]
                plain.write(ch.encode())
                model.feed(ch)
        return plain
        
    def test(plain, model, coder, cipher=io.BytesIO()):
        print(self)
        pos = plain.tell()
        self.compress(plain, model, coder, cipher)
        plain.seek(pos)
        plain2 = self.decompress(cipher, model, coder)
        plain2.seek(0)
        success = plain.read() == plain2.read()
        plain.seek(pos)
        cipher.seek(0)
        print('success')
        return success
    
def main():
