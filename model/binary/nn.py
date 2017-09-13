def build():
    from caffe2.python import core, workspace, model_helper, brew
    from caffe2.python.optimizer import build_sgd
    import numpy as np
    helper = model_helper.ModelHelper('train')
    brew.fc(helper, 'data', 'train-fc', 2, 2)
    brew.softmax(helper, 'train-fc', 'train-softmax')
    helper.net.Accuracy(['train-softmax', 'target'], 'accuracy')
    helper.LabelCrossEntropy(['train-softmax', 'target'], 'xent')
    helper.net.AveragedLoss('xent', 'loss')
    helper.AddGradientOperators(['loss'])
    build_sgd(
        helper,
        base_learning_rate=8.0,
        policy="step",
        stepsize=1,
        gamma=0.9999
    )
    init_net = helper.param_init_net
    train_net = helper.net
    pred_net = core.Net('pred')
    workspace.RunNetOnce(init_net)
    for blob in workspace.Blobs():
        if blob not in ['iteration_mutex']:
            init_net.Const(workspace.FetchBlob(blob), blob)
    init_net.Const(np.zeros([1, 2], dtype=np.float32), 'zero')
    pred_net.FC(['zero', 'train-fc_w', 'train-fc_b'], 'pred-fc')
    pred_net.Div(['pred-fc', 'accuracy'], 'pred-to-softmax', broadcast=True)
    pred_net.Softmax('pred-to-softmax', 'softmax')
    return {'init_net':init_net, 'train_net':train_net, 'pred_net':pred_net}

def save(path, proto_rpath, nets):
    import os
    savepath = os.path.join(path, proto_rpath)
    print('nn -> {}'.format([name+".proto" for name in nets.keys()]))
    if not os.path.exists(savepath):
            os.makedirs(savepath)
    for name, net in nets.items():
        protofile = os.path.join(savepath, name+".proto")
        with open(protofile, 'wb') as f:
            print('saving {}'.format(protofile))
            f.write(net.Proto().SerializeToString())
        
    
def main():
    import sys, os
    nets = build()
    save(sys.argv[1], 'proto/nn', nets)
    
if __name__ == '__main__':
    main()