from model import Model
from caffe2.python import core, workspace, model_helper, brew
from caffe2.python.optimizer import build_sgd
import numpy as np
import time

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
        helper.param_init_net.Const(np.zeros([1, self.nfeatures+1], dtype=np.float16), 'data')
        helper.param_init_net.Const(
            np.random.normal(scale=0.1, size=[self.nfeatures+1, self.nfeatures+1]).astype(np.float16),
            'wts'
        )
        helper.net.MatMul(['wts', 'data'], 'mul', trans_b=True)
        brew.tanh(helper, 'mul', 'tanh')
        self.pred_init_net = helper.param_init_net
        self.pred_net = helper.net
        
    def predict(self, bit):
        if not self.started:
            workspace.RunNetOnce(self.pred_init_net)
            workspace.CreateNet(self.pred_net)
            self.started = True
        data = np.zeros([1, 1, self.nfeatures], dtype=np.float32)
        data[bit] = 1
        workspace.FeedBlob('data', data)
        workspace.RunNet(self.pred_net)
    
    def bench(self, runs):
        workspace.RunNetOnce(self.pred_init_net)
        workspace.CreateNet(self.pred_net)
        workspace.RunNet(self.pred_net, runs)
    
    
if __name__ == '__main__':
    import sys
    BinRNN().run(sys.argv)