from model import Model
from caffe2.python import core, workspace, model_helper, brew, rnn_cell
from caffe2.python.optimizer import build_sgd
import numpy as np
from bitarray import bitarray

class BinRNN(Model):
    
    def __init__(self):
        self.nfeatures = 2
        self.build_pred()
        self.nets = {'pred_init_net':self.pred_init_net, 'pred_net':self.pred_net}
        self.ints = {}
    
    def name(self):
        return 'bin_rnn'
    
    def build_pred(self):
        helper = model_helper.ModelHelper('bin_rnn_pred')
        helper.param_init_net.Const(np.zeros([1, 1, 2], dtype=np.float32), 'data')
        helper.param_init_net.Const(np.array([1], dtype=np.int32), 'timestep_0/seq_lengths')
        helper.param_init_net.Const(np.zeros([1, 1, self.nfeatures], dtype=np.float32), 'timestep_0/hidden_init')
        helper.param_init_net.Const(np.zeros([1, 1, self.nfeatures], dtype=np.float32), 'timestep_0/cell_init')
        hidden_output_all, hidden_output_last, cell_state_all, cell_state_last = rnn_cell.LSTM(
            helper, 
            'data', 
            'seq_lengths', 
            ('hidden_init', 'cell_init'),
            2, 
            self.nfeatures,
            scope='LSTM',
            static_rnn_unroll_size=1
        )
        brew.fc(helper, hidden_output_all, 'fc', self.nfeatures, 2, axis=2)
        brew.softmax(helper, 'fc', 'softmax', axis=2)
        helper.net.Copy('timestep_0/LSTM/hidden_t', 'timestep_0/hidden_init')
        helper.net.Copy('timestep_0/LSTM/cell_t', 'timestep_0/cell_init')
        workspace.RunNetOnce(helper.param_init_net)
        for blob in workspace.Blobs():
            if blob not in ['iteration_mutex']:
                helper.param_init_net.Const(workspace.FetchBlob(blob), blob)
        self.pred_init_net = helper.param_init_net
        self.pred_net = helper.net
    
    def build(self):
        # flag for lazy creation of nets
        self.started = False
        nfeatures = 2
        self.nfeatures = nfeatures
        nbatches = 8
        forget_bias = 40.0
        self.nbatches = nbatches
        # length of unrolled nets
        trainT = 32
        self.trainT = trainT
        predT = 1
        self.predT = predT
        # pred_net
        helper = model_helper.ModelHelper('bin_rnn_pred')
        helper.param_init_net.Const(np.zeros([1, 1, 2], dtype=np.float32), 'data')
        helper.param_init_net.Const(np.array([1], dtype=np.int32), 'timestep_0/seq_lengths')
        helper.param_init_net.Const(np.zeros([1, 1, nfeatures], dtype=np.float32), 'timestep_0/hidden_init')
        helper.param_init_net.Const(np.zeros([1, 1, nfeatures], dtype=np.float32), 'timestep_0/cell_init')
        helper.net.AddExternalInputs('hidden_init', 'cell_init', 'data', 'seq_lengths')
