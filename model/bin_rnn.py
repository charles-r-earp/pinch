from model import Model
from caffe2.python import core, workspace, model_helper, brew, rnn_cell
from caffe2.python.optimizer import build_sgd
import numpy as np
from bitarray import bitarray

class BinRNN(Model):
    
    def name(self):
        return 'bin_rnn'
    
    def build(self):
        # flag for lazy creation of nets
        self.started = False
        nfeatures = 2
        self.nfeatures = nfeatures
        nbatches = 256
        self.nbatches = nbatches
        # length of unrolled nets
        trainT = 32
        self.trainT = trainT
        predT = 1
        # train net
        helper = model_helper.ModelHelper('bin_rnn')
        ns = 'train_'
        helper.net.AddExternalInputs(ns+'hidden_init', ns+'cell_init', ns+'data', ns+'target', ns+'seq_lengths')
        hidden_output_all, hidden_output_last, cell_state_all, cell_state_last = rnn_cell.LSTM(
            helper, 
            ns+'data', 
            ns+'seq_lengths', 
            (ns+'hidden_init', ns+'cell_init'),
            2, 
            nfeatures,
            scope=ns+'LSTM',
            forget_bias=40.0
        )
        brew.fc(helper, hidden_output_all, ns+'fc', nfeatures, 2, axis=2)
        brew.softmax(helper, ns+'fc', ns+'softmax', axis=2)
        helper.net.Reshape(ns+'softmax', [ns+'softmax_reshaped', ns+'softmax_shape'], shape=[-1, 2])
        helper.net.Accuracy([ns+'softmax_reshaped', ns+'target'], ns+'accuracy')
        helper.LabelCrossEntropy([ns+'softmax_reshaped', ns+'target'], ns+'xent')
        helper.net.AveragedLoss(ns+'xent', ns+'loss')
        helper.AddGradientOperators([ns+'loss'])
        build_sgd(
            helper,
            base_learning_rate=2.5,
            policy="step",
            stepsize=1,
            gamma=0.9999
        )
        init_net = helper.param_init_net
        train_net = helper.net
        workspace.RunNetOnce(init_net)
        for blob in workspace.Blobs():
            if blob not in ['iteration_mutex']:
                init_net.Const(workspace.FetchBlob(blob), blob)
        self.init_net = init_net
        self.train_net = train_net
        return {'init_net':init_net, 'train_net':train_net}
    
    def train(self, b):
        ns = 'train_'
        if not self.started:
            bits = bitarray()
            bits.frombytes(b)
            bits = bits[:self.trainT*self.nbatches+1]
            seq_lengths = np.array([self.trainT]*self.nbatches, dtype=np.int32)
            workspace.FeedBlob(ns+'seq_lengths', seq_lengths)
            data = np.zeros([self.trainT, self.nbatches, 2], dtype=np.float32)
            i = 0
            for batch in range(self.nbatches):
                for t in range(self.trainT):
                    if i > bits.length():
                        break
                    data[t, batch, bits[i]] = 1
                    i += 1
            workspace.FeedBlob(ns+'data', data)
            target = np.array(bits[1:], dtype=np.int32)
            workspace.FeedBlob(ns+'target', target)
        state = np.zeros([1, self.nbatches, self.nfeatures], dtype=np.float32)
        workspace.FeedBlob(ns+'hidden_init', state)
        workspace.FeedBlob(ns+'cell_init', state)
        if not self.started:
            workspace.RunNetOnce(self.init_net)
            workspace.CreateNet(self.train_net)
        workspace.RunNet(self.train_net)
        self.accuracy = float(workspace.FetchBlob(ns+'accuracy'))
        self.loss = float(workspace.FetchBlob(ns+'loss'))
        self.started = True
    
    
    
if __name__ == '__main__':
    import sys
    BinRNN().run(sys.argv)