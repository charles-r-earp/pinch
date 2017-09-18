#include "bin_rnn.netdef"
#include <caffe2/core/workspace.h>
#include <google/protobuf/message.h>

namespace pinch {
  namespace model {
    class bin_rnn {
      private:
        using Tensor = caffe2::Tensor<caffe2::CPUContext>;
        //caffe2::CPUContext ctx;
        caffe2::Workspace pred_ws;
        //static const int ntrain_batches=1;
        //static const int trainT=bin_rnn_netdef::trainT;
        //caffe2::NetDef pred_init_net, pred_net;
        caffe2::NetBase *pred_init_net = 0, *pred_net = 0;
        float *pred_data = 0, *pred_softmax = 0;
        //std::vector<int> bits;
        //bool pred_loaded;
      public:
        bin_rnn() {
          caffe2::NetDef net;
          net.ParseFromString(bin_rnn_netdef::pred_init_net);
          pred_init_net = pred_ws.CreateNet(net);
        }
        float operator()(int bit) {
          if(bit == -1) {
            pred_init_net->Run();
            if(!pred_net) {
              caffe2::NetDef net;
              net.ParseFromString(bin_rnn_netdef::pred_net);
              pred_net = pred_ws.CreateNet(net);
              pred_data = pred_ws.GetBlob("data")->GetMutable<Tensor>()->mutable_data<float>();
              assert(pred_data);
            }
            return 0.5;
          }
          else {
            pred_data[!bit] = 0; pred_data[bit] = 1;
            pred_net->Run();
            if(!pred_softmax)
              pred_softmax = pred_ws.GetBlob("softmax")->GetMutable<Tensor>()->mutable_data<float>();
            return pred_softmax[1];
          }
        }
    };
  };
};