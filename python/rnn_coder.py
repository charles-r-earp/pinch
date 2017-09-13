from caffe2.python import core, workspace, model_helper, brew, rnn_cell
from caffe2.python.optimizer import build_sgd
import numpy as np

class RNN:
    
    def __init__(self, nfeatures=2, nbits=16):
        helper = model_helper.ModelHelper('rnn')
        self.hidden = np.zeros([1, 1, nfeatures], dtype=np.float32)
        self.cell = np.zeros([1, 1, nfeatures], dtype=np.float32)
        hidden_output_all, hidden_output_last, cell_state_all, cell_state_last = rnn_cell.LSTM(
            helper, 
            'data', 
            'seq_lengths', 
            ('hidden_init', 'cell_init'),
            2, 
            nfeatures, 
            scope="LSTM", 
            forget_bias=1.0,
        )
        helper.Copy(hidden_output_all, 'hidden_output_all')
        brew.fc(helper, hidden_output_all, 'fc', 2, 2, axis=2)
        helper.net.Reshape('fc', ['fc_reshaped', 'fc_shape'], shape=[-1, 2])
        brew.softmax(helper, 'fc_reshaped', 'softmax')
        self.pred_net = core.Net(helper.net.Proto())
        helper.LabelCrossEntropy(['softmax', 'target'], 'xent')
        helper.net.AveragedLoss('xent', 'loss')
        helper.AddGradientOperators(['loss'])
        build_sgd(
            helper,
            base_learning_rate=0.5 * nfeatures,
            policy="step",
            stepsize=1,
            gamma=0.9999
        )      
        self.init_net = helper.param_init_net
        workspace.RunNetOnce(self.init_net)
        self.train_net = helper.net
        self.prepare()
        workspace.CreateNet(self.pred_net)
        workspace.CreateNet(self.train_net)
        
    def prepare(self, bits=[]):
        bits = [0] + bits
        seq_length = len(bits)
        seq_lengths = np.array([seq_length], dtype=np.int32)
        workspace.FeedBlob('seq_lengths', seq_lengths)
        data = np.zeros([seq_length, 1, 2], dtype=np.float32)
        u = 1
        for bit in bits[:-1]:
            data[u, 0, bit] = 1
            u += 1
        workspace.FeedBlob('data', data)
        target = np.array(bits, dtype=np.int32)
        workspace.FeedBlob('target', target)
        workspace.FeedBlob('hidden_init', self.hidden)
        workspace.FeedBlob('cell_init', self.cell)

    def train(self, bits):
        self.prepare(bits)
        workspace.RunNet(self.train_net)
        loss = float(workspace.FetchBlob('loss'))
        return loss
        
    def predict(self, bits):
        self.prepare(bits)
        workspace.RunNet(self.pred_net)
        softmax = workspace.FetchBlob('softmax')
        bit = np.argmax(softmax[-1])
        return bit
    
    def generate(self, n=1):
        bits = []
        for _ in range(n):
            bit = self.predict(bits)
            bits += [bit]
        return bits
        
def main ():
    bits = [0, 1, 1, 1]
    rnn = RNN()
    pbits = []
    def tostring(bits):
        return ''.join('1' if bit else '0' for bit in bits)
    while True:
        print(tostring(bits))
        while bits != pbits:
            loss = rnn.train(bits)
            pbits = rnn.generate(len(bits))
            info = tostring(pbits)+' loss: {:.8f}'.format(loss)
            print(info, end='\r', flush=True)
        print(info)
        bits += [int(np.random.binomial(1, 0.5))]
    
if __name__ == '__main__':
    main()