#        hidden_output_all, hidden_output_last, cell_state_all, cell_state_last = rnn_cell.LSTM(
#            helper, 
#            'data', 
#            'seq_lengths', 
#            ('hidden_init', 'cell_init'),
#            2, 
#            nfeatures,
#            scope='LSTM',
#            forget_bias=forget_bias,
#            static_rnn_unroll_size=predT
#        )
#        brew.fc(helper, hidden_output_all, 'fc', nfeatures, 2, axis=2)
        #brew.softmax(helper, 'fc', 'softmax', axis=2)
        pred_net = helper.net
        #pred_net.Copy('timestep_0/LSTM/hidden_t', 'timestep_0/LSTM/hidden_init')
        #pred_net.Copy('timestep_0/LSTM/cell_t', 'timestep_0/LSTM/cell_init')
        pred_init_net = helper.param_init_net
        self.pred_init_net = pred_init_net
        self.pred_net = pred_net
        workspace.RunNetOnce(pred_init_net)
        for blob in workspace.Blobs():
            if blob not in ['iteration_mutex']:
                pred_init_net.Const(workspace.FetchBlob(blob), blob)
        # train_net
        helper = model_helper.ModelHelper('bin_rnn_train')
        helper.net.AddExternalInputs('hidden_init', 'cell_init', 'data', 'seq_lengths', 'target')
        hidden_output_all, hidden_output_last, cell_state_all, cell_state_last = rnn_cell.LSTM(
            helper, 
            'data', 
            'seq_lengths', 
            ('hidden_init', 'cell_init'),
            2, 
            nfeatures,
            scope='LSTM',
            forget_bias=forget_bias,
            static_rnn_unroll_size=trainT
        )
        brew.fc(helper, hidden_output_all, 'fc', nfeatures, 2, axis=2)
        brew.softmax(helper, 'fc', 'softmax', axis=2)
        helper.net.Reshape('softmax', ['softmax_reshaped', 'softmax_shape'], shape=[-1, 2])
        helper.net.Accuracy(['softmax_reshaped', 'target'], 'accuracy')
        helper.LabelCrossEntropy(['softmax_reshaped', 'target'], 'xent')
        helper.net.AveragedLoss('xent', 'loss')
        helper.AddGradientOperators(['loss'])
        build_sgd(
            helper,
            base_learning_rate=2.5,
            policy="step",
            stepsize=1,
            gamma=0.9999
        )
        train_init_net = helper.param_init_net
        train_net = helper.net
        workspace.RunNetOnce(train_init_net)
        for blob in workspace.Blobs():
            if blob not in ['iteration_mutex']:
                train_init_net.Const(workspace.FetchBlob(blob), blob)
        self.train_init_net = train_init_net
        self.train_net = train_net
        
        self.ints = {'nfeatures':nfeatures, 'trainT':trainT, 'predT':predT}
        self.nets = {'pred_init_net':pred_init_net, 'pred_net':pred_net, 'train_init_net':train_init_net, 'train_net':train_net}
        
    def predict(self, bit):
        if not self.started:
            workspace.RunNetOnce(self.pred_init_net)
            workspace.CreateNet(self.pred_net)
            self.started = True
        data = np.zeros([1, 1, self.nfeatures], dtype=np.float32)
        data[bit] = 1
        workspace.FeedBlob('data', data)
        workspace.RunNet(self.pred_net)
    
    def train(self, b):
        if not self.started:
            bits = bitarray()
            bits.frombytes(b)
            bits = bits[:self.trainT*self.nbatches+1]
            data = np.zeros([self.trainT, self.nbatches, 2], dtype=np.float32)
            for batch in range(self.nbatches):
                for t in range(self.trainT):
                    i = batch*self.trainT + t
                    if i > bits.length():
                        break
                    data[t, batch, bits[i]] = 1
            workspace.FeedBlob('data', data)
            target = np.array(bits[1:], dtype=np.int32)
            workspace.FeedBlob('target', target)
        state = np.zeros([1, self.nbatches, self.nfeatures], dtype=np.float32)
        for timestep in range(self.trainT):
            ns = 'timestep_{}/'.format(timestep)
            if not self.started:
                seq_lengths = np.array([timestep+1]*self.nbatches, dtype=np.int32)
                workspace.FeedBlob(ns+'seq_lengths', seq_lengths)
                
            workspace.FeedBlob(ns+'hidden_init', state)
            workspace.FeedBlob(ns+'cell_init', state)
        if not self.started:
            workspace.RunNetOnce(self.init_net)
            workspace.CreateNet(self.train_net)
        workspace.RunNet(self.train_net)
        for name in workspace.Blobs():
            print('{}: {}'.format(name, workspace.FetchBlob(name).shape))
        assert(False)
        self.accuracy = float(workspace.FetchBlob('accuracy'))
        self.loss = float(workspace.FetchBlob('loss'))
        self.started = True
    
    
    
if __name__ == '__main__':
    import sys
    BinRNN().run(sys.argv)